from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from ..db import get_session
from ..models import Setting
from ..schemas import SettingIn, SMTPSettings, PushoverSettings, AppSettings
from ..auth import get_current_user
from ..settings_service import SettingsService

router = APIRouter(prefix="/settings")

@router.get("/")
def list_settings(user=Depends(get_current_user)):
    """Get all raw settings (for debugging)"""
    with get_session() as s:
        stmt = s.exec(text("SELECT key, value FROM setting"))
        rows = list(stmt)
    return {r[0]: r[1] for r in rows}

@router.post("/")
def set_setting(s_in: SettingIn, user=Depends(get_current_user)):
    """Set a raw setting (for debugging)"""
    with get_session() as s:
        st = Setting(key=s_in.key, value=s_in.value)
        s.merge(st)
        s.commit()
    return {"ok": True}

# SMTP Settings
@router.get("/smtp")
def get_smtp_settings(user=Depends(get_current_user)):
    """Get SMTP configuration"""
    with get_session() as s:
        service = SettingsService(s)
        settings = service.get_smtp_settings()
        # Don't return password in response
        settings.password = "***" if settings.password else None
        return settings

@router.post("/smtp")
def set_smtp_settings(settings: SMTPSettings, user=Depends(get_current_user)):
    """Save SMTP configuration"""
    with get_session() as s:
        service = SettingsService(s)
        service.set_smtp_settings(settings)
    return {"ok": True, "message": "SMTP settings saved"}

@router.post("/smtp/test")
def test_smtp_settings(settings: SMTPSettings, user=Depends(get_current_user)):
    """Test SMTP connection"""
    with get_session() as s:
        service = SettingsService(s)
        result = service.test_smtp_connection(settings)
    return result

# Pushover Settings
@router.get("/pushover")
def get_pushover_settings(user=Depends(get_current_user)):
    """Get Pushover configuration"""
    with get_session() as s:
        service = SettingsService(s)
        settings = service.get_pushover_settings()
        if settings:
            # Don't return API token in response
            settings.api_token = "***"
        return settings

@router.post("/pushover")
def set_pushover_settings(settings: PushoverSettings, user=Depends(get_current_user)):
    """Save Pushover configuration"""
    with get_session() as s:
        service = SettingsService(s)
        service.set_pushover_settings(settings)
    return {"ok": True, "message": "Pushover settings saved"}

@router.post("/pushover/test")
def test_pushover_settings(settings: PushoverSettings, user=Depends(get_current_user)):
    """Test Pushover API connection"""
    with get_session() as s:
        service = SettingsService(s)
        result = service.test_pushover_connection(settings)
    return result

# App Settings
@router.get("/app")
def get_app_settings(user=Depends(get_current_user)):
    """Get application settings"""
    with get_session() as s:
        service = SettingsService(s)
        return service.get_app_settings()

@router.post("/app")
def set_app_settings(settings: AppSettings, user=Depends(get_current_user)):
    """Save application settings"""
    with get_session() as s:
        service = SettingsService(s)
        service.set_app_settings(settings)
    return {"ok": True, "message": "App settings saved"}
