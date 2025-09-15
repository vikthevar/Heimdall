#!/usr/bin/env python3
"""
Database operations for message storage and retrieval
Simple SQLite-based storage for conversation history
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = "data/heimdall.db"

def _ensure_db_exists():
    """Ensure database directory and file exist"""
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # Create database and tables if they don't exist
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    intent_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to ensure database exists: {e}")

def save_message(user_msg: str, assistant_msg: str, intent: Optional[Dict[str, Any]] = None) -> Optional[int]:
    """
    Save a conversation message to the database
    
    Args:
        user_msg: User's input message
        assistant_msg: Assistant's response message
        intent: Optional intent data dictionary
        
    Returns:
        Message ID if successful, None if failed
    """
    try:
        _ensure_db_exists()
        
        timestamp = datetime.now().isoformat()
        intent_json = json.dumps(intent) if intent else None
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                INSERT INTO messages (timestamp, user_message, assistant_message, intent_data)
                VALUES (?, ?, ?, ?)
            """, (timestamp, user_msg, assistant_msg, intent_json))
            
            conn.commit()
            message_id = cursor.lastrowid
            
            logger.debug(f"Saved message with ID: {message_id}")
            return message_id
    
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        return None

def load_recent_messages(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Load recent conversation messages from the database
    
    Args:
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of message dictionaries
    """
    try:
        _ensure_db_exists()
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            
            cursor = conn.execute("""
                SELECT id, timestamp, user_message, assistant_message, intent_data, created_at
                FROM messages
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            messages = []
            for row in cursor.fetchall():
                intent_data = None
                if row['intent_data']:
                    try:
                        intent_data = json.loads(row['intent_data'])
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse intent data for message {row['id']}")
                
                messages.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'user_message': row['user_message'],
                    'assistant_message': row['assistant_message'],
                    'intent': intent_data,
                    'created_at': row['created_at']
                })
            
            # Reverse to get chronological order (oldest first)
            messages.reverse()
            
            logger.debug(f"Loaded {len(messages)} recent messages")
            return messages
    
    except Exception as e:
        logger.error(f"Failed to load recent messages: {e}")
        return []

def get_message_count() -> int:
    """Get total number of messages in database"""
    try:
        _ensure_db_exists()
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            count = cursor.fetchone()[0]
            return count
    
    except Exception as e:
        logger.error(f"Failed to get message count: {e}")
        return 0

def clear_all_messages() -> bool:
    """Clear all messages from database (use with caution)"""
    try:
        _ensure_db_exists()
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM messages")
            conn.commit()
            
        logger.info("All messages cleared from database")
        return True
    
    except Exception as e:
        logger.error(f"Failed to clear messages: {e}")
        return False

def search_messages(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search messages by text content
    
    Args:
        query: Search query string
        limit: Maximum number of results
        
    Returns:
        List of matching message dictionaries
    """
    try:
        _ensure_db_exists()
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT id, timestamp, user_message, assistant_message, intent_data, created_at
                FROM messages
                WHERE user_message LIKE ? OR assistant_message LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', limit))
            
            messages = []
            for row in cursor.fetchall():
                intent_data = None
                if row['intent_data']:
                    try:
                        intent_data = json.loads(row['intent_data'])
                    except json.JSONDecodeError:
                        pass
                
                messages.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'user_message': row['user_message'],
                    'assistant_message': row['assistant_message'],
                    'intent': intent_data,
                    'created_at': row['created_at']
                })
            
            logger.debug(f"Found {len(messages)} messages matching '{query}'")
            return messages
    
    except Exception as e:
        logger.error(f"Failed to search messages: {e}")
        return []

# Test function
if __name__ == "__main__":
    # Test database operations
    print("🧪 Testing Database Operations...")
    
    # Test save message
    msg_id = save_message(
        "Hello, can you help me?",
        "Of course! I'm here to help you with screen control and automation.",
        {'type': 'greeting', 'confidence': 0.9}
    )
    print(f"Saved message with ID: {msg_id}")
    
    # Test load recent messages
    recent = load_recent_messages(5)
    print(f"Loaded {len(recent)} recent messages")
    
    # Test message count
    count = get_message_count()
    print(f"Total messages in database: {count}")
    
    # Test search
    results = search_messages("help")
    print(f"Found {len(results)} messages containing 'help'")
    
    print("✅ Database tests completed!")