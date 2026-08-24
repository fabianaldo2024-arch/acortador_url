#!/usr/bin/env python3
import os

print("📝 Creando archivos del proyecto...")

# Lista de archivos a crear (contenido básico)
files = {
    "app/config.py": """import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shortener.db")
    DEBUG = True
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

config = Config()
""",
    
    "app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import config

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    
    "app/models.py": """from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    urls = relationship("URL", back_populates="owner", cascade="all, delete-orphan")

class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(10), unique=True, index=True, nullable=False)
    original_url = Column(Text, nullable=False)
    clicks = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="urls")
""",
    
    "app/schemas.py": """from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class URLCreate(BaseModel):
    original_url: HttpUrl

class Token(BaseModel):
    access_token: str
    token_type: str
""",
    
    "app/auth.py": """from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User
from app.config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401)
""",
    
    "app/dependencies.py": """from fastapi import Depends, HTTPException
from app.auth import get_current_user
from app.models import User

def admin_only(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
""",
    
    "app/main.py": """from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.database import get_db, engine
from app.models import Base, User, URL
from app.schemas import URLCreate, UserCreate
from app.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from app.dependencies import admin_only
import secrets
import string

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener API")
templates = Jinja2Templates(directory="app/templates")

@app.post("/api/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

@app.post("/api/token")
def login(form_data: dict, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.get("username"), form_data.get("password"))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/shorten")
def create_short_url(
    url_data: URLCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alphabet = string.ascii_letters + string.digits
    short_code = ''.join(secrets.choice(alphabet) for _ in range(6))
    
    new_url = URL(
        short_code=short_code,
        original_url=str(url_data.original_url),
        user_id=current_user.id
    )
    db.add(new_url)
    db.commit()
    
    return {
        "short_code": short_code,
        "short_url": f"http://localhost:8000/{short_code}"
    }

@app.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404)
    url.clicks += 1
    db.commit()
    return RedirectResponse(url=url.original_url)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    urls = db.query(URL).filter(URL.user_id == current_user.id).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "urls": urls, "user": current_user})

@app.get("/health")
def health():
    return {"status": "ok"}
""",
}

# Crear los archivos
for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"✅ Creado: {filepath}")

print("\n🎉 ¡Archivos creados!")
