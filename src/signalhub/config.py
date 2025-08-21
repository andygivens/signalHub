import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Config:
    listen_host: str = "127.0.0.1"
    listen_port: int = 2525
    allow_nonauth: bool = True
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    tls_cert_file: Optional[str] = None
    tls_key_file: Optional[str] = None
    pushover_token: str = ""
    default_user_key: str = ""
    recipient_map: Dict[str, str] = field(default_factory=dict)
    pushover_device: Optional[str] = None
    health_port: int = 8080
    rate_limit_per_minute: int = 120
    queue_dir: Optional[str] = None
    enable_starttls: bool = False


import os
import yaml
from typing import Dict, Any, Optional
from .settings_bridge import get_db_settings, get_setting

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from database first, then YAML file, then environment variables"""
    
    # Start with database settings
    config = get_db_settings()
    
    # Load YAML config if it exists
    yaml_config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load {config_path}: {e}")
    
    # Merge configs (database takes precedence over YAML, env vars take precedence over both)
    merged_config = {**yaml_config, **config}
    
    # Override with environment variables if present
    env_overrides = {
        'smtp_host': get_setting('SMTP_HOST'),
        'smtp_port': int(get_setting('SMTP_PORT', '587')),
        'smtp_username': get_setting('SMTP_USERNAME'),
        'smtp_password': get_setting('SMTP_PASSWORD'),
        'smtp_use_tls': get_setting('SMTP_USE_TLS', 'true').lower() == 'true',
        'smtp_use_ssl': get_setting('SMTP_USE_SSL', 'false').lower() == 'true',
        'pushover_token': get_setting('PUSHOVER_TOKEN'),
        'pushover_user': get_setting('PUSHOVER_USER_KEY'),
        'pushover_device': get_setting('PUSHOVER_DEVICE'),
        'queue_dir': get_setting('QUEUE_DIR', './queue'),
        'max_retries': int(get_setting('MAX_RETRIES', '3')),
        'retry_delay': int(get_setting('RETRY_DELAY', '300')),
    }
    
    # Only override if environment/database value exists
    for key, value in env_overrides.items():
        if value is not None:
            merged_config[key] = value
    
    return merged_config

def get_smtp_config() -> Dict[str, Any]:
    """Get SMTP configuration for use by the SMTP server"""
    from .settings_bridge import get_smtp_config as bridge_get_smtp
    return bridge_get_smtp()

def get_pushover_config() -> Dict[str, Any]:
    """Get Pushover configuration for notifications"""
    from .settings_bridge import get_pushover_config as bridge_get_pushover
    return bridge_get_pushover()
