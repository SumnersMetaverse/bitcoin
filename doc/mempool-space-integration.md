# Bitcoin Core and mempool.space Integration Guide

## Overview

This document provides a comprehensive cross-reference between Bitcoin Core and the mempool.space project, explaining how they integrate and what developers need to know when working with both repositories.

## What is mempool.space?

mempool.space (https://github.com/mempool/mempool) is an open-source Bitcoin blockchain explorer and mempool visualizer. It provides:

- Real-time mempool visualization
- Transaction tracking and analysis
- Block explorer functionality
- Fee estimation tools
- Network statistics and monitoring

## How mempool.space Integrates with Bitcoin Core

mempool.space acts as a frontend/middleware layer that connects to Bitcoin Core to:

1. **Fetch mempool data** via RPC and REST APIs
2. **Query blockchain information** for block and transaction details
3. **Monitor network activity** through transaction propagation
4. **Provide fee estimates** based on mempool state

## Bitcoin Core APIs Used by mempool.space

### JSON-RPC API Endpoints

mempool.space primarily uses the following RPC methods:

#### Mempool-Related RPCs
- `getrawmempool` - Returns all transaction IDs in the mempool
- `getmempoolentry` - Returns mempool data for a specific transaction
- `getmempoolinfo` - Returns mempool statistics
- `getmempoolancestors` - Returns ancestor transactions
- `getmempooldescendants` - Returns descendant transactions

#### Block and Transaction RPCs
- `getblock` - Fetches block data
- `getblockheader` - Fetches block header information
- `getblockcount` - Returns the current block height
- `getblockhash` - Returns block hash for a given height
- `getrawtransaction` - Fetches transaction data
- `gettxout` - Returns details about an unspent transaction output

#### Network and Chain Info RPCs
- `getblockchaininfo` - Returns blockchain state information
- `getnetworkinfo` - Returns network information
- `estimatesmartfee` - Estimates transaction fees

### REST API Endpoints

mempool.space also utilizes Bitcoin Core's REST interface:

- `GET /rest/mempool/info.json` - Mempool information
- `GET /rest/mempool/contents.json` - Full mempool contents
- `GET /rest/tx/<TX-HASH>.json` - Transaction details
- `GET /rest/block/<BLOCK-HASH>.json` - Block details
- `GET /rest/chaininfo.json` - Blockchain information

## Configuration Requirements

### Bitcoin Core Configuration for mempool.space

To enable mempool.space integration, configure Bitcoin Core with:

```conf
# Enable RPC server
server=1

# Enable transaction index (recommended for full functionality)
txindex=1

# Enable REST API
rest=1

# Set RPC credentials
rpcuser=your_username
rpcpassword=your_secure_password

# Allow RPC connections (adjust for your network)
rpcallowip=127.0.0.1
rpcbind=127.0.0.1

# Set RPC port (default: 8332 for mainnet)
rpcport=8332

# Enable ZMQ for real-time updates (optional but recommended)
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
zmqpubhashblock=tcp://127.0.0.1:28334
```

### mempool.space Backend Configuration

mempool.space backend needs to be configured to connect to Bitcoin Core:

```json
{
  "CORE_RPC": {
    "HOST": "127.0.0.1",
    "PORT": 8332,
    "USERNAME": "your_username",
    "PASSWORD": "your_secure_password"
  },
  "MEMPOOL": {
    "NETWORK": "mainnet",
    "BACKEND": "electrum",
    "ENABLED": true,
    "USE_SECOND_NODE_FOR_MINFEE": false
  }
}
```

## Key Integration Points

### 1. Mempool Monitoring

**Bitcoin Core Side:**
- Maintains the mempool (`src/txmempool.cpp`, `src/txmempool.h`)
- Validates transactions before adding to mempool (`src/validation.cpp`)
- Tracks transaction dependencies and fee rates
- Implements eviction policies

**mempool.space Side:**
- Polls Bitcoin Core mempool via `getrawmempool` RPC
- Caches and visualizes mempool state
- Calculates fee rate distributions
- Tracks transaction propagation times

### 2. Block Processing

**Bitcoin Core Side:**
- Validates and stores blocks
- Updates UTXO set
- Removes confirmed transactions from mempool

**mempool.space Side:**
- Monitors new blocks via ZMQ or polling
- Updates transaction status
- Calculates block statistics
- Tracks mining pool identification

### 3. Transaction Tracking

**Bitcoin Core Side:**
- Indexes transactions (if `txindex=1`)
- Provides transaction lookup via RPC/REST
- Maintains UTXO database

**mempool.space Side:**
- Provides user-friendly transaction visualization
- Shows transaction confirmation status
- Displays transaction graph and relationships
- Offers fee analysis

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    mempool.space Stack                       │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Angular)                                          │
│    ↓                                                         │
│  Backend API (Node.js/TypeScript)                           │
│    ↓                                                         │
│  Bitcoin Core RPC Client                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ↓ (JSON-RPC / REST)
┌─────────────────────────────────────────────────────────────┐
│                     Bitcoin Core                             │
├─────────────────────────────────────────────────────────────┤
│  RPC Server (src/rpc/)                                      │
│  REST Interface (src/rest.cpp)                              │
│  Mempool (src/txmempool.cpp)                                │
│  Validation (src/validation.cpp)                            │
│  Block Storage (src/node/blockstorage.cpp)                 │
└─────────────────────────────────────────────────────────────┘
```

## Development Considerations

### When Modifying Bitcoin Core Mempool

If you're modifying Bitcoin Core's mempool implementation, consider:

1. **RPC API Compatibility**: Changes to mempool structure may affect RPC responses
2. **Performance Impact**: mempool.space makes frequent RPC calls
3. **Data Consistency**: Ensure atomicity of mempool state updates
4. **Fee Estimation**: Changes may affect fee estimation accuracy

### When Developing mempool.space Features

If you're adding features to mempool.space that rely on Bitcoin Core:

1. **Version Compatibility**: Check Bitcoin Core version for API availability
2. **Rate Limiting**: Implement proper RPC call rate limiting
3. **Error Handling**: Handle RPC errors and node disconnections gracefully
4. **Data Validation**: Validate all data received from Bitcoin Core

## Testing Integration

### Local Development Setup

1. **Start Bitcoin Core in regtest mode:**
   ```bash
   bitcoind -regtest -server=1 -rest=1 -rpcuser=test -rpcpassword=test -txindex=1
   ```

2. **Generate test blocks:**
   ```bash
   bitcoin-cli -regtest -rpcuser=test -rpcpassword=test generatetoaddress 101 <address>
   ```

3. **Configure mempool.space backend** to connect to regtest node

4. **Test RPC connectivity:**
   ```bash
   curl --user test:test --data-binary '{"jsonrpc":"2.0","id":"test","method":"getmempoolinfo","params":[]}' -H 'content-type: application/json' http://127.0.0.1:18443/
   ```

### Integration Test Scenarios

- Verify mempool synchronization
- Test transaction submission and tracking
- Validate block processing and confirmation updates
- Check fee estimation accuracy
- Test error handling and recovery

## Performance Optimization

### Bitcoin Core Side

- Enable `txindex` for faster transaction lookups
- Increase `maxmempool` if needed for high-traffic scenarios
- Configure `dbcache` appropriately for your system
- Use ZMQ notifications instead of polling when possible

### mempool.space Side

- Implement caching layers to reduce RPC calls
- Use WebSocket connections for real-time updates
- Batch RPC requests where possible
- Implement connection pooling for RPC clients

## Security Considerations

1. **RPC Authentication**: Always use strong credentials
2. **Network Isolation**: Limit RPC access to trusted networks
3. **API Rate Limiting**: Implement rate limits to prevent abuse
4. **Input Validation**: Validate all data from external sources
5. **Privacy**: Be aware that querying patterns may leak information

## Monitoring and Debugging

### Bitcoin Core Logs

Monitor these log categories for mempool-related issues:
```
-debug=mempool
-debug=rpc
-debug=http
```

### mempool.space Debug

- Check backend logs for RPC connection issues
- Monitor RPC response times
- Track mempool synchronization lag
- Verify ZMQ message processing

## Key Files Reference

### Bitcoin Core Files

#### Mempool Core
- `src/txmempool.h` - Mempool class definition
- `src/txmempool.cpp` - Mempool implementation
- `src/kernel/mempool_entry.h` - Mempool entry structure
- `src/kernel/mempool_options.h` - Mempool configuration options

#### RPC Interface
- `src/rpc/mempool.h` - Mempool RPC declarations
- `src/rpc/mempool.cpp` - Mempool RPC implementations
- `src/rpc/blockchain.cpp` - Block and chain RPC methods
- `src/rpc/rawtransaction.cpp` - Transaction RPC methods

#### REST Interface
- `src/rest.cpp` - REST API implementation
- `doc/REST-interface.md` - REST API documentation

#### Network Layer
- `src/net_processing.cpp` - P2P message processing
- `src/validation.cpp` - Block and transaction validation

### mempool.space Repository Structure

- `backend/src/` - Backend API implementation
- `frontend/src/` - Angular frontend application
- `docker/` - Docker configuration files
- `production/` - Production deployment configs

## Cross-Repository Development Workflow

### Scenario: Testing a New Bitcoin Core Feature

1. **Develop and test in Bitcoin Core**
2. **Update RPC documentation** if API changes
3. **Test RPC compatibility** with existing clients
4. **Update mempool.space** if using new features
5. **Test integration** in regtest/testnet environment
6. **Document breaking changes** in release notes

### Scenario: Adding mempool.space Feature

1. **Identify required Bitcoin Core data**
2. **Check if existing RPC methods provide data**
3. **Request new RPC method** if needed (via Bitcoin Core PR)
4. **Implement using available APIs** in the interim
5. **Add caching/optimization** layers
6. **Document integration requirements**

## Common Issues and Solutions

### Issue: mempool.space shows outdated data

**Cause**: RPC polling interval too long or cache not invalidating

**Solution**: 
- Reduce polling interval in mempool.space config
- Implement ZMQ notifications for real-time updates
- Check Bitcoin Core is processing blocks normally

### Issue: High RPC load from mempool.space

**Cause**: Inefficient API usage or missing caching

**Solution**:
- Implement response caching in mempool.space backend
- Use batch RPC requests
- Optimize polling frequencies
- Consider using ZMQ instead of polling

### Issue: Transaction index not found

**Cause**: `txindex=1` not enabled in Bitcoin Core

**Solution**:
- Add `txindex=1` to bitcoin.conf
- Restart Bitcoin Core with `-reindex` once
- Wait for reindexing to complete

## Future Considerations

### Planned Bitcoin Core Improvements

- Enhanced mempool clustering and linearization
- Improved fee estimation algorithms
- Package relay and package RBF support
- Additional RPC methods for mempool analysis

### Potential Integration Enhancements

- More efficient data synchronization protocols
- Standardized APIs for blockchain explorers
- Better support for layer 2 protocols
- Enhanced privacy-preserving query methods

## Resources and References

### Bitcoin Core Documentation
- RPC Documentation: `doc/JSON-RPC-interface.md`
- REST Documentation: `doc/REST-interface.md`
- Mempool Policy: `doc/policy/mempool-design.md`
- Build Instructions: `doc/build-*.md`

### mempool.space Documentation
- GitHub Repository: https://github.com/mempool/mempool
- API Documentation: https://mempool.space/docs/api
- Self-Hosting Guide: https://github.com/mempool/mempool/tree/master/docker

### External Resources
- Bitcoin Core Developer Documentation: https://bitcoincore.reviews/
- Bitcoin Improvement Proposals (BIPs): https://github.com/bitcoin/bips
- Bitcoin Stack Exchange: https://bitcoin.stackexchange.com/

## Conclusion

Bitcoin Core and mempool.space work together to provide comprehensive Bitcoin blockchain and mempool analysis. Bitcoin Core handles the core validation, storage, and network functionality, while mempool.space provides user-friendly visualization and analysis tools.

Understanding the integration points, APIs, and data flow between these projects is essential for:
- Developing new features in either project
- Debugging integration issues
- Optimizing performance
- Ensuring compatibility across versions
- Self-hosting mempool.space instances

When making changes to either repository, always consider the impact on the other and test integration thoroughly.
