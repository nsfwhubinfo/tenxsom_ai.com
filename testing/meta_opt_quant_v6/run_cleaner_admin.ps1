# PowerShell script to run duplicate cleaner with admin permissions
# This ensures access to all directories

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Host "This script needs to be run as Administrator. Relaunching..." -ForegroundColor Yellow
    Start-Process PowerShell -Verb RunAs "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Write-Host "Running with Administrator privileges" -ForegroundColor Green

# Ensure Python is available
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "Python not found. Please install Python 3.x first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Set working directory to script location
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host @"

===========================================
Windows Duplicate File Cleaner
===========================================

This tool will scan your C:\ drive for duplicate files.
Protected system directories will be skipped.

Options:
1. Scan only (generate report)
2. Scan and delete duplicates (dry run)
3. Scan and delete duplicates (ACTUAL DELETION)
4. Custom path scan

"@ -ForegroundColor Cyan

$choice = Read-Host "Enter your choice (1-4)"

$pythonScript = "windows_duplicate_cleaner.py"
$scanPath = "C:\"

switch ($choice) {
    "1" {
        Write-Host "Starting scan-only mode..." -ForegroundColor Yellow
        python $pythonScript $scanPath
    }
    "2" {
        Write-Host "Starting scan with dry-run deletion..." -ForegroundColor Yellow
        python $pythonScript $scanPath --delete
    }
    "3" {
        Write-Host "WARNING: This will DELETE duplicate files!" -ForegroundColor Red
        $confirm = Read-Host "Are you sure? Type 'YES' to continue"
        if ($confirm -eq "YES") {
            Write-Host "Starting scan with ACTUAL deletion..." -ForegroundColor Red
            python $pythonScript $scanPath --delete --no-dry-run --interactive
        } else {
            Write-Host "Cancelled." -ForegroundColor Green
        }
    }
    "4" {
        $customPath = Read-Host "Enter path to scan"
        if (Test-Path $customPath) {
            Write-Host "Scanning $customPath..." -ForegroundColor Yellow
            python $pythonScript $customPath
        } else {
            Write-Host "Path not found: $customPath" -ForegroundColor Red
        }
    }
    default {
        Write-Host "Invalid choice." -ForegroundColor Red
    }
}

Write-Host "`nOperation completed. Check the following files for results:" -ForegroundColor Green
Write-Host "- duplicate_report.json (detailed report)" -ForegroundColor Cyan
Write-Host "- duplicate_scan_*.log (scan log)" -ForegroundColor Cyan
Write-Host "- scan_errors.log (if any errors occurred)" -ForegroundColor Cyan

Read-Host "`nPress Enter to exit"