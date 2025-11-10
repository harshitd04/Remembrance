"""
JSON file storage service for journal entries, embeddings, and summaries.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class JSONStorageService:
    """Handle all JSON file operations with atomic writes."""
    
    def __init__(self, base_dir: str = './data', username: str = 'harshit'):
        """
        Initialize storage service.
        
        Args:
            base_dir: Base directory for data storage
            username: Username for user-specific data storage
        """
        self.base_dir = Path(base_dir)
        self.username = username
        
        # User-specific directories
        user_dir = self.base_dir / username
        self.entries_dir = user_dir / 'entries'
        self.summaries_dir = user_dir / 'summaries'
        self.embeddings_dir = user_dir / 'embeddings'
        
        # Ensure directories exist
        self.entries_dir.mkdir(parents=True, exist_ok=True)
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    def save_entry(self, date: str, entry: Dict, is_append: bool = False) -> bool:
        """
        Save journal entry to JSON file.
        
        Args:
            date: ISO format date (YYYY-MM-DD)
            entry: Entry dictionary with id, content, type, created_at
            is_append: Whether to append to existing entry
            
        Returns:
            True if successful, False otherwise
        """
        try:
            date_obj = datetime.fromisoformat(date)
            year = date_obj.year
            month = date_obj.strftime('%B').lower()
            
            # Create year directory if needed
            year_dir = self.entries_dir / str(year)
            year_dir.mkdir(exist_ok=True)
            
            # File path
            file_path = year_dir / f"{month}_entries.json"
            
            # Load existing data
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Add or append entry
            if date not in data:
                data[date] = []
            
            data[date].append(entry)
            
            # Atomic write
            self._atomic_write(file_path, data)
            
            logger.info(f"Entry saved for date {date}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving entry: {str(e)}", exc_info=True)
            return False
    
    def load_entry_by_date(self, date: str) -> Optional[List[Dict]]:
        """
        Load entries for a specific date.
        
        Args:
            date: ISO format date (YYYY-MM-DD)
            
        Returns:
            List of entries or None if not found
        """
        try:
            date_obj = datetime.fromisoformat(date)
            year = date_obj.year
            month = date_obj.strftime('%B').lower()
            
            file_path = self.entries_dir / str(year) / f"{month}_entries.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get(date)
            
        except Exception as e:
            logger.error(f"Error loading entry: {str(e)}", exc_info=True)
            return None
    
    def load_all_entries(self) -> Dict[str, List[Dict]]:
        """
        Load all journal entries from all files.
        
        Returns:
            Dictionary mapping dates to entry lists
        """
        all_entries = {}
        
        try:
            for year_dir in self.entries_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                
                for file_path in year_dir.glob('*_entries.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_entries.update(data)
            
            return all_entries
            
        except Exception as e:
            logger.error(f"Error loading all entries: {str(e)}", exc_info=True)
            return {}
    
    def delete_entry(self, date: str, entry_id: Optional[str] = None) -> bool:
        """
        Delete entry for a specific date.
        
        Args:
            date: ISO format date (YYYY-MM-DD)
            entry_id: Optional specific entry ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            date_obj = datetime.fromisoformat(date)
            year = date_obj.year
            month = date_obj.strftime('%B').lower()
            
            file_path = self.entries_dir / str(year) / f"{month}_entries.json"
            
            if not file_path.exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if date not in data:
                return False
            
            if entry_id:
                # Delete specific entry
                data[date] = [e for e in data[date] if e['id'] != entry_id]
                if not data[date]:
                    del data[date]
                # Also delete the embedding for this entry
                self._delete_embedding(entry_id, year)
            else:
                # Delete all entries for date
                entry_ids = [e['id'] for e in data[date]]
                del data[date]
                # Delete embeddings for all entries on this date
                for eid in entry_ids:
                    self._delete_embedding(eid, year)
            
            self._atomic_write(file_path, data)
            
            logger.info(f"Entry deleted for date {date}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting entry: {str(e)}", exc_info=True)
            return False
    
    def save_embedding(self, entry_id: str, embedding: List[float], 
                      date: str, text_preview: str) -> bool:
        """
        Save embedding for an entry.
        
        Args:
            entry_id: Unique entry identifier
            embedding: Embedding vector
            date: ISO format date
            text_preview: First 100 chars of text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            year = datetime.fromisoformat(date).year
            file_path = self.embeddings_dir / f"{year}_embeddings.json"
            
            # Load existing embeddings
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Add new embedding
            data[entry_id] = {
                'embedding': embedding,
                'entry_id': entry_id,
                'date': date,
                'text_preview': text_preview[:100]
            }
            
            self._atomic_write(file_path, data)
            
            logger.info(f"Embedding saved for entry {entry_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving embedding: {str(e)}", exc_info=True)
            return False
    
    def load_all_embeddings(self, year: Optional[int] = None) -> Dict:
        """
        Load all embeddings, optionally filtered by year.
        
        Args:
            year: Optional year to filter by
            
        Returns:
            Dictionary of embeddings
        """
        all_embeddings = {}
        
        try:
            if year:
                file_path = self.embeddings_dir / f"{year}_embeddings.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        all_embeddings = json.load(f)
            else:
                for file_path in self.embeddings_dir.glob('*_embeddings.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_embeddings.update(data)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {str(e)}", exc_info=True)
            return {}
    
    def _delete_embedding(self, entry_id: str, year: int) -> None:
        """
        Delete embedding for a specific entry.
        
        Args:
            entry_id: Entry ID to delete embedding for
            year: Year of the embedding file
        """
        try:
            file_path = self.embeddings_dir / f"{year}_embeddings.json"
            
            if not file_path.exists():
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if entry_id in data:
                del data[entry_id]
                self._atomic_write(file_path, data)
                logger.info(f"Embedding deleted for entry {entry_id}")
        except Exception as e:
            logger.warning(f"Error deleting embedding: {str(e)}")
    
    def save_summary(self, summary_type: str, period_id: str, summary_data: Dict) -> bool:
        """
        Save a summary to storage.
        
        Args:
            summary_type: Type of summary ('weekly', 'monthly', 'yearly')
            period_id: Identifier for the period (e.g., '2024_46' for week 46 of 2024)
            summary_data: Summary data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.summaries_dir / f"{summary_type}_summaries.json"
            
            # Load existing summaries
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            # Add/update summary
            data[period_id] = summary_data
            
            self._atomic_write(file_path, data)
            
            logger.info(f"{summary_type.capitalize()} summary saved for {period_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving summary: {str(e)}", exc_info=True)
            return False
    
    def load_summary(self, summary_type: str, period_id: str) -> Optional[Dict]:
        """
        Load a summary from storage.
        
        Args:
            summary_type: Type of summary ('weekly', 'monthly', 'yearly')
            period_id: Identifier for the period
            
        Returns:
            Summary data or None if not found
        """
        try:
            file_path = self.summaries_dir / f"{summary_type}_summaries.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get(period_id)
            
        except Exception as e:
            logger.error(f"Error loading summary: {str(e)}", exc_info=True)
            return None
    
    def delete_summary(self, summary_type: str, period_id: str) -> bool:
        """
        Delete a summary from storage.
        
        Args:
            summary_type: Type of summary ('weekly', 'monthly', 'yearly')
            period_id: Identifier for the period
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.summaries_dir / f"{summary_type}_summaries.json"
            
            if not file_path.exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if period_id in data:
                del data[period_id]
                self._atomic_write(file_path, data)
                logger.info(f"{summary_type.capitalize()} summary deleted for {period_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting summary: {str(e)}", exc_info=True)
            return False
    
    def _atomic_write(self, file_path: Path, data: Dict) -> None:
        """
        Perform atomic write to prevent data corruption.
        
        Args:
            file_path: Path to file
            data: Data to write
        """
        temp_path = file_path.with_suffix('.tmp')
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic rename
        temp_path.replace(file_path)
