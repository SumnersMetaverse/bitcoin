# Quick Reference: Connecting Your SumnersMetaverse Repositories

## Your Repository Ecosystem

| Repository | Purpose | Connects to Bitcoin Core? | Status |
|------------|---------|----------------------------|--------|
| **bitcoin** | Bitcoin Core node | N/A (this is the foundation) | ✅ Ready |
| **3xplCore** | Blockchain explorer engine | ✅ Yes - via RPC | ⚠️ Needs setup |
| **lndhub** | Lightning Network accounts | ✅ Yes - via LND + RPC | ⚠️ Needs LND + setup |
| **mining-pools** | Mining pool ID data | ✅ Yes - read-only | ⚠️ Can integrate |

## Execution Order

### 1️⃣ Bitcoin Core (Foundation) - ALREADY RUNNING
```bash
# Verify it's running
bitcoin-cli getblockchaininfo

# Test RPC access
python3 contrib/mempool-space/test-integration.py --user <your_user> --password <your_pass>
```

### 2️⃣ 3xplCore (Blockchain Explorer) - EASIEST TO ADD
```bash
# Clone
git clone https://github.com/SumnersMetaverse/3xplCore.git
cd 3xplCore

# Configure
cp .env.example .env
nano .env
# Add: MODULE_bitcoin-main_NODES[]=http://user:pass@127.0.0.1:8332/

# Run
php 3xpl.php bitcoin-main M   # Monitor mode (tracks new blocks)
```

### 3️⃣ LND + LndHub (Lightning Network) - MORE COMPLEX
```bash
# Install LND first
wget https://github.com/lightningnetwork/lnd/releases/download/v0.17.3-beta/lnd-linux-amd64-v0.17.3-beta.tar.gz
tar -xzf lnd-linux-amd64-v0.17.3-beta.tar.gz
sudo install -m 0755 -o root -g root -t /usr/local/bin lnd-linux-amd64-v0.17.3-beta/*

# Configure LND (create ~/.lnd/lnd.conf)
[Bitcoin]
bitcoin.active=1
bitcoin.mainnet=1
bitcoin.node=bitcoind

[Bitcoind]
bitcoind.rpchost=127.0.0.1:8332
bitcoind.rpcuser=<your_user>
bitcoind.rpcpass=<your_pass>
bitcoind.zmqpubrawblock=tcp://127.0.0.1:28332
bitcoind.zmqpubrawtx=tcp://127.0.0.1:28333

# Start LND
lnd

# Create wallet (in another terminal)
lncli create

# Clone and setup LndHub
git clone https://github.com/SumnersMetaverse/lndhub.git
cd lndhub
npm install

# Copy LND credentials
cp ~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon .
cp ~/.lnd/tls.cert .

# Configure config.js with Bitcoin Core RPC details
nano config.js

# Start Redis
sudo systemctl start redis-server

# Run LndHub
npm start
```

## One-Line RPC Configuration

All these services need your Bitcoin Core RPC credentials:

```
RPC URL: http://127.0.0.1:8332
Username: [from bitcoin.conf rpcuser=]
Password: [from bitcoin.conf rpcpassword=]
```

## What Each Service Does

### Bitcoin Core
- **What**: Full Bitcoin node, stores entire blockchain
- **How to run**: `bitcoind` (should already be running)
- **Port**: 8332 (RPC), 8333 (P2P)

### 3xplCore
- **What**: Processes blockchain data into explorer-friendly format
- **How to run**: `php 3xpl.php bitcoin-main M`
- **Uses**: Bitcoin Core RPC to read blocks and transactions

### LND (Lightning Network Daemon)
- **What**: Second-layer payment network on top of Bitcoin
- **How to run**: `lnd` (needs Bitcoin Core with ZMQ)
- **Port**: 10009 (gRPC), 9735 (P2P)

### LndHub
- **What**: Multi-user Lightning wallet service
- **How to run**: `npm start` (needs LND + Redis + Bitcoin Core)
- **Port**: 3000 (HTTP API)

### mining-pools
- **What**: JSON data file for identifying which pool mined each block
- **How to run**: Import data into your scripts/explorers
- **Uses**: Can be queried alongside Bitcoin Core block data

## Priority Setup Order

1. **Start Here**: Bitcoin Core ✅ (Already done!)
2. **Add Next**: 3xplCore (Simple, just needs RPC access)
3. **Advanced**: LND + LndHub (Requires more setup)
4. **Data**: mining-pools (Use as reference data)

## Full Bitcoin Core Config for All Services

Add to `~/.bitcoin/bitcoin.conf`:

```conf
# Basic settings
server=1
rest=1
txindex=1

# RPC authentication
rpcuser=your_username
rpcpassword=your_secure_password
rpcbind=127.0.0.1
rpcallowip=127.0.0.1

# For LND (Lightning Network)
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
zmqpubhashblock=tcp://127.0.0.1:28334

# Performance (optional)
dbcache=2048
maxmempool=300
```

After changing config:
```bash
bitcoin-cli stop
bitcoind  # Restart
```

## Test Everything

```bash
# 1. Bitcoin Core
bitcoin-cli getblockchaininfo

# 2. Bitcoin Core RPC
curl --user your_user:your_pass \
  --data-binary '{"method":"getblockcount"}' \
  http://127.0.0.1:8332/

# 3. LND (if running)
lncli getinfo

# 4. LndHub (if running)
curl http://127.0.0.1:3000/status

# 5. 3xplCore (if running)
cd ~/projects/3xplCore
php 3xpl.php bitcoin-main B 0  # Get genesis block
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| RPC connection refused | Check Bitcoin Core is running: `ps aux \| grep bitcoind` |
| RPC authentication failed | Verify credentials in bitcoin.conf match what you're using |
| txindex error | Enable `txindex=1` in bitcoin.conf and run `bitcoind -reindex` |
| LND won't connect | Check ZMQ settings in bitcoin.conf |
| Redis error | Start Redis: `sudo systemctl start redis-server` |

## Get More Help

- Full integration guide: `doc/repository-integration-guide.md`
- mempool.space setup: `contrib/mempool-space/README.md`
- Bitcoin Core RPC: `doc/JSON-RPC-interface.md`

## Architecture Diagram

```
                    ┌─────────────────┐
                    │  Bitcoin Core   │ ← You are here!
                    │   Port 8332     │
                    └────────┬────────┘
                             │ RPC Access
                ┌────────────┼────────────┐
                │            │            │
         ┌──────▼──────┐ ┌──▼───┐  ┌────▼─────┐
         │  3xplCore   │ │ LND  │  │ mining-  │
         │  Explorer   │ │Lightning│ pools    │
         └─────────────┘ └──┬───┘  │ (data)   │
                            │      └──────────┘
                     ┌──────▼──────┐
                     │   LndHub    │
                     │  Port 3000  │
                     └─────────────┘
```

---

**Remember**: Start with Bitcoin Core (✅ done!), add 3xplCore next (easiest), then LND/LndHub if you need Lightning features.
