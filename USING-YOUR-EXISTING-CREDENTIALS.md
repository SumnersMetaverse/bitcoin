# Important: Using Your Existing Credentials

## What This Documentation Is

The documentation in this repository (`doc/mempool-space-integration.md`, `doc/repository-integration-guide.md`, etc.) is **reference material** that shows you:

- HOW to connect your repositories together
- WHERE to place configuration values
- WHAT order to execute things in
- HOW to troubleshoot issues

## What This Documentation Is NOT

This documentation does NOT:
- ❌ Replace your existing Docker files
- ❌ Replace your existing configuration files
- ❌ Create new RPC credentials you need to use
- ❌ Contain your actual server information

## Using Your Existing Setup

### Your Existing Files to Use

You already have configuration files in your repositories:

1. **lndhub** - Already has:
   - `Dockerfile` - Use this!
   - `config.js` - Configure with YOUR credentials
   - Docker Compose files (if any)

2. **3xplCore** - Already has:
   - `.env.example` - Copy to `.env` and add YOUR credentials
   - Setup scripts

3. **mining-pools** - Already has:
   - Data files to reference

### Your Existing Credentials to Use

#### From Tenderly.co
You mentioned you have RPC endpoints in Tenderly. Use those:
- Your Tenderly RPC URLs
- Your Tenderly API keys
- Your Tenderly project settings

#### From Your Redis Repository
You mentioned your private server info is there. Use that:
- Your Redis host address
- Your Redis port
- Your Redis password (if set)
- Your server IPs and configurations

#### From Bitcoin Core
Your Bitcoin Core RPC credentials (from `~/.bitcoin/bitcoin.conf`):
- Your actual `rpcuser` value
- Your actual `rpcpassword` value
- Your actual `rpcport` (if custom)

## How to Use This Documentation

### Step 1: Find Your Actual Credentials

**For Tenderly RPC:**
1. Log into https://tenderly.co
2. Go to your project/dashboard
3. Navigate to Node RPC section
4. Find your RPC endpoints (they look like: `https://rpc.tenderly.co/fork/YOUR-FORK-ID`)
5. Copy your actual RPC URLs and API keys
6. Use these in your application configs where RPC endpoints are needed

**Note on Tenderly:** If you're using Tenderly for Ethereum/EVM chains, those are separate from Bitcoin Core. Tenderly provides:
- Ethereum RPC endpoints
- Forking and simulation tools
- EVM-compatible networks

For **Bitcoin Core**, you'll use the standard Bitcoin RPC (not Tenderly), configured in `bitcoin.conf`.

**For Redis:**
1. Go to your Redis repository (you mentioned you have one)
2. Find your server information
3. Note your Redis host, port, password

**For Bitcoin Core:**
1. Check your `~/.bitcoin/bitcoin.conf` file
2. Look for existing `rpcuser` and `rpcpassword` lines
3. Use those values (don't create new ones unless you want to)

### Step 2: Update Configuration Files

When the guides say:

```conf
rpcuser=mempool
rpcpassword=your_secure_password
```

This means: **Replace "mempool" and "your_secure_password" with YOUR actual credentials.**

### Step 3: Use YOUR Existing Docker Files

When setting up lndhub or 3xplCore:

1. Use the **existing** Dockerfile in those repositories
2. Update the **existing** config files with YOUR credentials
3. Don't create new Docker files - use what's already there

## Example: Connecting lndhub

### Wrong Approach ❌
- Creating new config files from scratch
- Using example credentials from documentation

### Correct Approach ✅

1. **Clone your existing lndhub repo** (you already have this)
2. **Find your existing credentials:**
   - Bitcoin Core RPC: Check `~/.bitcoin/bitcoin.conf`
   - Redis: Check your Redis repository
   - LND: Use your existing LND setup
3. **Update config.js with YOUR values:**
   ```javascript
   module.exports = {
     bitcoind: {
       rpc: 'http://your-actual-bitcoin-host:8332',  // YOUR Bitcoin Core
     },
     redis: {
       host: 'your-redis-host.com',  // FROM your Redis repository
       port: 6379,
       password: 'your-actual-redis-password',  // FROM your Redis repository
     },
     lnd: {
       url: 'your-lnd-host:10009',  // YOUR LND server
     },
   };
   ```
4. **Use the existing Dockerfile:**
   ```bash
   docker build -t my-lndhub .
   docker run -p 3000:3000 my-lndhub
   ```

## Example: Connecting 3xplCore

### Correct Approach ✅

1. **Clone your existing 3xplCore repo**
2. **Copy the example env:**
   ```bash
   cp .env.example .env
   ```
3. **Edit .env with YOUR Bitcoin Core RPC:**
   ```bash
   # Use YOUR actual Bitcoin Core credentials
   MODULE_bitcoin-main_NODES[]=http://your-rpc-user:your-rpc-password@127.0.0.1:8332/
   ```
4. **Run using existing setup:**
   ```bash
   php 3xpl.php bitcoin-main M
   ```

## TL;DR - Quick Summary

1. ✅ **Use your existing Docker/config files** from your repositories
2. ✅ **Use your existing credentials** from Tenderly, Redis repository, and Bitcoin Core
3. ✅ **Use this documentation** as a reference for HOW to connect everything
4. ❌ **Don't create new files** - use what you already have
5. ❌ **Don't use example credentials** - use your actual ones

## Still Confused?

Ask yourself:
- **"Do I have existing Docker files?"** → Yes? Use those!
- **"Do I have existing credentials?"** → Yes? Use those!
- **"What is this documentation for?"** → To show you HOW to connect everything, not WHAT to connect with

The guides show the **process and structure**. You provide the **actual values**.

Think of it like a recipe:
- The documentation is the **recipe** (instructions)
- Your Tenderly/Redis/Bitcoin credentials are the **ingredients** (actual values)
- Your existing Docker/config files are the **tools** (what you use)

You don't need to create new tools or ingredients - just follow the recipe using what you already have!
