#!/usr/bin/env python3
"""
Settings Manager - Persistent user settings with database storage
Handles user preferences, configuration, and defaults
"""
import sqlite3
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SettingsManager:
    """Manages user settings with SQLite persistence"""
    
    # Default settings
    DEFAULT_SETTINGS = {
        'simulation_mode': True,
        'voice_output_enabled': True,
        'voice_input_enabled': True,
        'demo_safe_mode': True,
        'auto_analyze_ocr': True,
        'whisper_model_size': 'base',
        'tts_rate': 150,
        'tts_volume': 0.8,
        'max_recording_duration': 8,
        'auto_send_transcript': True,
        'theme': 'dark',
        'window_width': 1000,
        'window_height': 800,
        'debug_mode': False,
        'log_level': 'INFO'
    }
    
    def __init__(self, db_path: str = "data/heimdall.db"):
        self.db_path = db_path
        self.settings_cache = {}
        self._ensure_db_exists()
        self._load_settings()
    
    def _ensure_db_exists(self):
        """Ensure database and settings table exist"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                # Create settings table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        value_type TEXT NOT NULL,
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create settings history table for audit trail
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS settings_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT NOT NULL,
                        old_value TEXT,
                        new_value TEXT NOT NULL,
                        changed_by TEXT DEFAULT 'user',
                        changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to ensure settings database: {e}")
    
    def _load_settings(self):
        """Load all settings from database into cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT key, value, value_type FROM settings")
                
                for key, value_str, value_type in cursor.fetchall():
                    try:
                        # Convert string back to appropriate type
                        if value_type == 'bool':
                            value = value_str.lower() == 'true'
                        elif value_type == 'int':
                            value = int(value_str)
                        elif value_type == 'float':
                            value = float(value_str)
                        elif value_type == 'json':
                            value = json.loads(value_str)
                        else:  # str
                            value = value_str
                        
                        self.settings_cache[key] = value
                        
                    except (ValueError, json.JSONDecodeError) as e:
                        logger.warning(f"Failed to parse setting {key}: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
        
        # Ensure all default settings exist
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        """Ensure all default settings exist in cache and database"""
        for key, default_value in self.DEFAULT_SETTINGS.items():
            if key not in self.settings_cache:
                self.set(key, default_value, save_to_db=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return self.settings_cache.get(key, default)
    
    def set(self, key: str, value: Any, save_to_db: bool = True, description: str = None) -> bool:
        """Set setting value"""
        try:
            old_value = self.settings_cache.get(key)
            self.settings_cache[key] = value
            
            if save_to_db:
                self._save_to_db(key, value, old_value, description)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")
            return False
    
    def _save_to_db(self, key: str, value: Any, old_value: Any = None, description: str = None):
        """Save setting to database"""
        try:
            # Determine value type and convert to string
            if isinstance(value, bool):
                value_str = str(value).lower()
                value_type = 'bool'
            elif isinstance(value, int):
                value_str = str(value)
                value_type = 'int'
            elif isinstance(value, float):
                value_str = str(value)
                value_type = 'float'
            elif isinstance(value, (dict, list)):
                value_str = json.dumps(value)
                value_type = 'json'
            else:
                value_str = str(value)
                value_type = 'str'
            
            with sqlite3.connect(self.db_path) as conn:
                # Insert or update setting
                conn.execute("""
                    INSERT OR REPLACE INTO settings (key, value, value_type, description, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (key, value_str, value_type, description, datetime.now().isoformat()))
                
                # Log to history
                if old_value is not None:
                    old_value_str = json.dumps(old_value) if isinstance(old_value, (dict, list)) else str(old_value)
                    conn.execute("""
                        INSERT INTO settings_history (key, old_value, new_value)
                        VALUES (?, ?, ?)
                    """, (key, old_value_str, value_str))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save setting {key} to database: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.settings_cache.copy()
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            logger.info("Resetting all settings to defaults")
            
            # Clear cache and reload defaults
            self.settings_cache.clear()
            
            # Clear database settings (keep history)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM settings")
                conn.commit()
            
            # Reload defaults
            self._ensure_defaults()
            
            logger.info("Settings reset to defaults successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset settings: {e}")
            return False
    
    def reset_setting(self, key: str) -> bool:
        """Reset specific setting to default"""
        if key in self.DEFAULT_SETTINGS:
            return self.set(key, self.DEFAULT_SETTINGS[key])
        return False
    
    def export_settings(self, file_path: str) -> bool:
        """Export settings to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.settings_cache, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Import settings from JSON file"""
        try:
            with open(file_path, 'r') as f:
                imported_settings = json.load(f)
            
            for key, value in imported_settings.items():
                self.set(key, value)
            
            return True
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False
    
    def get_settings_history(self, key: str = None, limit: int = 50) -> list:
        """Get settings change history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if key:
                    cursor = conn.execute("""
                        SELECT * FROM settings_history 
                        WHERE key = ? 
                        ORDER BY changed_at DESC 
                        LIMIT ?
                    """, (key, limit))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM settings_history 
                        ORDER BY changed_at DESC 
                        LIMIT ?
                    """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to get settings history: {e}")
            return []
    
    def validate_setting(self, key: str, value: Any) -> tuple[bool, str]:
        """Validate setting value"""
        # Define validation rules
        validations = {
            'whisper_model_size': lambda v: v in ['tiny', 'base', 'small', 'medium', 'large'],
            'tts_rate': lambda v: isinstance(v, (int, float)) and 50 <= v <= 300,
            'tts_volume': lambda v: isinstance(v, (int, float)) and 0.0 <= v <= 1.0,
            'max_recording_duration': lambda v: isinstance(v, int) and 1 <= v <= 30,
            'window_width': lambda v: isinstance(v, int) and v >= 800,
            'window_height': lambda v: isinstance(v, int) and v >= 600,
            'log_level': lambda v: v in ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        }
        
        if key in validations:
            if validations[key](value):
                return True, "Valid"
            else:
                return False, f"Invalid value for {key}"
        
        return True, "Valid"  # No validation rule, assume valid

# Global settings manager instance
settings_manager = SettingsManager()

# Convenience functions
def get_setting(key: str, default: Any = None) -> Any:
    """Get setting value"""
    return settings_manager.get(key, default)

def set_setting(key: str, value: Any, description: str = None) -> bool:
    """Set setting value"""
    return settings_manager.set(key, value, description=description)

def reset_settings() -> bool:
    """Reset all settings to defaults"""
    return settings_manager.reset_to_defaults()

# Test function
if __name__ == "__main__":
    # Test settings manager
    print("🧪 Testing Settings Manager...")
    
    # Test basic operations
    settings_manager.set('test_setting', 'test_value')
    assert settings_manager.get('test_setting') == 'test_value'
    
    # Test different types
    settings_manager.set('test_bool', True)
    settings_manager.set('test_int', 42)
    settings_manager.set('test_float', 3.14)
    settings_manager.set('test_dict', {'key': 'value'})
    
    assert settings_manager.get('test_bool') is True
    assert settings_manager.get('test_int') == 42
    assert settings_manager.get('test_float') == 3.14
    assert settings_manager.get('test_dict') == {'key': 'value'}
    
    # Test validation
    valid, msg = settings_manager.validate_setting('tts_rate', 150)
    assert valid, f"Validation failed: {msg}"
    
    valid, msg = settings_manager.validate_setting('tts_rate', 500)
    assert not valid, "Validation should have failed"
    
    print("✅ Settings Manager tests passed!")