from fastapi import APIRouter, Depends
from sqlalchemy import text
from ..db import get_session
from ..models import QueueRecord
from ..schemas import TestSendIn
from .. import db as _db
from signalhub.queue import replay_queue
import os
from ..auth import get_current_user

router = APIRouter(prefix="/queue")

@router.get("/")
def list_queue(user=Depends(get_current_user)):
    with _db.get_session() as s:
        stmt = s.exec(text("SELECT id, timestamp, rcpt_to, subject, attempts, last_error FROM queuerecord"))
        rows = list(stmt)
    return rows

@router.post("/replay")
def replay(user=Depends(get_current_user)):
    qdir = os.getenv('QUEUE_DIR', './queue')
    replay_queue(qdir, None)
    return {"ok": True}
