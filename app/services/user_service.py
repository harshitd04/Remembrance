"""
User management service for multi-user journal support.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Handle user management and data directory structure."""
    
    def __init__(self, base_dir: str = './data'):
        """
        Initialize user service.
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = Path(base_dir)
        self.users_file = self.base_dir / 'users.json'
        
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize users file if it doesn't exist
        if not self.users_file.exists():
            self._initialize_users_file()
    
    def _initialize_users_file(self) -> None:
        """Initialize users.json with Harshit as default user."""
        default_users = {
            "users": ["harshit"],
            "created_at": "2024-01-01T00:00:00"
        }
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, indent=2)
        
        # Create Harshit user directory structure
        self._create_user_directories("harshit")
        
        logger.info("Initialized users file with Harshit as default user")
    
    def get_all_users(self) -> List[str]:
        """
        Get list of all users.
        
        Returns:
            List of user names
        """
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('users', [])
        except Exception as e:
            logger.error(f"Error loading users: {str(e)}", exc_info=True)
            return []
    
    def add_user(self, username: str) -> bool:
        """
        Add a new user and create their directory structure.
        
        Args:
            username: Name of the user to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate username
            if not username or not username.strip():
                logger.error("Invalid username: empty")
                return False
            
            username = username.strip().lower()
            
            # Check if user already exists
            users = self.get_all_users()
            if username in users:
                logger.warning(f"User already exists: {username}")
                return False
            
            # Add user to list
            users.append(username)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({"users": users}, f, indent=2)
            
            # Create user directories
            self._create_user_directories(username)
            
            logger.info(f"Added new user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding user: {str(e)}", exc_info=True)
            return False
    
    def delete_user(self, username: str, delete_data: bool = True) -> bool:
        """
        Delete a user and optionally their data directory.
        
        Args:
            username: Name of the user to delete
            delete_data: Whether to delete the user's data folder (default: True)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            users = self.get_all_users()
            
            if username not in users:
                logger.warning(f"User not found: {username}")
                return False
            
            # Don't allow deleting the last user
            if len(users) == 1:
                logger.error("Cannot delete the last user")
                return False
            
            # Remove from users list
            users.remove(username)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({"users": users}, f, indent=2)
            
            # Delete user's data folder if requested
            if delete_data:
                import shutil
                user_dir = self.base_dir / username
                if user_dir.exists():
                    shutil.rmtree(user_dir)
                    logger.info(f"Deleted data folder for user: {username}")
            
            logger.info(f"Deleted user: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}", exc_info=True)
            return False
    
    def user_exists(self, username: str) -> bool:
        """
        Check if a user exists.
        
        Args:
            username: Name of the user to check
            
        Returns:
            True if user exists, False otherwise
        """
        return username in self.get_all_users()
    
    def _create_user_directories(self, username: str) -> None:
        """
        Create directory structure for a user.
        
        Args:
            username: Name of the user
        """
        user_dir = self.base_dir / username
        
        # Create subdirectories
        (user_dir / 'entries').mkdir(parents=True, exist_ok=True)
        (user_dir / 'embeddings').mkdir(parents=True, exist_ok=True)
        (user_dir / 'summaries').mkdir(parents=True, exist_ok=True)
        (user_dir / 'temp').mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created directory structure for user: {username}")
    
    def get_user_data_path(self, username: str) -> Optional[Path]:
        """
        Get the data directory path for a user.
        
        Args:
            username: Name of the user
            
        Returns:
            Path to user's data directory or None if user doesn't exist
        """
        if not self.user_exists(username):
            return None
        
        return self.base_dir / username
