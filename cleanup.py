#!/usr/bin/env python3
"""
File and Session Cleanup Utility
Automatically removes old files from uploads, sessions, and exports
"""

import os
import sys
import time
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def cleanup_old_files(folder, max_age_hours=24, keep_gitkeep=True):
    """
    Delete files older than max_age_hours from a folder.
    
    Args:
        folder (str): Folder path to clean
        max_age_hours (int): Maximum file age in hours
        keep_gitkeep (bool): Keep .gitkeep files
        
    Returns:
        tuple: (deleted_count, deleted_size_bytes)
    """
    if not os.path.exists(folder):
        logger.warning(f"Folder does not exist: {folder}")
        return 0, 0
    
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    deleted_count = 0
    deleted_size = 0
    
    logger.info(f"Cleaning {folder} (files older than {max_age_hours}h)...")
    
    for filename in os.listdir(folder):
        # Skip .gitkeep files
        if keep_gitkeep and filename == '.gitkeep':
            continue
        
        filepath = os.path.join(folder, filename)
        
        # Only process files (not directories)
        if not os.path.isfile(filepath):
            continue
        
        try:
            # Check file modification time
            mtime = os.path.getmtime(filepath)
            
            if mtime < cutoff:
                # Get file size before deletion
                size = os.path.getsize(filepath)
                
                # Delete the file
                os.remove(filepath)
                
                deleted_count += 1
                deleted_size += size
                
                age_hours = (now - mtime) / 3600
                logger.info(f"  Deleted: {filename} (age: {age_hours:.1f}h, size: {size/1024:.1f}KB)")
        
        except Exception as e:
            logger.error(f"  Error processing {filename}: {e}")
    
    if deleted_count > 0:
        logger.info(f"  Total: {deleted_count} files, {deleted_size/1024/1024:.2f}MB freed")
    else:
        logger.info(f"  No files to delete")
    
    return deleted_count, deleted_size


def cleanup_sessions(session_folder='sessions', max_age_hours=24):
    """
    Clean up old session files using SessionManager.
    
    Args:
        session_folder (str): Session folder path
        max_age_hours (int): Maximum session age in hours
        
    Returns:
        int: Number of sessions deleted
    """
    try:
        # Import SessionManager
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from session_manager import SessionManager
        
        session_manager = SessionManager(session_folder)
        deleted_count = session_manager.cleanup_old_sessions(max_age_hours)
        
        logger.info(f"Session cleanup: {deleted_count} sessions deleted")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error during session cleanup: {e}")
        return 0


def main():
    """Main cleanup routine"""
    
    print("=" * 70)
    print("Bangla PDF Editor - File Cleanup Utility")
    print("=" * 70)
    print()
    
    # Configuration: (folder, max_age_hours)
    folders_to_clean = [
        ('backend/uploads', 24, "Uploaded PDFs"),
        ('backend/exports', 48, "Exported PDFs"),
        ('uploads', 24, "Uploaded PDFs (root)"),
        ('exports', 48, "Exported PDFs (root)"),
    ]
    
    total_deleted = 0
    total_size = 0
    
    # Clean regular folders
    for folder, max_age, description in folders_to_clean:
        print(f"\n📁 {description}: {folder}")
        deleted, size = cleanup_old_files(folder, max_age)
        total_deleted += deleted
        total_size += size
    
    # Clean sessions using SessionManager
    print(f"\n📁 Session files: backend/sessions")
    session_deleted = cleanup_sessions('backend/sessions', 24)
    
    print(f"\n📁 Session files: sessions")
    session_deleted += cleanup_sessions('sessions', 24)
    
    total_deleted += session_deleted
    
    # Summary
    print("\n" + "=" * 70)
    print("CLEANUP SUMMARY")
    print("=" * 70)
    print(f"Total files deleted: {total_deleted}")
    print(f"Total space freed: {total_size/1024/1024:.2f}MB")
    print("=" * 70)
    
    return total_deleted


if __name__ == '__main__':
    try:
        count = main()
        sys.exit(0 if count >= 0 else 1)
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        sys.exit(1)
