"""
Settings bridge for original signalhub code to read from database
"""
import os
import logging
from typing import Optional, Dict, Any
from sqlmodel import Session, create_engine
from .api.settings_service import SettingsService
from .api.models import Setting

# Database connection (same as API)
DATABASE_URL = "sqlite:///./signalhub.db"
engine = create_engine(DATABASE_URL)

def get_db_settings() -> Dict[str, Any]:
    """Get all settings from database for use by original signalhub code"""
    try:
        with Session(engine) as session:
            service = SettingsService(session)
            
            # Get all settings
            smtp_settings = service.get_smtp_settings()
            pushover_settings = service.get_pushover_settings()
            app_settings = service.get_app_settings()
            
            return {
                # SMTP settings
                'smtp_host': smtp_settings.host,
                'smtp_port': smtp_settings.port,
                'smtp_username': smtp_settings.username,
                'smtp_password': smtp_settings.password,
                'smtp_use_tls': smtp_settings.use_tls,
                'smtp_use_ssl': smtp_settings.use_ssl,
                
                # Pushover settings
                'pushover_token': pushover_settings.api_token if pushover_settings else None,
                'pushover_user': pushover_settings.default_user_key if pushover_settings else None,
                'pushover_device': pushover_settings.default_device if pushover_settings else None,
                
                # App settings
                'queue_dir': app_settings.queue_dir,
                'max_retries': app_settings.max_retries,
                'retry_delay': app_settings.retry_delay,
            }
    except Exception as e:
        logging.warning(f"Failed to read settings from database: {e}")
        return {}

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a single setting, fallback to environment variable, then default"""
    try:
        with Session(engine) as session:
            service = SettingsService(session)
            
            # Map common setting keys to database settings
            setting_map = {
                'SMTP_HOST': 'smtp.host',
                'SMTP_PORT': 'smtp.port', 
                'SMTP_USERNAME': 'smtp.username',
                'SMTP_PASSWORD': 'smtp.password',
                'SMTP_USE_TLS': 'smtp.use_tls',
                'SMTP_USE_SSL': 'smtp.use_ssl',
                'PUSHOVER_TOKEN': 'pushover.api_token',
                'PUSHOVER_USER_KEY': 'pushover.default_user_key',
                'PUSHOVER_DEVICE': 'pushover.default_device',
                'QUEUE_DIR': 'app.queue_dir',
                'MAX_RETRIES': 'app.max_retries',
                'RETRY_DELAY': 'app.retry_delay',
            }
            
            db_key = setting_map.get(key)
            if db_key:
                from .api.settings_crypto import get_setting as db_get_setting
                value = db_get_setting(session, db_key)
                if value is not None:
                    return value
            
    except Exception as e:
        logging.debug(f"Failed to get setting {key} from database: {e}")
    
    # Fallback to environment variable
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value
    
    return default

def get_smtp_config() -> Dict[str, Any]:
    """Get SMTP configuration for email sending"""
    try:
        with Session(engine) as session:
            service = SettingsService(session)
            settings = service.get_smtp_settings()
            
            return {
                'host': settings.host,
                'port': settings.port,
                'username': settings.username,
                'password': settings.password,
                'use_tls': settings.use_tls,
                'use_ssl': settings.use_ssl,
            }
    except Exception as e:
        logging.warning(f"Failed to get SMTP config from database: {e}")
        # Fallback to environment variables
        return {
            'host': os.getenv('SMTP_HOST', 'localhost'),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD'),
            'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
            'use_ssl': os.getenv('SMTP_USE_SSL', 'false').lower() == 'true',
        }

def get_pushover_config() -> Dict[str, Any]:
    """Get Pushover configuration for notifications"""
    try:
        with Session(engine) as session:
            service = SettingsService(session)
            settings = service.get_pushover_settings()
            
            if settings:
                return {
                    'token': settings.api_token,
                    'user': settings.default_user_key,
                    'device': settings.default_device,
                }
    except Exception as e:
        logging.warning(f"Failed to get Pushover config from database: {e}")
    
    # Fallback to environment variables
    return {
        'token': os.getenv('PUSHOVER_TOKEN'),
        'user': os.getenv('PUSHOVER_USER_KEY'),
        'device': os.getenv('PUSHOVER_DEVICE'),
    }