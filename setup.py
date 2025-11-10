"""
Setup script for Remembrance application.
Creates necessary directories and initializes the environment.
"""
import os
import sys


def create_directories():
    """Create necessary data directories."""
    directories = [
        'data',
        'data/entries',
        'data/entries/2025',
        'data/summaries',
        'data/summaries/2025',
        'data/embeddings',
        'data/temp',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists('.env'):
        print("\n⚠️  Warning: .env file not found!")
        print("Please copy .env.example to .env and add your OpenAI API key")
        return False
    return True


def main():
    """Main setup function."""
    print("=" * 60)
    print("Remembrance - Voice Journaling Application Setup")
    print("=" * 60)
    print()
    
    # Create directories
    print("Creating data directories...")
    create_directories()
    print()
    
    # Check .env file
    print("Checking environment configuration...")
    if check_env_file():
        print("✓ .env file found")
    print()
    
    # Installation instructions
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Add your OpenAI API key to .env file")
    print("3. Run the application: python run.py")
    print("4. Open your browser to http://localhost:5000")
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
