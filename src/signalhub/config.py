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

    # pushover values: prefer explicit PUSHOVER_* env vars
    pushover_cfg = cfg.get("pushover", {})
    pushover_token = env.get("PUSHOVER_TOKEN") or pushover_cfg.get("api_token", "")
    # support both PUSHOVER_USER_KEY and DEFAULT_USER_KEY env names, then YAML default_user_key
    default_user_key = env.get("PUSHOVER_USER_KEY") or env.get("DEFAULT_USER_KEY") or pushover_cfg.get("default_user_key", "")
    recipient_map = pushover_cfg.get("recipient_map", {})

    server_cfg = cfg.get("server", {})
    # server-level env overrides
    listen_host = env.get("SMTP_HOST") or env.get("LISTEN_HOST") or server_cfg.get("listen_host", "127.0.0.1")
    listen_port = int(env.get("SMTP_PORT") or env.get("LISTEN_PORT") or server_cfg.get("listen_port", 2525))
    allow_nonauth = str(env.get("SMTP_ALLOW_NOAUTH", server_cfg.get("allow_nonauth", True))).lower() == "true"
    smtp_user = env.get("SMTP_USER") or server_cfg.get("smtp_user")
    smtp_pass = env.get("SMTP_PASS") or server_cfg.get("smtp_pass")
    tls_cert_file = env.get("TLS_CERT_FILE") or server_cfg.get("tls_cert_file")
    tls_key_file = env.get("TLS_KEY_FILE") or server_cfg.get("tls_key_file")

    return Config(
        listen_host=listen_host,
        listen_port=listen_port,
        allow_nonauth=allow_nonauth,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass,
        tls_cert_file=tls_cert_file,
        tls_key_file=tls_key_file,
        pushover_token=pushover_token,
        default_user_key=default_user_key,
        recipient_map=recipient_map,
        pushover_device=env.get("PUSHOVER_DEVICE") or pushover_cfg.get("pushover_device"),
        health_port=int(env.get("HTTP_HEALTH_PORT") or server_cfg.get("health_port", 8080)),
        rate_limit_per_minute=int(env.get("RATE_LIMIT_PER_MINUTE") or cfg.get("rate_limit_per_minute", 120)),
        queue_dir=env.get("QUEUE_DIR") or cfg.get("queue_dir"),
        enable_starttls=str(env.get("ENABLE_STARTTLS", server_cfg.get("enable_starttls", False))).lower() == "true",
    )
