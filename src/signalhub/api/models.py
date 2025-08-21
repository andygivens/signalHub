from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class AdminUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    password_hash: str
    api_key_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Setting(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
    category: Optional[str] = None  # e.g., "smtp", "pushover", "app"
    is_encrypted: bool = Field(default=False)  # whether value is encrypted
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Mapping(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rcpt_pattern: str
    user_key: str
    device: Optional[str] = None

class Template(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    content: str

class QueueRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    rcpt_to: str
    subject: str
    attempts: int = Field(default=0)
    last_error: Optional[str] = None
