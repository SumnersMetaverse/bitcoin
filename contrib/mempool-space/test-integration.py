#!/usr/bin/env python3
"""
Bitcoin Core and mempool.space Integration Test Script

This script helps verify that your Bitcoin Core node is properly configured
for mempool.space integration by testing RPC and REST endpoints.

Usage:
    python3 test-integration.py --user <rpc_user> --password <rpc_password>
    python3 test-integration.py --help
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import base64
from typing import Dict, Any, Tuple, Optional


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text: str) -> None:
    """Print info message"""
    print(f"  {text}")


def make_rpc_request(
    host: str,
    port: int,
    user: str,
    password: str,
    method: str,
    params: list = None
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Make a JSON-RPC request to Bitcoin Core"""
    if params is None:
        params = []

    url = f"http://{host}:{port}/"
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Add basic authentication
    credentials = f"{user}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers['Authorization'] = f'Basic {encoded_credentials}'
    
    data = json.dumps({
        "jsonrpc": "2.0",
        "id": "test",
        "method": method,
        "params": params
    }).encode()
    
    try:
        request = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode())
            if 'error' in result and result['error'] is not None:
                return False, result['error']
            return True, result.get('result')
    except urllib.error.HTTPError as e:
        return False, {"code": e.code, "message": str(e)}
    except Exception as e:
        return False, {"code": -1, "message": str(e)}


def make_rest_request(
    host: str,
    port: int,
    endpoint: str
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Make a REST request to Bitcoin Core"""
    url = f"http://{host}:{port}/rest/{endpoint}"
    
    try:
        request = urllib.request.Request(url)
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode())
            return True, result
    except urllib.error.HTTPError as e:
        return False, {"code": e.code, "message": str(e)}
    except Exception as e:
        return False, {"code": -1, "message": str(e)}


def test_rpc_connection(host: str, port: int, user: str, password: str) -> bool:
    """Test basic RPC connectivity"""
    print_header("Testing RPC Connection")
    
    success, result = make_rpc_request(host, port, user, password, "getblockchaininfo")
    
    if success:
        print_success("RPC connection successful")
        print_info(f"Network: {result.get('chain', 'unknown')}")
        print_info(f"Blocks: {result.get('blocks', 0)}")
        print_info(f"Headers: {result.get('headers', 0)}")
        return True
    else:
        print_error(f"RPC connection failed: {result.get('message', 'Unknown error')}")
        return False


def test_rest_endpoint(host: str, port: int) -> bool:
    """Test REST API endpoint"""
    print_header("Testing REST API")
    
    success, result = make_rest_request(host, port, "chaininfo.json")
    
    if success:
        print_success("REST API is accessible")
        print_info(f"Chain: {result.get('chain', 'unknown')}")
        return True
    else:
        print_error(f"REST API failed: {result.get('message', 'Unknown error')}")
        print_warning("Enable REST with 'rest=1' in bitcoin.conf")
        return False


def test_mempool_info(host: str, port: int, user: str, password: str) -> bool:
    """Test mempool info RPC"""
    print_header("Testing Mempool RPC Methods")
    
    success, result = make_rpc_request(host, port, user, password, "getmempoolinfo")
    
    if success:
        print_success("getmempoolinfo works")
        print_info(f"Transactions in mempool: {result.get('size', 0)}")
        print_info(f"Mempool size (bytes): {result.get('bytes', 0):,}")
        print_info(f"Mempool usage (bytes): {result.get('usage', 0):,}")
        print_info(f"Max mempool (bytes): {result.get('maxmempool', 0):,}")
        return True
    else:
        print_error(f"getmempoolinfo failed: {result.get('message', 'Unknown error')}")
        return False


def test_mempool_rest(host: str, port: int) -> bool:
    """Test mempool REST endpoint"""
    success, result = make_rest_request(host, port, "mempool/info.json")
    
    if success:
        print_success("REST mempool/info endpoint works")
        return True
    else:
        print_error(f"REST mempool endpoint failed: {result.get('message', 'Unknown error')}")
        return False


def test_txindex(host: str, port: int, user: str, password: str) -> bool:
    """Test if transaction index is enabled"""
    print_header("Testing Transaction Index")
    
    success, result = make_rpc_request(host, port, user, password, "getindexinfo")
    
    if success:
        if 'txindex' in result:
            if result['txindex'].get('synced'):
                print_success("Transaction index is enabled and synced")
                print_info(f"Best block height: {result['txindex'].get('best_block_height', 'N/A')}")
                return True
            else:
                print_warning("Transaction index is enabled but still syncing")
                print_info(f"Progress: {result['txindex'].get('best_block_height', 0)} blocks indexed")
                return False
        else:
            print_error("Transaction index is not enabled")
            print_warning("Enable with 'txindex=1' in bitcoin.conf and restart with -reindex")
            return False
    else:
        print_error(f"Could not check transaction index: {result.get('message', 'Unknown error')}")
        return False


def test_zmq_availability(host: str, port: int, user: str, password: str) -> bool:
    """Check if ZMQ is configured"""
    print_header("Checking ZMQ Configuration")
    
    success, result = make_rpc_request(host, port, user, password, "getzmqnotifications")
    
    if success:
        if result:
            print_success("ZMQ notifications are configured")
            for notification in result:
                print_info(f"  - {notification.get('type')}: {notification.get('address')}")
            return True
        else:
            print_warning("ZMQ is available but no notifications are configured")
            print_info("For real-time updates, add ZMQ settings to bitcoin.conf:")
            print_info("  zmqpubrawblock=tcp://127.0.0.1:28332")
            print_info("  zmqpubrawtx=tcp://127.0.0.1:28333")
            print_info("  zmqpubhashblock=tcp://127.0.0.1:28334")
            return False
    else:
        print_warning("Could not check ZMQ configuration")
        print_info("ZMQ support may not be compiled in this Bitcoin Core build")
        return False


def test_network_info(host: str, port: int, user: str, password: str) -> bool:
    """Get network information"""
    print_header("Network Information")
    
    success, result = make_rpc_request(host, port, user, password, "getnetworkinfo")
    
    if success:
        print_success("Network info retrieved")
        print_info(f"Version: {result.get('version', 'unknown')}")
        print_info(f"Subversion: {result.get('subversion', 'unknown')}")
        print_info(f"Protocol version: {result.get('protocolversion', 'unknown')}")
        print_info(f"Connections: {result.get('connections', 0)}")
        return True
    else:
        print_error(f"Could not get network info: {result.get('message', 'Unknown error')}")
        return False


def generate_summary(results: Dict[str, bool]) -> None:
    """Generate and print test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"Total tests: {total}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"  {color}{status}{Colors.RESET} - {test_name}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All tests passed! Your Bitcoin Core node is ready for mempool.space.{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some tests failed. Review the output above for recommended fixes.{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(
        description="Test Bitcoin Core configuration for mempool.space integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --user mempool --password mypassword
  %(prog)s --host 192.168.1.100 --port 8332 --user mempool --password mypassword
  %(prog)s --help
        """
    )
    
    parser.add_argument('--host', default='127.0.0.1', help='Bitcoin Core RPC host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8332, help='Bitcoin Core RPC port (default: 8332)')
    parser.add_argument('--user', required=True, help='Bitcoin Core RPC username')
    parser.add_argument('--password', required=True, help='Bitcoin Core RPC password')
    
    args = parser.parse_args()
    
    print_header("Bitcoin Core & mempool.space Integration Test")
    print_info(f"Testing connection to {args.host}:{args.port}")
    print_info(f"RPC User: {args.user}")
    
    results = {}
    
    # Run tests
    results['RPC Connection'] = test_rpc_connection(args.host, args.port, args.user, args.password)
    if not results['RPC Connection']:
        print_error("\nCannot proceed without RPC connection. Please check:")
        print_info("  1. Bitcoin Core is running")
        print_info("  2. RPC credentials are correct")
        print_info("  3. server=1 is set in bitcoin.conf")
        print_info("  4. Host and port are correct")
        sys.exit(1)
    
    results['REST API'] = test_rest_endpoint(args.host, args.port)
    results['Mempool Info RPC'] = test_mempool_info(args.host, args.port, args.user, args.password)
    results['Mempool REST'] = test_mempool_rest(args.host, args.port)
    results['Transaction Index'] = test_txindex(args.host, args.port, args.user, args.password)
    results['ZMQ Configuration'] = test_zmq_availability(args.host, args.port, args.user, args.password)
    results['Network Info'] = test_network_info(args.host, args.port, args.user, args.password)
    
    # Generate summary
    generate_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == '__main__':
    main()
