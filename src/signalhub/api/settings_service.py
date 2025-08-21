from typing import Optional, Dict, Any
from sqlmodel import Session
from .settings_crypto import get_setting, set_setting
from .schemas import SMTPSettings, PushoverSettings, AppSettings

class SettingsService:
    """Service for managing structured application settings"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_smtp_settings(self) -> SMTPSettings:
        """Get SMTP configuration"""
        return SMTPSettings(
            host=get_setting(self.session, "smtp.host", "localhost"),
            port=int(get_setting(self.session, "smtp.port", "587")),
            username=get_setting(self.session, "smtp.username"),
            password=get_setting(self.session, "smtp.password"),
            use_tls=get_setting(self.session, "smtp.use_tls", "true").lower() == "true",
            use_ssl=get_setting(self.session, "smtp.use_ssl", "false").lower() == "true"
        )
    
    def set_smtp_settings(self, settings: SMTPSettings):
        """Save SMTP configuration"""
        set_setting(self.session, "smtp.host", settings.host, category="smtp")
        set_setting(self.session, "smtp.port", str(settings.port), category="smtp")
        
        if settings.username:
            set_setting(self.session, "smtp.username", settings.username, category="smtp")
        if settings.password:
            set_setting(self.session, "smtp.password", settings.password, 
                       category="smtp", encrypt=True, description="SMTP password")
            
        set_setting(self.session, "smtp.use_tls", str(settings.use_tls).lower(), category="smtp")
        set_setting(self.session, "smtp.use_ssl", str(settings.use_ssl).lower(), category="smtp")
    
    def get_pushover_settings(self) -> Optional[PushoverSettings]:
        """Get Pushover configuration"""
        api_token = get_setting(self.session, "pushover.api_token")
        if not api_token:
            return None
            
        return PushoverSettings(
            api_token=api_token,
            default_user_key=get_setting(self.session, "pushover.default_user_key"),
            default_device=get_setting(self.session, "pushover.default_device")
        )
    
    def set_pushover_settings(self, settings: PushoverSettings):
        """Save Pushover configuration"""
        set_setting(self.session, "pushover.api_token", settings.api_token, 
                   category="pushover", encrypt=True, description="Pushover API token")
        
        if settings.default_user_key:
            set_setting(self.session, "pushover.default_user_key", settings.default_user_key, 
                       category="pushover")
        if settings.default_device:
            set_setting(self.session, "pushover.default_device", settings.default_device, 
                       category="pushover")
    
    def get_app_settings(self) -> AppSettings:
        """Get application settings"""
        return AppSettings(
            queue_dir=get_setting(self.session, "app.queue_dir", "./queue"),
            max_retries=int(get_setting(self.session, "app.max_retries", "3")),
            retry_delay=int(get_setting(self.session, "app.retry_delay", "300"))
        )
    
    def set_app_settings(self, settings: AppSettings):
        """Save application settings"""
        set_setting(self.session, "app.queue_dir", settings.queue_dir, category="app")
        set_setting(self.session, "app.max_retries", str(settings.max_retries), category="app")
        set_setting(self.session, "app.retry_delay", str(settings.retry_delay), category="app")
    
    def test_smtp_connection(self, settings: SMTPSettings) -> Dict[str, Any]:
        """Test SMTP connection with given settings"""
        import smtplib
        import ssl
        
        try:
            if settings.use_ssl:
                server = smtplib.SMTP_SSL(settings.host, settings.port)
            else:
                server = smtplib.SMTP(settings.host, settings.port)
                if settings.use_tls:
                    server.starttls()
            
            if settings.username and settings.password:
                server.login(settings.username, settings.password)
            
            server.quit()
            return {"success": True, "message": "SMTP connection successful"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_pushover_connection(self, settings: PushoverSettings) -> Dict[str, Any]:
        """Test Pushover API connection"""
        import requests
        
        try:
            response = requests.post("https://api.pushover.net/1/users/validate.json", {
                "token": settings.api_token,
                "user": settings.default_user_key or "test"
            }, timeout=10)
            
            if response.status_code == 200:
                return {"success": True, "message": "Pushover API connection successful"}
            else:
                return {"success": False, "error": f"API returned {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}