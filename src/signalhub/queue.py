import os
import json
import time

def persist_failed_send(queue_dir, envelope, directives):
    os.makedirs(queue_dir, exist_ok=True)
    record = {
        "timestamp": time.time(),
        "rcpt_tos": envelope.rcpt_tos,
        "mail_from": envelope.mail_from,
        "content": envelope.content.decode(errors="replace"),
        "directives": directives,
    }
    with open(os.path.join(queue_dir, "queue.jsonl"), "a") as f:
        f.write(json.dumps(record) + "\n")

def replay_queue(queue_dir, send_func):
    path = os.path.join(queue_dir, "queue.jsonl")
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            record = json.loads(line)
            send_func(
                record["rcpt_tos"],
                record["content"],
                record["directives"]
            )
