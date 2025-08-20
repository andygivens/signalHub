import re
import time
import logging
import asyncio
import email
import json
from email import policy
from email.parser import BytesParser
from collections import deque
from .pushover import send_message
from .queue import persist_failed_send

class RateLimiter:
    def __init__(self, rate_per_minute):
        self.rate = rate_per_minute
        self.window = deque()

    def allow(self):
        now = time.time()
        while self.window and self.window[0] < now - 60:
            self.window.popleft()
        if len(self.window) < self.rate:
            self.window.append(now)
            return True
        return False

class Dedup:
    def __init__(self):
        self.last = {}

    def is_dup(self, key):
        now = time.time()
        if key in self.last and now - self.last[key] < 5:
            return True
        self.last[key] = now
        return False

class Handler:
    def __init__(self, config):
        self.config = config
        self.ratelimiter = RateLimiter(config.rate_limit_per_minute)
        self.dedup = Dedup()
        self.metrics = {
            'emails_received': 0,
            'pushed_ok': 0,
            'pushed_failed': 0,
            'dedup_dropped': 0,
            'rate_limited': 0,
        }
        self.authenticator = self._authenticator if not config.allow_nonauth else None
        self.tls_context = None  # Set up if needed

    async def handle_DATA(self, server, session, envelope):
        self.metrics['emails_received'] += 1
        remote_ip = session.peer[0] if session.peer else None
        rcpt_to = envelope.rcpt_tos[0] if envelope.rcpt_tos else None
        subject, body, directives = self._parse_message(envelope.content)
        title = subject[:250] if subject else "(No Subject)"
        message = body[:1024] if body else "(No Body)"
        dedup_key = f"{title}:{message}"
        if self.dedup.is_dup(dedup_key):
            self.metrics['dedup_dropped'] += 1
            logging.info(f'{{"event":"dedup","rcpt_to":"{rcpt_to}","subject":"{title}"}}')
            return '250 Message deduplicated'
        if not self.ratelimiter.allow():
            self.metrics['rate_limited'] += 1
            logging.info(f'{{"event":"rate_limit","rcpt_to":"{rcpt_to}","subject":"{title}"}}')
            return '451 Rate limit exceeded, try later'
        user_key = self._route_recipient(rcpt_to)
        token = self.config.pushover_token
        device = self.config.pushover_device

        # Log the translated message before sending to Pushover
        log_payload = {
            "event": "translated_message",
            "rcpt_to": rcpt_to,
            "title": title,
            "message": message,
            "directives": directives,
            "user_key": user_key,
        }
        logging.info(json.dumps(log_payload))

        retries = 0
        backoffs = [0.5, 2, 5]
        while retries <= 3:
            ok, status, body_resp = await asyncio.get_event_loop().run_in_executor(
                None,
                send_message,
                user_key,
                title,
                message,
                token,
                directives.get('priority'),
                directives.get('sound'),
                directives.get('url'),
                directives.get('url_title'),
                device,
            )
            if ok:
                self.metrics['pushed_ok'] += 1
                logging.info(f'{{"event":"push_ok","rcpt_to":"{rcpt_to}","subject":"{title}","status":{status}}}')
                return '250 Message accepted'
            else:
                retries += 1
                # log failure details
                logging.error(json.dumps({
                    "event": "push_attempt_failed",
                    "rcpt_to": rcpt_to,
                    "subject": title,
                    "status": status,
                    "response": str(body_resp),
                    "retry": retries,
                }))
                if retries > 3:
                    self.metrics['pushed_failed'] += 1
                    logging.info(f'{{"event":"push_failed","rcpt_to":"{rcpt_to}","subject":"{title}","status":{status}}}')
                    if self.config.queue_dir:
                        persist_failed_send(self.config.queue_dir, envelope, directives)
                    return '451 Temporary failure, queued'
                await asyncio.sleep(backoffs[retries-1])

    def _parse_message(self, content):
        msg = BytesParser(policy=policy.default).parsebytes(content)
        subject = msg['subject'] or ""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_content().strip()
                    break
            if not body:
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        body = re.sub('<[^<]+?>', '', part.get_content())
                        break
        else:
            if msg.get_content_type() == "text/plain":
                body = msg.get_content().strip()
            elif msg.get_content_type() == "text/html":
                body = re.sub('<[^<]+?>', '', msg.get_content())
        directives = {}
        directive_re = re.compile(r'\[(PRIO|SOUND|URL|URLTITLE)=([^\]]+)\]', re.I)
        for m in directive_re.finditer(subject):
            key = m.group(1).lower()
            val = m.group(2)
            directives[key] = val
        return subject, body, directives

    def _route_recipient(self, rcpt_to):
        if not rcpt_to:
            return self.config.default_user_key
        rcpt_map = {k.lower(): v for k, v in self.config.recipient_map.items()}
        val = rcpt_map.get(rcpt_to.lower())
        # If mapping exists but is empty/None, fall back to default
        if not val:
            return self.config.default_user_key
        return val

    def _authenticator(self, server, session, envelope, mechanism, auth_data):
        if mechanism != "LOGIN":
            return False
        user = self.config.smtp_user
        pw = self.config.smtp_pass
        if not user or not pw:
            return False
        return auth_data.login_data[0] == user and auth_data.login_data[1] == pw
