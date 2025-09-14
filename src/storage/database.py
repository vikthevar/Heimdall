"""
Free local database using SQLite
"""
import asyncio
import aiosqlite
import json
from datetime import datetime
from loguru import logger
from typing import Dict, Any, List, Optional
import os


class LocalDatabase:
    def __init__(self, db_path: str = "./data/heimdall.db"):
        """Initialize SQLite database"""
        self.db_path = db_path
        self.ensure_directory()
    
    def ensure_directory(self):
        """Create database directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    async def initialize(self):
        """Create database tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Commands history table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS commands (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        parsed_intent TEXT,
                        action_taken TEXT,
                        success BOOLEAN,
                        response_text TEXT,
                        screen_context TEXT
                    )
                """)
                
                # User preferences table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # Screenshots metadata table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS screenshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        filepath TEXT NOT NULL,
                        analysis_data TEXT,
                        command_id INTEGER,
                        FOREIGN KEY (command_id) REFERENCES commands (id)
                    )
                """)
                
                await db.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    async def log_command(self, user_input: str, parsed_intent: Dict[str, Any] = None,
                         action_taken: str = None, success: bool = None,
                         response_text: str = None, screen_context: str = None) -> int:
        """Log a user command and its execution"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO commands 
                    (timestamp, user_input, parsed_intent, action_taken, success, response_text, screen_context)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    user_input,
                    json.dumps(parsed_intent) if parsed_intent else None,
                    action_taken,
                    success,
                    response_text,
                    screen_context
                ))
                
                command_id = cursor.lastrowid
                await db.commit()
                
                logger.info(f"Command logged with ID: {command_id}")
                return command_id
                
        except Exception as e:
            logger.error(f"Command logging error: {e}")
            return -1
    
    async def log_screenshot(self, filepath: str, analysis_data: Dict[str, Any] = None,
                           command_id: int = None) -> int:
        """Log screenshot metadata"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO screenshots (timestamp, filepath, analysis_data, command_id)
                    VALUES (?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    filepath,
                    json.dumps(analysis_data) if analysis_data else None,
                    command_id
                ))
                
                screenshot_id = cursor.lastrowid
                await db.commit()
                
                return screenshot_id
                
        except Exception as e:
            logger.error(f"Screenshot logging error: {e}")
            return -1
    
    async def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commands from history"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                async with db.execute("""
                    SELECT * FROM commands 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,)) as cursor:
                    
                    rows = await cursor.fetchall()
                    commands = []
                    
                    for row in rows:
                        command = dict(row)
                        if command['parsed_intent']:
                            command['parsed_intent'] = json.loads(command['parsed_intent'])
                        commands.append(command)
                    
                    return commands
                    
        except Exception as e:
            logger.error(f"Error getting recent commands: {e}")
            return []
    
    async def set_preference(self, key: str, value: Any):
        """Set user preference"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO preferences (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, json.dumps(value), datetime.now().isoformat()))
                
                await db.commit()
                logger.info(f"Preference set: {key}")
                
        except Exception as e:
            logger.error(f"Error setting preference: {e}")
    
    async def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT value FROM preferences WHERE key = ?
                """, (key,)) as cursor:
                    
                    row = await cursor.fetchone()
                    if row:
                        return json.loads(row[0])
                    else:
                        return default
                        
        except Exception as e:
            logger.error(f"Error getting preference: {e}")
            return default
    
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data to save space"""
        try:
            cutoff_date = datetime.now().replace(day=datetime.now().day - days)
            cutoff_str = cutoff_date.isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                # Clean old commands
                cursor = await db.execute("""
                    DELETE FROM commands WHERE timestamp < ?
                """, (cutoff_str,))
                commands_deleted = cursor.rowcount
                
                # Clean old screenshots
                cursor = await db.execute("""
                    DELETE FROM screenshots WHERE timestamp < ?
                """, (cutoff_str,))
                screenshots_deleted = cursor.rowcount
                
                await db.commit()
                
                logger.info(f"Cleaned up {commands_deleted} commands and {screenshots_deleted} screenshots")
                
        except Exception as e:
            logger.error(f"Data cleanup error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Count commands
                async with db.execute("SELECT COUNT(*) FROM commands") as cursor:
                    commands_count = (await cursor.fetchone())[0]
                
                # Count screenshots
                async with db.execute("SELECT COUNT(*) FROM screenshots") as cursor:
                    screenshots_count = (await cursor.fetchone())[0]
                
                # Count preferences
                async with db.execute("SELECT COUNT(*) FROM preferences") as cursor:
                    preferences_count = (await cursor.fetchone())[0]
                
                return {
                    "commands": commands_count,
                    "screenshots": screenshots_count,
                    "preferences": preferences_count
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"commands": 0, "screenshots": 0, "preferences": 0}