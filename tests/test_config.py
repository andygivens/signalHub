import os
import tempfile
import yaml
from signalhub.config import load_config, Config

def test_env_and_yaml_merge(tmp_path, monkeypatch):
    monkeypatch.setenv("PUSHOVER_TOKEN", "envtoken")
    monkeypatch.setenv("SMTP_HOST", "1.2.3.4")
    config_yaml = tmp_path / "config.yaml"
    config_yaml.write_text("""
pushover:
  api_token: "filetoken"
  default_user_key: "fileuser"
  recipient_map:
    test@x.com: "U1"
server:
  listen_host: "0.0.0.0"
  listen_port: 2525
  allow_nonauth: true
""")
    monkeypatch.setenv("CONFIG_FILE", str(config_yaml))
    cfg = load_config()
    assert cfg.pushover_token == "envtoken"
    assert cfg.listen_host == "1.2.3.4"
    assert cfg.recipient_map["test@x.com"] == "U1"

def test_recipient_lookup():
    cfg = Config(recipient_map={"alerts@home.local": "U2"}, default_user_key="U0")
    from signalhub.handler import Handler
    h = Handler(cfg)
    assert h._route_recipient("alerts@home.local") == "U2"
    assert h._route_recipient("unknown@x") == "U0"
