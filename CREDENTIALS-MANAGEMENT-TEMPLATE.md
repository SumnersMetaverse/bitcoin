# Credentials Management Template

> **🔒 SECURITY WARNING:** Never store actual credentials in this file or commit them to Git!
> This is a TEMPLATE showing WHAT credentials you need and WHERE they should be stored.

## Purpose

This template helps you track:
- WHAT credentials are needed for your setup
- WHERE to store them securely (not the credentials themselves!)
- HOW to reference them in your applications

## ⚠️ NEVER Store in Git

**DO NOT** put any of the following in Git repositories:
- Passwords
- API keys
- Private keys
- RPC credentials
- Database passwords
- SSH keys
- Certificates

## Recommended Storage Solutions

### 1. Password Manager (Recommended for Personal Use)
- **1Password**: https://1password.com
- **Bitwarden**: https://bitwarden.com
- **LastPass**: https://lastpass.com
- **KeePass**: https://keepass.info

### 2. Secrets Management (Recommended for Production)
- **HashiCorp Vault**: For enterprise secrets management
- **AWS Secrets Manager**: If using AWS
- **Azure Key Vault**: If using Azure
- **Google Secret Manager**: If using Google Cloud

### 3. Environment Variables (For Development)
- Store in `.env` files (add to `.gitignore`)
- Load with dotenv or similar libraries
- Never commit `.env` to Git

### 4. Hardware Security (For Crypto Keys)
- **Ledger**: Hardware wallet for crypto keys
- **Trezor**: Hardware wallet for crypto keys
- **YubiKey**: For SSH and GPG keys

## Credentials Inventory Template

### Bitcoin Core Credentials

**Location to Store:** Password manager or secrets vault

```
Service: Bitcoin Core RPC
Location: ~/.bitcoin/bitcoin.conf
Stored in: [YOUR PASSWORD MANAGER NAME]
Entry name: "Bitcoin Core RPC - Production"

Credentials needed:
- rpcuser: [STORED IN PASSWORD MANAGER]
- rpcpassword: [STORED IN PASSWORD MANAGER]
- rpcport: [Usually 8332, can be plain text]

Environment variable reference:
- BITCOIN_RPC_USER=${BITCOIN_RPC_USER}
- BITCOIN_RPC_PASSWORD=${BITCOIN_RPC_PASSWORD}
```

### Tenderly.co Credentials

**Location to Store:** Password manager or secrets vault

```
Service: Tenderly RPC
Website: https://tenderly.co
Stored in: [YOUR PASSWORD MANAGER NAME]
Entry name: "Tenderly.co - Account"

Credentials needed:
- Account email: [STORED IN PASSWORD MANAGER]
- Account password: [STORED IN PASSWORD MANAGER]
- API Key: [STORED IN PASSWORD MANAGER]
- Project ID: [STORED IN PASSWORD MANAGER]
- RPC Endpoint URL: [STORED IN PASSWORD MANAGER]

Environment variable reference:
- TENDERLY_API_KEY=${TENDERLY_API_KEY}
- TENDERLY_PROJECT_ID=${TENDERLY_PROJECT_ID}
- TENDERLY_RPC_URL=${TENDERLY_RPC_URL}
```

### Redis Server Credentials

**Location to Store:** Password manager or secrets vault

```
Service: Redis Database
Repository: [YOUR REDIS REPOSITORY NAME]
Stored in: [YOUR PASSWORD MANAGER NAME]
Entry name: "Redis - Production Server"

Credentials needed:
- Host: [STORED IN PASSWORD MANAGER OR CONFIG]
- Port: [Usually 6379, can be plain text]
- Password: [STORED IN PASSWORD MANAGER]
- Username (if auth enabled): [STORED IN PASSWORD MANAGER]

Environment variable reference:
- REDIS_HOST=${REDIS_HOST}
- REDIS_PORT=6379
- REDIS_PASSWORD=${REDIS_PASSWORD}
```

### Lightning Network (LND) Credentials

**Location to Store:** Secure file system with proper permissions

```
Service: Lightning Network Daemon
Location: ~/.lnd/
Stored in: File system with 0600 permissions

Files needed:
- admin.macaroon: ~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon
- tls.cert: ~/.lnd/tls.cert
- Wallet password: [STORED IN PASSWORD MANAGER]

Backup location: [OFFLINE BACKUP LOCATION]

Environment variable reference:
- LND_MACAROON_PATH=~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon
- LND_TLS_CERT_PATH=~/.lnd/tls.cert
```

### SSH Server Access

**Location to Store:** SSH keys in ~/.ssh/ (not in password manager)

```
Service: Server SSH Access
Server: [YOUR SERVER IP/HOSTNAME]
Stored in: ~/.ssh/ directory

Files:
- Private key: ~/.ssh/id_rsa or ~/.ssh/id_ed25519
- Public key: ~/.ssh/id_rsa.pub
- Config: ~/.ssh/config

Passphrase: [STORED IN PASSWORD MANAGER]

Connection command:
ssh user@server.example.com
```

### GitHub Personal Access Tokens

**Location to Store:** Password manager

```
Service: GitHub API
Website: https://github.com
Stored in: [YOUR PASSWORD MANAGER NAME]
Entry name: "GitHub Personal Access Token"

Credentials needed:
- Personal Access Token: [STORED IN PASSWORD MANAGER]
- Scopes: repo, read:org, workflow

Environment variable reference:
- GITHUB_TOKEN=${GITHUB_TOKEN}
```

## Environment Variables Setup

### Create .env File (Add to .gitignore!)

```bash
# .env file (NEVER commit this file!)

# Bitcoin Core
BITCOIN_RPC_USER=your_user_from_password_manager
BITCOIN_RPC_PASSWORD=your_password_from_password_manager
BITCOIN_RPC_HOST=127.0.0.1
BITCOIN_RPC_PORT=8332

# Tenderly
TENDERLY_API_KEY=your_api_key_from_password_manager
TENDERLY_PROJECT_ID=your_project_id
TENDERLY_RPC_URL=https://rpc.tenderly.co/fork/your-fork-id

# Redis
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_from_password_manager

# LND
LND_MACAROON_PATH=/home/user/.lnd/data/chain/bitcoin/mainnet/admin.macaroon
LND_TLS_CERT_PATH=/home/user/.lnd/tls.cert

# Other services
# Add more as needed
```

### Add to .gitignore

```bash
# Add to .gitignore file
.env
.env.local
.env.production
*.pem
*.key
*.macaroon
credentials.json
secrets.json
```

## Loading Environment Variables

### Python
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

bitcoin_rpc_user = os.getenv('BITCOIN_RPC_USER')
bitcoin_rpc_password = os.getenv('BITCOIN_RPC_PASSWORD')
```

### Node.js
```javascript
require('dotenv').config();

const bitcoinRpcUser = process.env.BITCOIN_RPC_USER;
const bitcoinRpcPassword = process.env.BITCOIN_RPC_PASSWORD;
```

### Bash
```bash
source .env
echo $BITCOIN_RPC_USER
```

## Backup Strategy

### What to Backup

**Critical (Must backup):**
- Password manager database
- LND wallet seed (write on paper, store in safe)
- SSH private keys
- API keys and tokens

**Important (Should backup):**
- Configuration files (sanitized - no credentials!)
- Database backups
- Application data

### Where to Store Backups

1. **Online Encrypted Backup:**
   - Cloud storage with encryption (Dropbox, Google Drive)
   - Encrypted before upload
   - Use tools like `gpg` or `veracrypt`

2. **Offline Backup:**
   - External hard drive (encrypted)
   - USB drive (encrypted)
   - Store in safe location

3. **Physical Backup (for critical keys):**
   - Write seed phrases on paper
   - Store in fireproof safe
   - Consider safe deposit box for very critical keys

### Backup Encryption

```bash
# Encrypt backup file
gpg -c sensitive-backup.tar.gz

# Decrypt backup file
gpg -d sensitive-backup.tar.gz.gpg > sensitive-backup.tar.gz
```

## Access Control

### File Permissions

```bash
# Secure file permissions
chmod 600 ~/.ssh/id_rsa           # SSH private key
chmod 600 ~/.lnd/admin.macaroon   # LND macaroon
chmod 600 .env                    # Environment file
chmod 700 ~/.ssh                  # SSH directory
chmod 700 ~/.lnd                  # LND directory
```

### User Separation

- Don't run services as root
- Create dedicated users for services
- Use sudo only when necessary

```bash
# Create service user
sudo useradd -r -s /bin/false bitcoin
sudo useradd -r -s /bin/false lnd
```

## Credential Rotation Schedule

### Regular Rotation (Every 90 days)
- [ ] Bitcoin Core RPC password
- [ ] Database passwords
- [ ] API keys for third-party services

### Periodic Review (Every 6 months)
- [ ] SSH keys
- [ ] SSL/TLS certificates
- [ ] Service account passwords

### Immediate Rotation (When compromised)
- [ ] Any credential that may have been exposed
- [ ] Credentials after team member departure
- [ ] After security incident

## Emergency Procedures

### If Credentials Are Compromised

1. **Immediately:**
   - Change the compromised credentials
   - Revoke API keys/tokens
   - Check access logs for unauthorized use

2. **Within 24 hours:**
   - Rotate all related credentials
   - Review security logs
   - Notify affected parties if required

3. **Within 1 week:**
   - Conduct security audit
   - Update security procedures
   - Implement additional safeguards

### Emergency Contacts

```
Security Team: [YOUR CONTACT METHOD]
Password Manager Support: [VENDOR CONTACT]
Cloud Provider Security: [VENDOR CONTACT]
```

## Audit Trail

### Track Credential Changes

Keep a log (without actual credentials!) of:
- When credentials were created
- When credentials were changed
- Who has access to credentials
- When backups were made

Example format:
```
Date: 2025-12-31
Action: Rotated Bitcoin Core RPC password
Changed by: [Your name]
Reason: Regular 90-day rotation
Backup updated: Yes
```

## Compliance Checklist

- [ ] All credentials stored in password manager or vault
- [ ] No credentials in Git repository
- [ ] `.env` files in `.gitignore`
- [ ] File permissions set correctly (600/700)
- [ ] Backup strategy implemented
- [ ] Rotation schedule established
- [ ] Emergency procedures documented
- [ ] Team members trained on security practices
- [ ] Regular security audits scheduled

## Tools and Resources

### Password Managers
- 1Password: https://1password.com
- Bitwarden: https://bitwarden.com
- KeePass: https://keepass.info

### Secrets Management
- HashiCorp Vault: https://www.vaultproject.io
- AWS Secrets Manager: https://aws.amazon.com/secrets-manager/
- Doppler: https://www.doppler.com

### Security Best Practices
- OWASP: https://owasp.org
- NIST Guidelines: https://www.nist.gov/cybersecurity

## Support

For questions about:
- **Password managers**: Contact your chosen vendor
- **Secrets management**: See vendor documentation
- **Bitcoin security**: https://bitcoin.org/en/secure-your-wallet
- **General security**: Consult with security professionals

## Summary

Remember:
1. ✅ Store credentials in secure systems (password managers, vaults)
2. ✅ Use environment variables for application access
3. ✅ Keep backups encrypted and secure
4. ✅ Rotate credentials regularly
5. ❌ NEVER commit credentials to Git
6. ❌ NEVER share credentials in plain text
7. ❌ NEVER store credentials in documentation files

This template is your guide for WHAT and WHERE - not for storing actual values!
