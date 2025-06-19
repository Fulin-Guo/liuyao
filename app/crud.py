from sqlalchemy.orm import Session
from . import models

def get_api_key(db: Session, key: str):
    return db.query(models.ApiKey).filter(models.ApiKey.key == key, models.ApiKey.is_active == True).first()

def create_api_key(db: Session, key: str, owner: str):
    db_key = models.ApiKey(key=key, owner=owner)
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key