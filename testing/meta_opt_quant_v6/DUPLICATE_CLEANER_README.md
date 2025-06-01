# Windows Duplicate File Cleaner

## Quick Start

1. **Copy files to your Windows machine:**
   - `windows_duplicate_cleaner.py`
   - `run_cleaner_admin.ps1`

2. **Install Python 3.x if not already installed**

3. **Right-click `run_cleaner_admin.ps1` → Run with PowerShell**

## Features

- **Safe scanning** - Automatically skips system directories
- **MD5 hash verification** - Ensures files are truly identical
- **Smart duplicate selection** - Keeps newest file by default
- **Detailed reporting** - JSON report with all findings
- **Dry-run mode** - Preview what would be deleted
- **Interactive mode** - Confirm each deletion

## Usage Options

### Option 1: Scan Only (Recommended First Step)
```powershell
python windows_duplicate_cleaner.py C:\
```
This creates a report without deleting anything.

### Option 2: Dry Run (See What Would Be Deleted)
```powershell
python windows_duplicate_cleaner.py C:\ --delete
```

### Option 3: Interactive Deletion
```powershell
python windows_duplicate_cleaner.py C:\ --delete --no-dry-run --interactive
```

### Option 4: Automatic Deletion (Use With Caution!)
```powershell
python windows_duplicate_cleaner.py C:\ --delete --no-dry-run
```

### Scan Specific Directory
```powershell
python windows_duplicate_cleaner.py "D:\Downloads" --delete
```

### Exclude Additional Directories
```powershell
python windows_duplicate_cleaner.py C:\ --exclude "C:\ImportantFolder" "C:\BackupFolder"
```

## Protected Directories (Automatically Skipped)

- C:\Windows
- C:\Program Files
- C:\Program Files (x86)
- C:\ProgramData
- C:\$Recycle.Bin
- C:\System Volume Information

## Output Files

- **duplicate_report.json** - Detailed duplicate analysis
- **duplicate_scan_YYYYMMDD_HHMMSS.log** - Scan progress log
- **scan_errors.log** - Any permission/access errors

## Safety Features

1. **System directories protected** - Critical Windows folders are never touched
2. **Keeps newest file** - By default, retains the most recently modified version
3. **Dry run by default** - Must explicitly enable actual deletion
4. **Detailed logging** - Every action is logged
5. **Error handling** - Continues scanning even if some files can't be accessed

## Performance Tips

- Close unnecessary programs before scanning
- Scanning 1TB typically takes 30-60 minutes
- Deletion is much faster than scanning
- SSD drives scan faster than HDDs

## Troubleshooting

**"Permission denied" errors:**
- Run as Administrator using the PowerShell script
- Some files may be in use - close programs and retry

**"Python not found":**
- Install Python from python.org
- Ensure Python is added to PATH during installation

**Scan takes too long:**
- Start with specific directories like Downloads or Documents
- Exclude large backup folders that you know don't have duplicates

## Example Workflow

1. First, do a scan-only run to see what duplicates exist
2. Review the duplicate_report.json file
3. Do a dry-run to see what would be deleted
4. If satisfied, run with interactive mode to confirm important deletions
5. Check the space freed!

## Command Reference

```powershell
# Basic scan
python windows_duplicate_cleaner.py C:\

# Scan with report only
python windows_duplicate_cleaner.py C:\ > scan_output.txt

# Delete duplicates (dry run)
python windows_duplicate_cleaner.py C:\ --delete

# Delete duplicates (actual) with confirmation
python windows_duplicate_cleaner.py C:\ --delete --no-dry-run --interactive

# Scan specific folder
python windows_duplicate_cleaner.py "C:\Users\YourName\Downloads"

# Exclude folders
python windows_duplicate_cleaner.py C:\ --exclude "C:\Backups" "C:\Archives"
```

## Important Notes

- Always review the report before deleting
- Keep backups of critical data
- The tool identifies duplicates by content (MD5 hash), not filename
- Deleted files go to Recycle Bin (unless too large)
- Run regularly to prevent duplicate buildup