import secrets
import argparse
from app.database import SessionLocal
from app.crud import create_api_key

def generate_key(owner: str):
    """Generates a secure API key and saves it to the database."""
    db = SessionLocal()
    try:
        # 生成一个安全的、URL安全的32字节密钥
        new_key = secrets.token_urlsafe(32)
        create_api_key(db, key=new_key, owner=owner)
        print(f"Successfully created API Key for '{owner}':")
        print(f"Key: {new_key}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new API key.")
    parser.add_argument("--owner", type=str, required=True, help="The owner of the API key (e.g., 'user_A', 'partner_service').")
    args = parser.parse_args()
    
    generate_key(args.owner)