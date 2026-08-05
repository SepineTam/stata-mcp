#
# MCP-for-Stata Installation Script for Windows
# https://github.com/sepinetam/mcp-for-stata
#
# Usage:
#   .\install.ps1                    # Install to all supported clients
#   .\install.ps1 -Client claude     # Install to Claude Desktop only
#   .\install.ps1 -Client claude,cc  # Install to Claude Desktop and Claude Code

param(
    [string[]]$Client = @(),
    [switch]$Help
)

# Supported clients
$supportedClients = @("claude", "cc", "gemini", "cursor", "cline", "codex", "opencode", "openclaw")

if ($Help) {
    Write-Host "Usage: .\install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Client <name[]>  Target client(s) - can be comma-separated or multiple -Client args"
    Write-Host "                    Supported: $($supportedClients -join ', ')"
    Write-Host "  -Help             Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\install.ps1                    # Install to all clients"
    Write-Host "  .\install.ps1 -Client claude     # Install to Claude Desktop only"
    Write-Host "  .\install.ps1 -Client claude,cc  # Install to Claude Desktop and Claude Code"
    return
}

Write-Host ""
Write-Host "======================================"
Write-Host "    MCP-for-Stata Installation Script"
Write-Host "======================================"
Write-Host ""

# Add common uv installation paths to PATH
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:USERPROFILE\.local\bin;$env:Path"

# Add uv to the current process PATH when it is installed in a standard location.
function Add-UvToPath {
    $uvCandidates = @()

    if ($env:UV_INSTALL_DIR) {
        $uvCandidates += Join-Path $env:UV_INSTALL_DIR "uv.exe"
    }
    if ($env:XDG_BIN_HOME) {
        $uvCandidates += Join-Path $env:XDG_BIN_HOME "uv.exe"
    }
    if ($env:XDG_DATA_HOME) {
        $uvCandidates += Join-Path $env:XDG_DATA_HOME "..\bin\uv.exe"
    }
    if ($HOME) {
        $uvCandidates += Join-Path $HOME ".local\bin\uv.exe"
        $uvCandidates += Join-Path $HOME ".cargo\bin\uv.exe"
    }
    if ($env:USERPROFILE) {
        $uvCandidates += Join-Path $env:USERPROFILE ".local\bin\uv.exe"
        $uvCandidates += Join-Path $env:USERPROFILE ".cargo\bin\uv.exe"
    }
    if ($env:CARGO_HOME) {
        $uvCandidates += Join-Path $env:CARGO_HOME "bin\uv.exe"
    }

    foreach ($uvCandidate in ($uvCandidates | Select-Object -Unique)) {
        if (Test-Path -LiteralPath $uvCandidate -PathType Leaf) {
            $uvDirectory = Split-Path -Parent $uvCandidate
            if ($uvDirectory -notin ($env:Path -split ";")) {
                $env:Path = "$uvDirectory;$env:Path"
            }
            return $true
        }
    }

    return $false
}

# Check if uv is installed.
function Check-Uv {
    if ((Get-Command uv -ErrorAction SilentlyContinue) -or (Add-UvToPath)) {
        Write-Host "[OK] uv is installed" -ForegroundColor Green
        return $true
    }
    return $false
}

# Run the official installer in a child process so its `exit` cannot close the
# user's current PowerShell window. Bypass applies only to the child process.
function Invoke-UvInstaller {
    $powerShellExecutable = (Get-Process -Id $PID).Path
    if (-not $powerShellExecutable) {
        $powerShellExecutable = (Get-Command powershell.exe -ErrorAction Stop).Source
    }

    & $powerShellExecutable `
        -NoProfile `
        -ExecutionPolicy Bypass `
        -Command "Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression" `
        2>&1 | ForEach-Object { Write-Host $_ }

    return ($LASTEXITCODE -eq 0)
}

# Install uv
function Install-Uv {
    Write-Host "[!] uv is not installed" -ForegroundColor Yellow
    Write-Host ""

    $choice = Read-Host "Do you want to install uv? [Y/n]"
    switch -Regex ($choice) {
        "^(n|N|no|No|NO)$" {
            Write-Host "[X] Installation cancelled." -ForegroundColor Red
            return $false
        }
        default {
            Write-Host ""
            $maxRetries = 3
            $retryCount = 0

            while ($retryCount -lt $maxRetries) {
                Write-Host "Installing uv... (attempt $($retryCount + 1)/$maxRetries)"
                try {
                    $installerSucceeded = Invoke-UvInstaller
                } catch {
                    Write-Host "[!] uv installer error: $($_.Exception.Message)" -ForegroundColor Yellow
                    $installerSucceeded = $false
                }

                if ($installerSucceeded -and (Check-Uv)) {
                    Write-Host "[OK] uv installed successfully" -ForegroundColor Green
                    return $true
                }

                $retryCount++
                if ($retryCount -lt $maxRetries) {
                    Write-Host "[!] Installation failed, retrying in 3 seconds..." -ForegroundColor Yellow
                    Start-Sleep -Seconds 3
                }
            }

            Write-Host "[X] Failed to install uv after $maxRetries attempts." -ForegroundColor Red
            Write-Host "    The PowerShell window will remain open so you can review the error above."
            Write-Host "    Manual install command:"
            Write-Host '    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"'
            return $false
        }
    }
}

# Main installation logic
# Step 1: Check and install uv
if (-not (Check-Uv)) {
    if (-not (Install-Uv)) {
        throw "[X] MCP-for-Stata installation stopped because uv is unavailable."
    }
}

# Step 2: Parse and validate clients
$targetClients = @()
foreach ($c in $Client) {
    # Split by comma in case of "claude,cc" format
    $splitClients = $c -split ","
    foreach ($sc in $splitClients) {
        $trimmed = $sc.Trim()
        if ($trimmed -in $supportedClients) {
            $targetClients += $trimmed
        } elseif ($trimmed -ne "") {
            Write-Host "[X] Unknown client: $trimmed" -ForegroundColor Red
            Write-Host "    Supported clients: $($supportedClients -join ', ')"
        }
    }
}

# Step 3: Install to clients
if ($targetClients.Count -eq 0) {
    # No specific clients specified, install to all
    Write-Host ""
    Write-Host "Installing to all supported clients..."
    uvx stata-mcp install --all
    if ($LASTEXITCODE -ne 0) {
        throw "[X] MCP-for-Stata installation failed. Review the error above."
    }
} else {
    # Install to specified clients
    foreach ($client in $targetClients) {
        Write-Host ""
        Write-Host "Installing to $client..."
        uvx stata-mcp install -c $client
        if ($LASTEXITCODE -ne 0) {
            throw "[X] Installation failed for $client. Review the error above."
        }
    }
}

# Step 4: Remind user to restart
Write-Host ""
Write-Host "======================================"
Write-Host "[OK] Installation complete!" -ForegroundColor Green
Write-Host "======================================"
Write-Host ""
Write-Host "Please restart your MCP client(s) for the changes to take effect."
Write-Host ""
Write-Host "For more information, visit: https://github.com/sepinetam/mcp-for-stata"
Write-Host ""
