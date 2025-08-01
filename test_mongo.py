#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pydantic import BaseModel
from datetime import datetime
from passlib.context import CryptContext

# MongoDB connection
mongo_url = "mongodb://localhost:27017"
client = AsyncIOMotorClient(mongo_url)
db = client["test_database"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def show_admin_users():
    print("=== ADMIN USERS ACTUELS ===")
    users = await db.admin_users.find().to_list(10)
    for user in users:
        print(f"ID: {user.get('id')}")
        print(f"Username: {user.get('username')}")
        print(f"Email: {user.get('email')}")
        print(f"Is Active: {user.get('is_active')}")
        print(f"Created: {user.get('created_at')}")
        print("---")

async def modify_admin_direct():
    print("=== MODIFICATION DIRECTE EN BASE ===")
    
    # Modifier l'admin par défaut
    result = await db.admin_users.update_one(
        {"username": "admin"},
        {"$set": {
            "username": "admin_securise",
            "email": "admin.securise@jeanyves.dev",
            "hashed_password": get_password_hash("MotDePasseTresSecurise2024!"),
            "updated_at": datetime.utcnow()
        }}
    )
    
    if result.matched_count > 0:
        print("✅ Admin modifié avec succès en base")
        print("   Nouveau username: admin_securise")
        print("   Nouveau mot de passe: MotDePasseTresSecurise2024!")
    else:
        print("❌ Aucun admin trouvé à modifier")
    
    return result.matched_count > 0

async def main():
    await show_admin_users()
    success = await modify_admin_direct()
    print()
    print("=== ADMIN USERS APRÈS MODIFICATION ===")
    await show_admin_users()
    client.close()
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\nRésultat: {'SUCCÈS' if result else 'ÉCHEC'}")