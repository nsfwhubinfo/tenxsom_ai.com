#!/usr/bin/env python3
"""
Windows Duplicate File Cleaner
Safely finds and removes duplicate files from Windows drives
"""

import os
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import argparse
import logging

class DuplicateFileCleaner:
    def __init__(self, root_path="C:\\", chunk_size=8192):
        self.root_path = root_path
        self.chunk_size = chunk_size
        self.file_hashes = defaultdict(list)
        self.duplicates = []
        self.total_size_saved = 0
        self.scan_errors = []
        self.protected_dirs = {
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\ProgramData",
            "C:\\$Recycle.Bin",
            "C:\\System Volume Information"
        }
        
        # Setup logging
        log_file = f"duplicate_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_file_hash(self, filepath):
        """Calculate MD5 hash of a file"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(self.chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.scan_errors.append((filepath, str(e)))
            return None

    def is_safe_to_scan(self, path):
        """Check if directory is safe to scan"""
        path_str = str(path).upper()
        for protected in self.protected_dirs:
            if path_str.startswith(protected.upper()):
                return False
        return True

    def scan_directory(self, directory):
        """Recursively scan directory for files"""
        scanned_files = 0
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(directory):
                # Filter out protected directories
                dirs[:] = [d for d in dirs if self.is_safe_to_scan(os.path.join(root, d))]
                
                for filename in files:
                    filepath = os.path.join(root, filename)
                    
                    try:
                        # Skip symbolic links and system files
                        if os.path.islink(filepath):
                            continue
                            
                        file_stat = os.stat(filepath)
                        file_size = file_stat.st_size
                        
                        # Skip empty files
                        if file_size == 0:
                            continue
                        
                        # Calculate hash
                        file_hash = self.get_file_hash(filepath)
                        if file_hash:
                            self.file_hashes[file_hash].append({
                                'path': filepath,
                                'size': file_size,
                                'modified': datetime.fromtimestamp(file_stat.st_mtime)
                            })
                            scanned_files += 1
                            total_size += file_size
                            
                            if scanned_files % 1000 == 0:
                                self.logger.info(f"Scanned {scanned_files} files ({total_size / 1024 / 1024:.2f} MB)")
                                
                    except PermissionError:
                        self.scan_errors.append((filepath, "Permission denied"))
                    except Exception as e:
                        self.scan_errors.append((filepath, str(e)))
                        
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            
        return scanned_files, total_size

    def find_duplicates(self):
        """Identify duplicate files from hash map"""
        self.logger.info("Analyzing duplicates...")
        
        for file_hash, file_list in self.file_hashes.items():
            if len(file_list) > 1:
                # Sort by modification time (keep newest)
                file_list.sort(key=lambda x: x['modified'], reverse=True)
                
                original = file_list[0]
                duplicates = file_list[1:]
                
                duplicate_size = sum(f['size'] for f in duplicates)
                self.total_size_saved += duplicate_size
                
                self.duplicates.append({
                    'hash': file_hash,
                    'original': original,
                    'duplicates': duplicates,
                    'size_saved': duplicate_size
                })
        
        self.logger.info(f"Found {len(self.duplicates)} sets of duplicates")
        self.logger.info(f"Potential space savings: {self.total_size_saved / 1024 / 1024 / 1024:.2f} GB")

    def generate_report(self, output_file="duplicate_report.json"):
        """Generate detailed report of duplicates"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'root_path': self.root_path,
            'total_files_scanned': sum(len(files) for files in self.file_hashes.values()),
            'duplicate_sets': len(self.duplicates),
            'total_duplicates': sum(len(d['duplicates']) for d in self.duplicates),
            'space_savings_gb': self.total_size_saved / 1024 / 1024 / 1024,
            'scan_errors': len(self.scan_errors),
            'duplicates': []
        }
        
        for dup_set in self.duplicates:
            report['duplicates'].append({
                'original_file': dup_set['original']['path'],
                'original_size_mb': dup_set['original']['size'] / 1024 / 1024,
                'duplicate_files': [d['path'] for d in dup_set['duplicates']],
                'space_saved_mb': dup_set['size_saved'] / 1024 / 1024
            })
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Report saved to {output_file}")

    def delete_duplicates(self, dry_run=True, interactive=False):
        """Delete duplicate files with safety checks"""
        deleted_count = 0
        deleted_size = 0
        
        self.logger.info(f"{'DRY RUN: ' if dry_run else ''}Starting duplicate deletion...")
        
        for dup_set in self.duplicates:
            duplicates = dup_set['duplicates']
            
            for dup in duplicates:
                filepath = dup['path']
                
                # Safety check - never delete from protected directories
                if not self.is_safe_to_scan(filepath):
                    self.logger.warning(f"Skipping protected file: {filepath}")
                    continue
                
                if interactive and not dry_run:
                    response = input(f"\nDelete {filepath}? (y/n): ").lower()
                    if response != 'y':
                        continue
                
                try:
                    if not dry_run:
                        os.remove(filepath)
                        self.logger.info(f"Deleted: {filepath}")
                    else:
                        self.logger.info(f"Would delete: {filepath}")
                    
                    deleted_count += 1
                    deleted_size += dup['size']
                    
                except Exception as e:
                    self.logger.error(f"Failed to delete {filepath}: {e}")
        
        self.logger.info(f"{'Would delete' if dry_run else 'Deleted'} {deleted_count} files")
        self.logger.info(f"Space {'would be' if dry_run else ''} freed: {deleted_size / 1024 / 1024 / 1024:.2f} GB")

    def run(self, delete=False, dry_run=True, interactive=False):
        """Main execution method"""
        self.logger.info(f"Starting duplicate scan on {self.root_path}")
        self.logger.info(f"Protected directories: {', '.join(self.protected_dirs)}")
        
        # Scan for files
        files_scanned, total_size = self.scan_directory(self.root_path)
        self.logger.info(f"Total files scanned: {files_scanned}")
        self.logger.info(f"Total size: {total_size / 1024 / 1024 / 1024:.2f} GB")
        
        # Find duplicates
        self.find_duplicates()
        
        # Generate report
        self.generate_report()
        
        # Delete if requested
        if delete:
            self.delete_duplicates(dry_run=dry_run, interactive=interactive)
        
        # Report errors
        if self.scan_errors:
            self.logger.warning(f"Encountered {len(self.scan_errors)} errors during scan")
            error_file = "scan_errors.log"
            with open(error_file, 'w') as f:
                for path, error in self.scan_errors:
                    f.write(f"{path}: {error}\n")
            self.logger.info(f"Error details saved to {error_file}")

def main():
    parser = argparse.ArgumentParser(description="Find and remove duplicate files on Windows")
    parser.add_argument("path", nargs='?', default="C:\\", help="Root path to scan (default: C:\\)")
    parser.add_argument("--delete", action="store_true", help="Delete duplicate files")
    parser.add_argument("--no-dry-run", action="store_true", help="Actually delete files (use with caution!)")
    parser.add_argument("--interactive", action="store_true", help="Ask before deleting each file")
    parser.add_argument("--exclude", nargs='+', help="Additional directories to exclude")
    
    args = parser.parse_args()
    
    cleaner = DuplicateFileCleaner(root_path=args.path)
    
    # Add custom exclusions
    if args.exclude:
        cleaner.protected_dirs.update(args.exclude)
    
    # Run the cleaner
    cleaner.run(
        delete=args.delete,
        dry_run=not args.no_dry_run,
        interactive=args.interactive
    )

if __name__ == "__main__":
    main()