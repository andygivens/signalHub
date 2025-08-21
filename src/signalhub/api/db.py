from sqlmodel import SQLModel, create_engine, Session
import os

DB_PATH = os.getenv('API_DB_PATH', './signalhub.db')
ENGINE = create_engine(f'sqlite:///{DB_PATH}', connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(ENGINE)

def get_session():
    return Session(ENGINE)
