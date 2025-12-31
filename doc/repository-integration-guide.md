# SumnersMetaverse Repository Integration Guide

This document explains how to connect your various SumnersMetaverse repositories to your Bitcoin Core node and how to execute the code to run everything together.

## Overview of Your Repositories

Based on your GitHub account, here are the Bitcoin/blockchain-related repositories that need to be connected to your Bitcoin Core node:

### 1. **bitcoin** (This Repository)
- **Purpose**: Bitcoin Core node - the foundation for everything else
- **Status**: ✅ Configured with mempool.space integration documentation

### 2. **lndhub** 
- **Purpose**: Lightning Network Hub - Wrapper for LND (Lightning Network Daemon) providing separate accounts for users
- **Needs**: Bitcoin Core + LND (Lightning Network Daemon)
- **Status**: ⚠️ Requires Bitcoin Core to be running with Lightning Network

### 3. **3xplCore**
- **Purpose**: Universal blockchain explorer core modules (like mempool.space but supports multiple chains)
- **Needs**: Bitcoin Core node for Bitcoin blockchain data
- **Status**: ⚠️ Requires Bitcoin Core with RPC access

### 4. **mining-pools**
- **Purpose**: Bitcoin mining pool identification and Coinbase tag data
- **Needs**: Read-only connection to Bitcoin Core for block data analysis
- **Status**: ⚠️ Requires Bitcoin Core with RPC access

### 5. **Other Repositories** (Not directly connected to Bitcoin Core)
- `metamask-docs`, `provider-engine`, `aave-v4-sdk`, `dapp-near-ref-ui`, `filda` - These are for Ethereum/other chains

---

## Complete Setup and Execution Guide

### Phase 1: Bitcoin Core Foundation (COMPLETED)

Your Bitcoin Core node is the foundation that everything else connects to.

**Status**: ✅ Already configured with mempool.space documentation

**Verify your Bitcoin Core is running:**
```bash
# Check if Bitcoin Core is running
bitcoin-cli getblockchaininfo

# Or use the test script we created
python3 contrib/mempool-space/test-integration.py --user your_rpc_user --password your_rpc_password
```

---

## Phase 2: Connect 3xplCore (Blockchain Explorer)

3xplCore is a blockchain explorer engine that needs to connect to your Bitcoin Core node.

### Step 1: Clone and Setup 3xplCore

```bash
# Clone your 3xplCore repository
cd ~/projects  # or wherever you keep your projects
git clone https://github.com/SumnersMetaverse/3xplCore.git
cd 3xplCore
```

### Step 2: Configure 3xplCore to Connect to Bitcoin Core

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file
nano .env
```

Add your Bitcoin Core node credentials:

```bash
# In .env file, find the bitcoin-main module section and configure:

# Bitcoin Core RPC connection
MODULE_bitcoin-main_NODES[]=http://your_rpc_user:your_rpc_password@127.0.0.1:8332/

# Example with the default setup:
MODULE_bitcoin-main_NODES[]=http://mempool:your_secure_password@127.0.0.1:8332/
```

### Step 3: Run 3xplCore

```bash
# Process Bitcoin blocks starting from genesis (block 0)
php 3xpl.php bitcoin-main B 0 T

# Or track the newest blocks in real-time (Monitor mode)
php 3xpl.php bitcoin-main M

# Create data dumps in TSV format
# This will create dumps in the Dumps/ folder
php 3xpl.php bitcoin-main B 0 T
```

**What each mode does:**
- `M` = Monitor mode (tracks new blocks continuously)
- `B <number>` = Process a specific block number
- `T` = Create TSV dumps of the data

---

## Phase 3: Connect LndHub (Lightning Network)

LndHub provides Lightning Network functionality and needs both Bitcoin Core AND Lightning Network Daemon (LND).

### Step 1: Install Lightning Network Daemon (LND)

```bash
# Install LND (Lightning Network Daemon)
# Visit: https://github.com/lightningnetwork/lnd/releases

# For Ubuntu/Debian:
wget https://github.com/lightningnetwork/lnd/releases/download/v0.17.3-beta/lnd-linux-amd64-v0.17.3-beta.tar.gz
tar -xzf lnd-linux-amd64-v0.17.3-beta.tar.gz
sudo install -m 0755 -o root -g root -t /usr/local/bin lnd-linux-amd64-v0.17.3-beta/*
```

### Step 2: Configure LND to Connect to Bitcoin Core

Create LND configuration file:

```bash
mkdir -p ~/.lnd
nano ~/.lnd/lnd.conf
```

Add this configuration:

```conf
[Application Options]
debuglevel=info
maxpendingchannels=10
alias=YourNodeName
color=#3399FF

[Bitcoin]
bitcoin.active=1
bitcoin.mainnet=1
bitcoin.node=bitcoind

[Bitcoind]
bitcoind.rpchost=127.0.0.1:8332
bitcoind.rpcuser=your_rpc_user
bitcoind.rpcpass=your_rpc_password
bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333
```

### Step 3: Start LND

```bash
# Start LND
lnd

# In another terminal, create a wallet
lncli create

# Unlock the wallet (needed after every restart)
lncli unlock
```

### Step 4: Setup LndHub

```bash
# Clone your lndhub repository
cd ~/projects
git clone https://github.com/SumnersMetaverse/lndhub.git
cd lndhub

# Install dependencies
npm install
```

### Step 5: Configure LndHub

```bash
# Edit config.js
nano config.js
```

Update the configuration:

```javascript
module.exports = {
  bitcoind: {
    rpc: 'http://your_rpc_user:your_rpc_password@127.0.0.1:8332',
  },
  redis: {
    port: 6379,
    host: '127.0.0.1',
    family: 4,
    password: '', // Add if you secured Redis
    db: 0,
  },
  lnd: {
    url: '127.0.0.1:10009',
    password: '', // Your LND wallet password
  },
};
```

### Step 6: Copy LND Credentials to LndHub

```bash
# Copy admin.macaroon and tls.cert from LND to LndHub directory
cp ~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon ~/projects/lndhub/
cp ~/.lnd/tls.cert ~/projects/lndhub/
```

### Step 7: Install and Start Redis

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should return PONG
```

### Step 8: Run LndHub

```bash
cd ~/projects/lndhub
npm start
```

LndHub will now be running on http://localhost:3000

---

## Phase 4: Connect mining-pools (Mining Pool Identification)

This repository is primarily a data repository for mining pool identification.

### Step 1: Clone and Use mining-pools

```bash
cd ~/projects
git clone https://github.com/SumnersMetaverse/mining-pools.git
cd mining-pools
```

### Step 2: Use the Mining Pool Data

The `pools.json` and `pools-v2.json` files contain mining pool identification data. You can:

**A. Query Bitcoin Core for block data and match against pool data:**

```python
#!/usr/bin/env python3
import json
import requests

# Load pool data
with open('pools.json', 'r') as f:
    pools = json.load(f)

# Bitcoin Core RPC connection
rpc_url = 'http://127.0.0.1:8332'
rpc_user = 'your_rpc_user'
rpc_password = 'your_rpc_password'

def get_block_info(block_height):
    # Get block hash
    response = requests.post(
        rpc_url,
        auth=(rpc_user, rpc_password),
        json={
            'jsonrpc': '2.0',
            'id': 'blockinfo',
            'method': 'getblockhash',
            'params': [block_height]
        }
    )
    block_hash = response.json()['result']
    
    # Get block details
    response = requests.post(
        rpc_url,
        auth=(rpc_user, rpc_password),
        json={
            'jsonrpc': '2.0',
            'id': 'blockdetails',
            'method': 'getblock',
            'params': [block_hash, 2]  # 2 = verbose with tx info
        }
    )
    return response.json()['result']

# Example: Get info about a recent block
block_info = get_block_info(850000)
coinbase_tx = block_info['tx'][0]  # First tx is always coinbase
print(f"Block mined by: {coinbase_tx}")

# Match against pool data to identify miner
# (You'll need to implement matching logic based on coinbase data)
```

**B. Integrate with 3xplCore:**

The mining pool data can be used by 3xplCore to identify which pool mined each block.

---

## Complete System Architecture

Here's how everything connects:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Bitcoin Core                             │
│                     (Your bitcoin repo)                          │
│  - Full blockchain node                                          │
│  - RPC API (port 8332)                                           │
│  - REST API                                                       │
│  - ZMQ notifications (ports 28332-28336)                         │
└────────────┬────────────────────────────┬───────────────────────┘
             │                            │
             │                            │
    ┌────────▼────────┐          ┌───────▼──────────┐
    │   3xplCore      │          │  Lightning (LND) │
    │   Explorer      │          │                  │
    │                 │          │  - Port 10009    │
    │ Queries Bitcoin │          │  - Manages L2    │
    │ blockchain data │          └────────┬─────────┘
    │ via RPC         │                   │
    └─────────────────┘          ┌────────▼─────────┐
                                 │     LndHub       │
                                 │                  │
                                 │ - Port 3000      │
    ┌─────────────────┐          │ - User accounts  │
    │  mining-pools   │          │ - Lightning API  │
    │                 │          └──────────────────┘
    │ Pool ID data    │
    │ (read-only)     │          ┌──────────────────┐
    └─────────────────┘          │     Redis        │
                                 │                  │
                                 │ - Port 6379      │
                                 │ - LndHub cache   │
                                 └──────────────────┘
```

---

## Quick Start Script

Save this as `start-all-services.sh`:

```bash
#!/bin/bash

echo "Starting Bitcoin Core stack..."

# Start Bitcoin Core (if not already running)
if ! pgrep -x "bitcoind" > /dev/null; then
    echo "Starting Bitcoin Core..."
    bitcoind -daemon
    sleep 10
fi

# Start Redis (if not already running)
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis..."
    sudo systemctl start redis-server
fi

# Start LND (if you have it configured)
if command -v lnd &> /dev/null; then
    if ! pgrep -x "lnd" > /dev/null; then
        echo "Starting LND..."
        lnd &
        sleep 5
        # Unlock wallet (you'll need to enter password)
        lncli unlock
    fi
fi

# Start LndHub (if you have it configured)
if [ -d ~/projects/lndhub ]; then
    echo "Starting LndHub..."
    cd ~/projects/lndhub
    npm start &
    cd -
fi

# Start 3xplCore in monitor mode (if you have it configured)
if [ -d ~/projects/3xplCore ]; then
    echo "Starting 3xplCore monitor..."
    cd ~/projects/3xplCore
    php 3xpl.php bitcoin-main M &
    cd -
fi

echo "All services started!"
echo ""
echo "Bitcoin Core RPC: http://127.0.0.1:8332"
echo "LND gRPC: 127.0.0.1:10009"
echo "LndHub API: http://127.0.0.1:3000"
echo ""
echo "To check status:"
echo "  bitcoin-cli getblockchaininfo"
echo "  lncli getinfo"
echo "  curl http://127.0.0.1:3000/status"
```

Make it executable:
```bash
chmod +x start-all-services.sh
./start-all-services.sh
```

---

## Testing the Full Stack

### Test 1: Bitcoin Core
```bash
bitcoin-cli getblockchaininfo
```

### Test 2: Bitcoin Core RPC Access
```bash
python3 /home/runner/work/bitcoin/bitcoin/contrib/mempool-space/test-integration.py \
  --user your_rpc_user --password your_rpc_password
```

### Test 3: LND (if running)
```bash
lncli getinfo
```

### Test 4: LndHub (if running)
```bash
curl http://127.0.0.1:3000/status
```

### Test 5: 3xplCore (if running)
```bash
cd ~/projects/3xplCore
php 3xpl.php bitcoin-main B 850000  # Get block 850000
```

---

## Configuration Summary

### Bitcoin Core (`~/.bitcoin/bitcoin.conf`)
```conf
server=1
rest=1
txindex=1
rpcuser=your_username
rpcpassword=your_secure_password
rpcbind=127.0.0.1
rpcallowip=127.0.0.1

# For Lightning Network
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
zmqpubhashblock=tcp://127.0.0.1:28334
```

### LND (`~/.lnd/lnd.conf`)
```conf
[Bitcoin]
bitcoin.active=1
bitcoin.mainnet=1
bitcoin.node=bitcoind

[Bitcoind]
bitcoind.rpchost=127.0.0.1:8332
bitcoind.rpcuser=your_rpc_user
bitcoind.rpcpass=your_rpc_password
bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333
```

### 3xplCore (`.env`)
```bash
MODULE_bitcoin-main_NODES[]=http://your_rpc_user:your_rpc_password@127.0.0.1:8332/
```

### LndHub (`config.js`)
```javascript
{
  bitcoind: {
    rpc: 'http://your_rpc_user:your_rpc_password@127.0.0.1:8332',
  },
  redis: { host: '127.0.0.1', port: 6379 },
  lnd: { url: '127.0.0.1:10009' }
}
```

---

## Troubleshooting

### Bitcoin Core Issues
```bash
# Check if Bitcoin Core is running
ps aux | grep bitcoind

# Check RPC access
bitcoin-cli getblockchaininfo

# View logs
tail -f ~/.bitcoin/debug.log
```

### LND Issues
```bash
# Check if LND is running
ps aux | grep lnd

# Check LND status
lncli getinfo

# View logs
tail -f ~/.lnd/logs/bitcoin/mainnet/lnd.log
```

### LndHub Issues
```bash
# Check if LndHub is running
ps aux | grep node

# Check Redis connection
redis-cli ping

# Test LndHub endpoint
curl http://127.0.0.1:3000/status
```

### 3xplCore Issues
```bash
# Test Bitcoin Core connection
curl --user your_rpc_user:your_rpc_password \
  --data-binary '{"jsonrpc":"2.0","id":"test","method":"getblockcount","params":[]}' \
  http://127.0.0.1:8332/

# Check PHP version
php --version  # Should be PHP 7.4 or higher
```

---

## Next Steps

1. **Start with Bitcoin Core** - Make sure it's fully synced
2. **Add 3xplCore** - Set up blockchain explorer functionality
3. **Add LND** - If you want Lightning Network features
4. **Add LndHub** - If you want to provide Lightning accounts
5. **Use mining-pools** - Integrate pool identification data

Each component builds on top of Bitcoin Core, so start there and add components as needed.

## Support Resources

- Bitcoin Core: https://bitcoin.org/en/bitcoin-core/
- LND: https://github.com/lightningnetwork/lnd
- 3xplCore: https://github.com/SumnersMetaverse/3xplCore
- LndHub: https://github.com/SumnersMetaverse/lndhub
- This repo's documentation: See `doc/mempool-space-integration.md`
