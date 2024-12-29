import json
import os

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv 

load_dotenv() 
DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()

class Session(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login_name = Column(String(255), unique=True, nullable=False)
    hash_password = Column(Text, nullable=False)
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")  

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    login_name = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    links = Column(Text) 
    session = relationship("Session", back_populates="messages")  
    
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
      
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to save a single message
def save_message(login_name: str, role: str, content: str, links: list = None):
    db = next(get_db())
    try:
        session = db.query(Session).filter(Session.login_name == login_name).first()
        if not session:
            print(f"User {login_name} not found!")
            return
        
        links_json = json.dumps(links) if links else None

        new_message = Message(
            login_name=session.id,
            role=role,
            content=content,
            links=links_json
        )
        db.add(new_message)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
    finally:
        db.close()

def load_session_history(login_name: str):
    db = next(get_db())
    chat_history = [{"role": "assistant", "content": "How may I assist you today?"}]
    try:
        session = db.query(Session).filter(Session.login_name == login_name).first()
        if session:
            for message in session.messages:
                links = json.loads(message.links) if message.links else []
                chat_history.append({
                    "role": message.role,
                    "content": message.content,
                    "links": links
                })
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        pass
    finally:
        db.close()

    return chat_history

def delete_user_messages(login_name: str):
    db = next(get_db())
    try:
        session = db.query(Session).filter(Session.login_name == login_name).first()
        if not session:
            print(f"User {login_name} not found!")
            return False

        db.query(Message).filter(Message.login_name == Session.id).delete()
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        db.close()