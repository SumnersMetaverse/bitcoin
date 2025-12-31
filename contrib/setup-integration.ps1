# Bitcoin Core + Repository Integration Setup Script
# This script helps set up Bitcoin Core with your other repositories
# Run this in PowerShell as Administrator

# ============================================================================
# CONFIGURATION - UPDATE THESE WITH YOUR VALUES
# ============================================================================

# Bitcoin Core RPC Credentials (from your bitcoin.conf)
$BITCOIN_RPC_USER = "YOUR_RPC_USERNAME_HERE"
$BITCOIN_RPC_PASSWORD = "YOUR_RPC_PASSWORD_HERE"
$BITCOIN_RPC_HOST = "127.0.0.1"
$BITCOIN_RPC_PORT = "8332"

# Redis Configuration (from your Redis repository)
$REDIS_HOST = "YOUR_REDIS_HOST_HERE"
$REDIS_PORT = "6379"
$REDIS_PASSWORD = "YOUR_REDIS_PASSWORD_HERE"

# Tenderly Configuration (from tenderly.co)
$TENDERLY_API_KEY = "YOUR_TENDERLY_API_KEY_HERE"
$TENDERLY_PROJECT_ID = "YOUR_TENDERLY_PROJECT_ID_HERE"

# Project directories
$PROJECTS_DIR = "$HOME\projects"

# ============================================================================
# DO NOT EDIT BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Bitcoin Core Integration Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$prerequisites = @{
    "bitcoin-cli" = "Bitcoin Core"
    "git" = "Git"
    "python" = "Python 3"
    "node" = "Node.js"
}

$missing = @()
foreach ($cmd in $prerequisites.Keys) {
    if (Test-Command $cmd) {
        Write-Host "  [OK] $($prerequisites[$cmd]) found" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $($prerequisites[$cmd]) not found" -ForegroundColor Red
        $missing += $prerequisites[$cmd]
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing prerequisites: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "Please install them before continuing." -ForegroundColor Red
    exit 1
}

# Test Bitcoin Core RPC connection
Write-Host ""
Write-Host "Testing Bitcoin Core RPC connection..." -ForegroundColor Yellow

$bitcoinTest = @{
    jsonrpc = "2.0"
    id = "test"
    method = "getblockchaininfo"
    params = @()
} | ConvertTo-Json

$credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${BITCOIN_RPC_USER}:${BITCOIN_RPC_PASSWORD}"))
$headers = @{
    "Authorization" = "Basic $credentials"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "http://${BITCOIN_RPC_HOST}:${BITCOIN_RPC_PORT}" `
        -Method Post `
        -Headers $headers `
        -Body $bitcoinTest `
        -ErrorAction Stop
    
    Write-Host "  [OK] Bitcoin Core RPC connection successful" -ForegroundColor Green
    Write-Host "  Chain: $($response.result.chain)" -ForegroundColor Gray
    Write-Host "  Blocks: $($response.result.blocks)" -ForegroundColor Gray
} catch {
    Write-Host "  [ERROR] Cannot connect to Bitcoin Core RPC" -ForegroundColor Red
    Write-Host "  Please check your RPC credentials and ensure Bitcoin Core is running" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    exit 1
}

# Create projects directory
Write-Host ""
Write-Host "Setting up project directories..." -ForegroundColor Yellow

if (-not (Test-Path $PROJECTS_DIR)) {
    New-Item -ItemType Directory -Path $PROJECTS_DIR | Out-Null
    Write-Host "  [OK] Created $PROJECTS_DIR" -ForegroundColor Green
} else {
    Write-Host "  [OK] Projects directory exists" -ForegroundColor Green
}

# Clone 3xplCore if not exists
Write-Host ""
Write-Host "Setting up 3xplCore..." -ForegroundColor Yellow

$xplCoreDir = Join-Path $PROJECTS_DIR "3xplCore"
if (-not (Test-Path $xplCoreDir)) {
    Write-Host "  Cloning 3xplCore repository..." -ForegroundColor Gray
    git clone https://github.com/SumnersMetaverse/3xplCore.git $xplCoreDir
    Write-Host "  [OK] 3xplCore cloned" -ForegroundColor Green
} else {
    Write-Host "  [OK] 3xplCore already exists" -ForegroundColor Green
}

# Configure 3xplCore
$envFile = Join-Path $xplCoreDir ".env"
if (Test-Path "$xplCoreDir\.env.example") {
    if (-not (Test-Path $envFile)) {
        Copy-Item "$xplCoreDir\.env.example" $envFile
        Write-Host "  [OK] Created .env file from example" -ForegroundColor Green
        
        # Update .env with Bitcoin Core credentials
        $envContent = Get-Content $envFile
        $envContent = $envContent -replace 'MODULE_bitcoin-main_NODES\[\]=.*', "MODULE_bitcoin-main_NODES[]=${BITCOIN_RPC_USER}:${BITCOIN_RPC_PASSWORD}@${BITCOIN_RPC_HOST}:${BITCOIN_RPC_PORT}/"
        Set-Content -Path $envFile -Value $envContent
        Write-Host "  [OK] Updated .env with Bitcoin Core credentials" -ForegroundColor Green
    } else {
        Write-Host "  [OK] .env already configured" -ForegroundColor Green
    }
}

# Clone lndhub if not exists
Write-Host ""
Write-Host "Setting up lndhub..." -ForegroundColor Yellow

$lndhubDir = Join-Path $PROJECTS_DIR "lndhub"
if (-not (Test-Path $lndhubDir)) {
    Write-Host "  Cloning lndhub repository..." -ForegroundColor Gray
    git clone https://github.com/SumnersMetaverse/lndhub.git $lndhubDir
    Write-Host "  [OK] lndhub cloned" -ForegroundColor Green
    
    # Install dependencies
    Write-Host "  Installing Node.js dependencies..." -ForegroundColor Gray
    Push-Location $lndhubDir
    npm install
    Pop-Location
    Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  [OK] lndhub already exists" -ForegroundColor Green
}

# Clone mining-pools if not exists
Write-Host ""
Write-Host "Setting up mining-pools..." -ForegroundColor Yellow

$miningPoolsDir = Join-Path $PROJECTS_DIR "mining-pools"
if (-not (Test-Path $miningPoolsDir)) {
    Write-Host "  Cloning mining-pools repository..." -ForegroundColor Gray
    git clone https://github.com/SumnersMetaverse/mining-pools.git $miningPoolsDir
    Write-Host "  [OK] mining-pools cloned" -ForegroundColor Green
} else {
    Write-Host "  [OK] mining-pools already exists" -ForegroundColor Green
}

# Create environment template for easy reference
Write-Host ""
Write-Host "Creating environment reference file..." -ForegroundColor Yellow

$envTemplate = @"
# Bitcoin Core + Repository Integration Environment Variables
# Copy this to your PowerShell profile or .env file
# DO NOT commit this file with actual values!

# Bitcoin Core
`$env:BITCOIN_RPC_USER="$BITCOIN_RPC_USER"
`$env:BITCOIN_RPC_PASSWORD="$BITCOIN_RPC_PASSWORD"
`$env:BITCOIN_RPC_HOST="$BITCOIN_RPC_HOST"
`$env:BITCOIN_RPC_PORT="$BITCOIN_RPC_PORT"

# Redis
`$env:REDIS_HOST="$REDIS_HOST"
`$env:REDIS_PORT="$REDIS_PORT"
`$env:REDIS_PASSWORD="$REDIS_PASSWORD"

# Tenderly
`$env:TENDERLY_API_KEY="$TENDERLY_API_KEY"
`$env:TENDERLY_PROJECT_ID="$TENDERLY_PROJECT_ID"
"@

$envReferenceFile = Join-Path $PROJECTS_DIR "environment-reference.ps1"
Set-Content -Path $envReferenceFile -Value $envTemplate
Write-Host "  [OK] Environment reference saved to: $envReferenceFile" -ForegroundColor Green
Write-Host "  [INFO] Review and source this file when needed" -ForegroundColor Cyan

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the environment reference file: $envReferenceFile" -ForegroundColor Gray
Write-Host "  2. Configure LND if you need Lightning Network features" -ForegroundColor Gray
Write-Host "  3. Run 3xplCore: cd $xplCoreDir && php 3xpl.php bitcoin-main M" -ForegroundColor Gray
Write-Host "  4. See documentation in: REPOSITORY-INTEGRATION-QUICK-REFERENCE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed instructions, see:" -ForegroundColor Yellow
Write-Host "  - doc/repository-integration-guide.md" -ForegroundColor Gray
Write-Host "  - USING-YOUR-EXISTING-CREDENTIALS.md" -ForegroundColor Gray
Write-Host ""
Write-Host "[SECURITY REMINDER] Never commit the environment-reference.ps1 file!" -ForegroundColor Red
Write-Host ""
