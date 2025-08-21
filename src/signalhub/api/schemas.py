from typing import Optional
from pydantic import BaseModel, EmailStr

class LoginIn(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    token: str

class SettingIn(BaseModel):
    key: str
    value: str

class MappingIn(BaseModel):
    rcpt_pattern: str
    user_key: str
    device: Optional[str] = None

class TemplateIn(BaseModel):
    name: str
    content: str

class TestSendIn(BaseModel):
    to: EmailStr
    subject: str
    body: str

# Settings schemas
class SMTPSettings(BaseModel):
    host: str
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True
    use_ssl: bool = False

class PushoverSettings(BaseModel):
    api_token: str
    default_user_key: Optional[str] = None
    default_device: Optional[str] = None
    
class AppSettings(BaseModel):
    queue_dir: str = "./queue"
    max_retries: int = 3
    retry_delay: int = 300  # seconds
