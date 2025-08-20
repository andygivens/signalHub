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


def load_config():
    env = os.environ
    config_file = env.get("CONFIG_FILE", "./config.yaml")
    cfg = {}
    if os.path.exists(config_file):
        with open(config_file) as f:
            cfg = yaml.safe_load(f) or {}
    # Merge env vars
    def env_or_cfg(key, default=None):
        return env.get(key.upper(), cfg.get(key, default))
    recipient_map = cfg.get("pushover", {}).get("recipient_map", {})
    return Config(
        listen_host=env_or_cfg("listen_host", cfg.get("server", {}).get("listen_host", "127.0.0.1")),
        listen_port=int(env_or_cfg("listen_port", cfg.get("server", {}).get("listen_port", 2525))),
        allow_nonauth=str(env_or_cfg("allow_nonauth", cfg.get("server", {}).get("allow_nonauth", True))).lower() == "true",
        smtp_user=env_or_cfg("smtp_user", cfg.get("server", {}).get("smtp_user")),
        smtp_pass=env_or_cfg("smtp_pass", cfg.get("server", {}).get("smtp_pass")),
        tls_cert_file=env_or_cfg("tls_cert_file", cfg.get("server", {}).get("tls_cert_file")),
        tls_key_file=env_or_cfg("tls_key_file", cfg.get("server", {}).get("tls_key_file")),
        pushover_token=env_or_cfg("pushover_token", cfg.get("pushover", {}).get("api_token", "")),
        default_user_key=env_or_cfg("default_user_key", cfg.get("pushover", {}).get("default_user_key", "")),
        recipient_map=recipient_map,
        pushover_device=env_or_cfg("pushover_device", cfg.get("pushover", {}).get("pushover_device")),
        health_port=int(env_or_cfg("health_port", cfg.get("server", {}).get("health_port", 8080))),
        rate_limit_per_minute=int(env_or_cfg("rate_limit_per_minute", cfg.get("rate_limit_per_minute", 120))),
        queue_dir=env_or_cfg("queue_dir", cfg.get("queue_dir")),
        enable_starttls=str(env_or_cfg("enable_starttls", cfg.get("server", {}).get("enable_starttls", False))).lower() == "true",
    )
