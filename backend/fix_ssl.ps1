# PowerShell script to fix SSL certificate issues for Python
# Run this as Administrator if needed

Write-Host "SSL Certificate Fix Script" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠ Not running as Administrator. Some fixes may not work." -ForegroundColor Yellow
}

# Function to test internet connectivity
function Test-Internet {
    try {
        $test = Test-NetConnection -ComputerName "8.8.8.8" -Port 443 -InformationLevel Quiet
        return $test
    } catch {
        return $false
    }
}

# Function to update certificates
function Update-Certificates {
    Write-Host "Updating certificates..." -ForegroundColor Cyan
    
    try {
        # Update Windows certificates
        if ($isAdmin) {
            Write-Host "Updating Windows certificate store..."
            certlm.msc
            Write-Host "✓ Certificate store opened" -ForegroundColor Green
        } else {
            Write-Host "⚠ Need Administrator privileges to update system certificates" -ForegroundColor Yellow
        }
        
        # Update pip certificates
        Write-Host "Updating pip certificates..."
        pip install --upgrade certifi
        Write-Host "✓ Certifi updated" -ForegroundColor Green
        
        return $true
    } catch {
        Write-Host "✗ Error updating certificates: $_" -ForegroundColor Red
        return $false
    }
}

# Function to set environment variables
function Set-SSLEnvironment {
    Write-Host "Setting SSL environment variables..." -ForegroundColor Cyan
    
    try {
        # Get certifi path
        $certifiPath = python -c "import certifi; print(certifi.where())"
        
        # Set environment variables
        [Environment]::SetEnvironmentVariable("SSL_CERT_FILE", $certifiPath, "User")
        [Environment]::SetEnvironmentVariable("REQUESTS_CA_BUNDLE", $certifiPath, "User")
        [Environment]::SetEnvironmentVariable("CURL_CA_BUNDLE", $certifiPath, "User")
        
        Write-Host "✓ Environment variables set" -ForegroundColor Green
        Write-Host "SSL_CERT_FILE: $certifiPath" -ForegroundColor Gray
        
        return $true
    } catch {
        Write-Host "✗ Error setting environment variables: $_" -ForegroundColor Red
        return $false
    }
}

# Function to disable SSL verification (NOT RECOMMENDED)
function Disable-SSLVerification {
    Write-Host "Disabling SSL verification (NOT RECOMMENDED for production)..." -ForegroundColor Yellow
    
    try {
        [Environment]::SetEnvironmentVariable("PYTHONHTTPSVERIFY", "0", "User")
        [Environment]::SetEnvironmentVariable("CURL_CA_BUNDLE", "", "User")
        
        Write-Host "✓ SSL verification disabled" -ForegroundColor Green
        Write-Host "⚠ This is not secure! Only use for testing." -ForegroundColor Yellow
        
        return $true
    } catch {
        Write-Host "✗ Error disabling SSL verification: $_" -ForegroundColor Red
        return $false
    }
}

# Function to test Python SSL
function Test-PythonSSL {
    Write-Host "Testing Python SSL..." -ForegroundColor Cyan
    
    try {
        $result = python -c "import ssl, urllib.request; urllib.request.urlopen('https://huggingface.co', timeout=10); print('SSL OK')"
        if ($result -eq "SSL OK") {
            Write-Host "✓ Python SSL working" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Python SSL failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Python SSL test failed: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "Starting SSL diagnosis..." -ForegroundColor Cyan

# Test internet connectivity
if (Test-Internet) {
    Write-Host "✓ Internet connectivity OK" -ForegroundColor Green
} else {
    Write-Host "✗ No internet connectivity" -ForegroundColor Red
    exit 1
}

# Test initial Python SSL
if (Test-PythonSSL) {
    Write-Host "✓ SSL already working! No fixes needed." -ForegroundColor Green
    exit 0
}

# Try fixes
Write-Host "`nAttempting fixes..." -ForegroundColor Cyan

# Method 1: Update certificates
if (Update-Certificates) {
    if (Test-PythonSSL) {
        Write-Host "✓ Fixed with certificate update!" -ForegroundColor Green
        exit 0
    }
}

# Method 2: Set environment variables
if (Set-SSLEnvironment) {
    if (Test-PythonSSL) {
        Write-Host "✓ Fixed with environment variables!" -ForegroundColor Green
        exit 0
    }
}

# Method 3: Disable SSL verification (last resort)
Write-Host "`nWARNING: Attempting to disable SSL verification..." -ForegroundColor Yellow
$confirm = Read-Host "This is not secure. Continue? (y/N)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    if (Disable-SSLVerification) {
        if (Test-PythonSSL) {
            Write-Host "✓ SSL verification disabled - this worked but is not secure!" -ForegroundColor Yellow
        }
    }
}

Write-Host "`nIf nothing worked, you may need to:" -ForegroundColor Yellow
Write-Host "1. Contact your IT team about corporate certificates" -ForegroundColor Gray
Write-Host "2. Configure proxy settings if behind a corporate firewall" -ForegroundColor Gray
Write-Host "3. Use the offline setup instructions in OFFLINE_SETUP.md" -ForegroundColor Gray

Write-Host "`nPress any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
