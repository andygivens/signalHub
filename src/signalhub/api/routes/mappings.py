from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from ..db import get_session
from ..models import Mapping
from ..schemas import MappingIn
from ..auth import get_current_user

router = APIRouter(prefix="/mappings")

@router.get("/")
def list_mappings(user=Depends(get_current_user)):
    with get_session() as s:
        stmt = s.exec(text("SELECT id, rcpt_pattern, user_key, device FROM mapping"))
        rows = [dict(id=r[0], rcpt_pattern=r[1], user_key=r[2], device=r[3]) for r in stmt]
    return rows

@router.post("/")
def create_mapping(m_in: MappingIn, user=Depends(get_current_user)):
    with get_session() as s:
        m = Mapping(rcpt_pattern=m_in.rcpt_pattern, user_key=m_in.user_key, device=m_in.device)
        s.add(m)
        s.commit()
        s.refresh(m)
    return m

@router.put("/{id}")
def update_mapping(id: int, m_in: MappingIn, user=Depends(get_current_user)):
    with get_session() as s:
        m = s.get(Mapping, id)
        if not m:
            raise HTTPException(status_code=404, detail="Mapping not found")
        m.rcpt_pattern = m_in.rcpt_pattern
        m.user_key = m_in.user_key
        m.device = m_in.device
        s.add(m)
        s.commit()
        s.refresh(m)
    return m

@router.delete("/{id}")
def delete_mapping(id: int, user=Depends(get_current_user)):
    with get_session() as s:
        m = s.get(Mapping, id)
        if not m:
            raise HTTPException(status_code=404, detail="Mapping not found")
        s.delete(m)
        s.commit()
    return {"ok": True}
