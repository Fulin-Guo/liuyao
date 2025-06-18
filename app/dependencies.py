# app/dependencies.py
from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_api_key_from_header(
    x_api_key: str = Header(..., description="Your unique API key."),
    db: Session = Depends(get_db)
):
    """
    从请求头 X-API-Key 中获取并验证 API Key。
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is missing"
        )
    
    db_api_key = crud.get_api_key(db, key=x_api_key)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or inactive API Key"
        )
    
    return db_api_key