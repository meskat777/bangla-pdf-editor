"""
Session Manager Module
Handles persistent session storage using file-based approach
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages user sessions with file-based persistence.
    Sessions are stored as JSON files in the sessions folder.
    """
    
    def __init__(self, session_folder='sessions'):
        """
        Initialize SessionManager.
        
        Args:
            session_folder (str): Directory to store session files
        """
        self.session_folder = session_folder
        os.makedirs(session_folder, exist_ok=True)
        logger.info(f"SessionManager initialized with folder: {session_folder}")
    
    def _get_filepath(self, session_id: str) -> str:
        """Get file path for a session ID"""
        return os.path.join(self.session_folder, f'{session_id}.json')
    
    def save(self, session_id: str, data: Dict[Any, Any]) -> bool:
        """
        Save session data to file.
        
        Args:
            session_id (str): Unique session identifier
            data (dict): Session data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            filepath = self._get_filepath(session_id)
            
            # Add metadata
            data['session_id'] = session_id
            data['last_updated'] = datetime.now().isoformat()
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Session saved: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}", exc_info=True)
            return False
    
    def load(self, session_id: str) -> Optional[Dict[Any, Any]]:
        """
        Load session data from file.
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            dict or None: Session data if exists, None otherwise
        """
        try:
            filepath = self._get_filepath(session_id)
            
            if not os.path.exists(filepath):
                logger.warning(f"Session not found: {session_id}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Session loaded: {session_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}", exc_info=True)
            return None
    
    def exists(self, session_id: str) -> bool:
        """
        Check if session exists.
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            bool: True if session exists, False otherwise
        """
        filepath = self._get_filepath(session_id)
        exists = os.path.exists(filepath)
        
        if exists:
            # Check if session is expired
            try:
                mtime = os.path.getmtime(filepath)
                age_hours = (datetime.now().timestamp() - mtime) / 3600
                
                # Session expires after 24 hours
                if age_hours > 24:
                    logger.info(f"Session expired (age: {age_hours:.1f}h): {session_id}")
                    self.delete(session_id)
                    return False
            except:
                pass
        
        return exists
    
    def delete(self, session_id: str) -> bool:
        """
        Delete session.
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            filepath = self._get_filepath(session_id)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Session deleted: {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}", exc_info=True)
            return False
    
    def update(self, session_id: str, updates: Dict[Any, Any]) -> bool:
        """
        Update session data (merge with existing).
        
        Args:
            session_id (str): Unique session identifier
            updates (dict): Data to update/merge
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load existing data
            data = self.load(session_id)
            
            if data is None:
                logger.warning(f"Cannot update non-existent session: {session_id}")
                return False
            
            # Merge updates
            data.update(updates)
            
            # Save updated data
            return self.save(session_id, data)
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}", exc_info=True)
            return False
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Delete sessions older than max_age_hours.
        
        Args:
            max_age_hours (int): Maximum age in hours
            
        Returns:
            int: Number of sessions deleted
        """
        try:
            cutoff = datetime.now() - timedelta(hours=max_age_hours)
            cutoff_timestamp = cutoff.timestamp()
            
            deleted_count = 0
            
            for filename in os.listdir(self.session_folder):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.session_folder, filename)
                    
                    try:
                        # Check file modification time
                        mtime = os.path.getmtime(filepath)
                        
                        if mtime < cutoff_timestamp:
                            os.remove(filepath)
                            deleted_count += 1
                            logger.info(f"Deleted old session: {filename}")
                    
                    except Exception as e:
                        logger.warning(f"Error checking {filename}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleanup complete: {deleted_count} sessions deleted")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
            return 0
    
    def list_sessions(self) -> list:
        """
        Get list of all active session IDs.
        
        Returns:
            list: List of session IDs
        """
        try:
            sessions = []
            
            for filename in os.listdir(self.session_folder):
                if filename.endswith('.json'):
                    session_id = filename[:-5]  # Remove .json
                    sessions.append(session_id)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error listing sessions: {e}", exc_info=True)
            return []
    
    def get_session_count(self) -> int:
        """
        Get total number of active sessions.
        
        Returns:
            int: Number of sessions
        """
        return len(self.list_sessions())
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session metadata without loading full data.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            dict: Session info (filename, size, modified time) or None
        """
        try:
            filepath = self._get_filepath(session_id)
            
            if not os.path.exists(filepath):
                return None
            
            stat = os.stat(filepath)
            
            return {
                'session_id': session_id,
                'file_size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'age_hours': (datetime.now().timestamp() - stat.st_mtime) / 3600
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}", exc_info=True)
            return None
