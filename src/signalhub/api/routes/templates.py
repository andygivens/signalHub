from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from ..db import get_session
from ..models import Template
from ..schemas import TemplateIn
from ..auth import get_current_user

router = APIRouter(prefix="/templates")

@router.get("/")
def list_templates(user=Depends(get_current_user)):
    with get_session() as s:
        stmt = s.exec(text("SELECT id, name, content FROM template"))
        rows = [dict(id=r[0], name=r[1], content=r[2]) for r in stmt]
    return rows

@router.post("/")
def create_template(t_in: TemplateIn, user=Depends(get_current_user)):
    with get_session() as s:
        t = Template(name=t_in.name, content=t_in.content)
        s.add(t)
        s.commit()
        s.refresh(t)
    return t

@router.put("/{id}")
def update_template(id: int, t_in: TemplateIn, user=Depends(get_current_user)):
    with get_session() as s:
        t = s.get(Template, id)
        if not t:
            raise HTTPException(status_code=404, detail="Template not found")
        t.name = t_in.name
        t.content = t_in.content
        s.add(t)
        s.commit()
        s.refresh(t)
    return t

@router.delete("/{id}")
def delete_template(id: int, user=Depends(get_current_user)):
    with get_session() as s:
        t = s.get(Template, id)
        if not t:
            raise HTTPException(status_code=404, detail="Template not found")
        s.delete(t)
        s.commit()
    return {"ok": True}
