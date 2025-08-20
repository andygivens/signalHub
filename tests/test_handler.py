import pytest
import time
from signalhub.handler import Handler, RateLimiter, Dedup
from signalhub.config import Config

class DummyEnvelope:
    def __init__(self, rcpt_tos, content):
        self.rcpt_tos = rcpt_tos
        self.content = content
        self.mail_from = "from@x"

@pytest.mark.asyncio
async def test_ratelimit():
    cfg = Config(rate_limit_per_minute=2)
    h = Handler(cfg)
    h.ratelimiter.window.clear()
    assert h.ratelimiter.allow()
    assert h.ratelimiter.allow()
    assert not h.ratelimiter.allow()

@pytest.mark.asyncio
async def test_dedup(monkeypatch):
    d = Dedup()
    key = "abc"
    assert not d.is_dup(key)
    assert d.is_dup(key)
    monkeypatch.setattr(time, "time", lambda: time.time() + 6)
    assert not d.is_dup(key)

@pytest.mark.asyncio
async def test_parse_message():
    cfg = Config()
    h = Handler(cfg)
    msg = b"Subject: Test [PRIO=1] [SOUND=ping]\n\nBody line"
    subject, body, directives = h._parse_message(msg)
    assert "Test" in subject
    assert body.startswith("Body")
    assert directives["prio"] == "1"
    assert directives["sound"] == "ping"
