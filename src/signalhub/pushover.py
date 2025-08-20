import urllib.request
import urllib.parse
import json

def send_message(user_key, title, message, token, priority=None, sound=None, url=None, url_title=None, device=None, timeout=10):
    endpoint = "https://api.pushover.net/1/messages.json"
    data = {
        "token": token,
        "user": user_key,
        "title": title[:250],
        "message": message[:1024],
    }
    if priority is not None:
        try:
            data["priority"] = int(priority)
        except Exception:
            pass
    if sound:
        data["sound"] = sound
    if url:
        data["url"] = url
    if url_title:
        data["url_title"] = url_title
    if device:
        data["device"] = device
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(endpoint, data=encoded)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode()
            ok = resp.status == 200 and json.loads(body).get("status") == 1
            return ok, resp.status, body
    except Exception as e:
        return False, 0, str(e)
