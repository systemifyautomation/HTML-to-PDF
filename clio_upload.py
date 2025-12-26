#!/usr/bin/env python3
"""
Clio File Upload Utility

This script allows you to upload files to your Clio account.
It provides a simple command-line interface to select a file from your PC
and upload it to Clio.com using the Clio Manage API.

Requirements:
    - Clio account with API access
    - Clio access token (OAuth2)
    - clio-manage-api-client installed (pip install clio-manage-api-client)

Setup:
    1. Copy .clio-config.example.json to .clio-config.json
    2. Add your Clio access token to .clio-config.json
    3. Run this script: python clio_upload.py

To get a Clio access token:
    1. Log in to your Clio account
    2. Go to Settings > Developer Applications
    3. Create a new application or use an existing one
    4. Generate an access token
    5. Copy the token to .clio-config.json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    from clio_manage_python_client import Manage as ClioClient
except ImportError:
    print("Error: clio-manage-api-client not installed")
    print("Install it with: pip install clio-manage-api-client")
    sys.exit(1)


class ClioFileUploader:
    """
    Handle file uploads to Clio.com
    """
    
    def __init__(self, config_path='.clio-config.json'):
        """
        Initialize the Clio uploader with configuration
        
        Args:
            config_path: Path to the Clio configuration file
        """
        self.config = self.load_config(config_path)
        self.client = None
        self.initialize_client()
    
    def load_config(self, config_path):
        """
        Load Clio configuration from JSON file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dictionary with configuration
        """
        if not os.path.exists(config_path):
            print(f"Error: Configuration file not found: {config_path}")
            print(f"Please copy .clio-config.example.json to {config_path}")
            print("and add your Clio access token.")
            sys.exit(1)
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            if not config.get('access_token') or config['access_token'] == 'YOUR_CLIO_ACCESS_TOKEN_HERE':
                print("Error: Please set your Clio access token in .clio-config.json")
                print("\nTo get your access token:")
                print("1. Log in to https://app.clio.com")
                print("2. Go to Settings > Developer Applications")
                print("3. Create a new application or use an existing one")
                print("4. Generate an access token")
                print("5. Add it to .clio-config.json")
                sys.exit(1)
            
            return config
            
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def initialize_client(self):
        """
        Initialize the Clio API client
        """
        try:
            self.client = ClioClient(access_token=self.config['access_token'])
            print("✓ Successfully connected to Clio API")
        except Exception as e:
            print(f"Error initializing Clio client: {e}")
            sys.exit(1)
    
    def get_matters(self, limit=10):
        """
        Get a list of matters from Clio
        
        Args:
            limit: Maximum number of matters to retrieve
            
        Returns:
            List of matters
        """
        try:
            matters = self.client.get.matters(limit=limit)
            return matters.get('data', [])
        except Exception as e:
            print(f"Error fetching matters: {e}")
            return []
    
    def upload_file(self, file_path, matter_id=None, name=None):
        """
        Upload a file to Clio
        
        Args:
            file_path: Path to the file to upload
            matter_id: Optional ID of the matter to attach the file to
            name: Optional custom name for the file
            
        Returns:
            Response from Clio API
        """
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_name = name or os.path.basename(file_path)
        
        print(f"\nUploading file: {file_name}")
        print(f"Size: {file_size / 1024:.2f} KB")
        
        try:
            # Upload to Clio using the documents endpoint
            # Based on clio-manage-api-client documentation
            # The file must remain open during the API call, so we use it within the with context
            with open(file_path, 'rb') as f:
                # The API expects the file as a parameter along with metadata
                upload_params = {
                    'name': file_name,
                    'file': f  # File object passed directly; SDK reads it during the API call
                }
                
                # Add matter_id if provided
                if matter_id:
                    upload_params['matter_id'] = matter_id
                
                # Upload document using POST method
                # The API call happens here while the file is still open
                response = self.client.post.documents(**upload_params)
            
            # File is automatically closed after this point
            return response
            
        except Exception as e:
            raise Exception(f"Upload failed: {e}")
    
    def list_recent_documents(self, limit=10):
        """
        List recent documents in Clio
        
        Args:
            limit: Maximum number of documents to retrieve
            
        Returns:
            List of documents
        """
        try:
            documents = self.client.get.documents(limit=limit)
            return documents.get('data', [])
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []


def select_file_interactive():
    """
    Interactively select a file from the current directory
    
    Returns:
        Path to selected file or None
    """
    print("\n" + "="*60)
    print("File Selection")
    print("="*60)
    
    # Option 1: Enter file path directly
    print("\nOption 1: Enter the full path to your file")
    print("Option 2: Press Enter to see files in current directory")
    
    choice = input("\nYour choice (or press Enter for Option 2): ").strip()
    
    if choice:
        if os.path.exists(choice):
            return choice
        else:
            print(f"Error: File not found: {choice}")
            return None
    
    # Show files in current directory
    current_dir = os.getcwd()
    files = [f for f in os.listdir(current_dir) if os.path.isfile(f)]
    
    if not files:
        print(f"No files found in {current_dir}")
        return None
    
    # Filter out hidden files and Python cache
    files = [f for f in files if not f.startswith('.') and not f.endswith('.pyc')]
    files.sort()
    
    print(f"\nFiles in {current_dir}:")
    print("-" * 60)
    
    for i, file in enumerate(files, 1):
        file_size = os.path.getsize(file)
        print(f"{i:3}. {file:40} ({file_size / 1024:>8.2f} KB)")
    
    print("-" * 60)
    
    try:
        selection = input("\nEnter file number (or 'q' to quit): ").strip()
        
        if selection.lower() == 'q':
            return None
        
        file_index = int(selection) - 1
        
        if 0 <= file_index < len(files):
            return files[file_index]
        else:
            print("Invalid selection")
            return None
            
    except ValueError:
        print("Invalid input")
        return None


def main():
    """
    Main function - CLI interface for Clio file upload
    """
    parser = argparse.ArgumentParser(
        description='Upload files to Clio.com',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a file interactively
  python clio_upload.py

  # Upload a specific file
  python clio_upload.py --file /path/to/document.pdf

  # Upload and attach to a specific matter
  python clio_upload.py --file document.pdf --matter 12345

  # List recent documents
  python clio_upload.py --list-documents

  # List matters
  python clio_upload.py --list-matters
        """
    )
    
    parser.add_argument('--file', '-f', help='Path to file to upload')
    parser.add_argument('--matter', '-m', help='Matter ID to attach file to')
    parser.add_argument('--name', '-n', help='Custom name for the file in Clio')
    parser.add_argument('--config', '-c', default='.clio-config.json', 
                       help='Path to Clio config file (default: .clio-config.json)')
    parser.add_argument('--list-documents', action='store_true',
                       help='List recent documents')
    parser.add_argument('--list-matters', action='store_true',
                       help='List recent matters')
    
    args = parser.parse_args()
    
    # Print banner
    print("\n" + "="*60)
    print("Clio File Upload Utility")
    print("="*60)
    
    # Initialize uploader
    try:
        uploader = ClioFileUploader(config_path=args.config)
    except Exception as e:
        print(f"Failed to initialize: {e}")
        sys.exit(1)
    
    # List documents
    if args.list_documents:
        print("\nRecent Documents:")
        print("-" * 60)
        documents = uploader.list_recent_documents(limit=10)
        if documents:
            for doc in documents:
                print(f"- {doc.get('name', 'Unnamed')} (ID: {doc.get('id')})")
        else:
            print("No documents found or unable to fetch")
        return
    
    # List matters
    if args.list_matters:
        print("\nRecent Matters:")
        print("-" * 60)
        matters = uploader.get_matters(limit=10)
        if matters:
            for matter in matters:
                print(f"- {matter.get('display_number', 'N/A')}: {matter.get('description', 'Unnamed')} (ID: {matter.get('id')})")
        else:
            print("No matters found or unable to fetch")
        return
    
    # Get file path
    file_path = args.file
    
    if not file_path:
        # Interactive file selection
        file_path = select_file_interactive()
        
        if not file_path:
            print("\nNo file selected. Exiting.")
            return
    
    # Validate file
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Get matter ID if needed
    matter_id = args.matter
    
    if not matter_id:
        attach_to_matter = input("\nDo you want to attach this file to a matter? (y/n): ").strip().lower()
        
        if attach_to_matter == 'y':
            matters = uploader.get_matters(limit=20)
            
            if matters:
                print("\nAvailable Matters:")
                print("-" * 60)
                for i, matter in enumerate(matters, 1):
                    print(f"{i}. {matter.get('display_number', 'N/A')}: {matter.get('description', 'Unnamed')}")
                print("-" * 60)
                
                matter_choice = input("\nEnter matter number (or press Enter to skip): ").strip()
                
                if matter_choice:
                    try:
                        matter_index = int(matter_choice) - 1
                        if 0 <= matter_index < len(matters):
                            matter_id = matters[matter_index].get('id')
                            print(f"Selected matter: {matters[matter_index].get('description', 'Unnamed')}")
                    except ValueError:
                        print("Invalid input, continuing without matter attachment")
    
    # Confirm upload
    print("\n" + "="*60)
    print("Upload Summary")
    print("="*60)
    print(f"File: {file_path}")
    print(f"Name in Clio: {args.name or os.path.basename(file_path)}")
    print(f"Attach to Matter: {matter_id or 'No'}")
    print("="*60)
    
    confirm = input("\nProceed with upload? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Upload cancelled.")
        return
    
    # Upload file
    try:
        print("\nUploading...")
        response = uploader.upload_file(
            file_path=file_path,
            matter_id=matter_id,
            name=args.name
        )
        
        print("\n✓ Upload successful!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"\n✗ Upload failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
