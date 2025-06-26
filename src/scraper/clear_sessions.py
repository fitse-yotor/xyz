#!/usr/bin/env python3
"""
Session Management Script for Telegram Scraper
Clears old sessions to allow login with a new account
"""

import os
import glob
import shutil

def clear_sessions():
    """Clear all Telegram session files"""
    print("🧹 Clearing Telegram session files...")
    
    # List of session file patterns to remove
    session_patterns = [
        "*.session",
        "*.session-journal",
        "state.json",
        "scraper_state.json"
    ]
    
    removed_files = []
    
    for pattern in session_patterns:
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                removed_files.append(file)
                print(f"✓ Removed: {file}")
            except Exception as e:
                print(f"✗ Error removing {file}: {str(e)}")
    
    if removed_files:
        print(f"\n✅ Successfully removed {len(removed_files)} session files")
        print("🔄 You can now run the scraper with a new Telegram account")
    else:
        print("\nℹ️  No session files found to remove")
    
    return len(removed_files)

def show_current_sessions():
    """Show current session files"""
    print("📋 Current session files:")
    
    session_patterns = [
        "*.session",
        "*.session-journal",
        "state.json",
        "scraper_state.json"
    ]
    
    found_files = []
    
    for pattern in session_patterns:
        files = glob.glob(pattern)
        found_files.extend(files)
    
    if found_files:
        for file in found_files:
            size = os.path.getsize(file) if os.path.exists(file) else 0
            print(f"  📄 {file} ({size} bytes)")
    else:
        print("  No session files found")

def main():
    """Main function"""
    print("=" * 50)
    print("Telegram Scraper Session Manager")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Show current session files")
        print("2. Clear all session files")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            show_current_sessions()
        elif choice == '2':
            confirm = input("⚠️  This will remove all session files. Continue? (y/N): ").strip().lower()
            if confirm == 'y':
                clear_sessions()
            else:
                print("❌ Operation cancelled")
        elif choice == '3':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 