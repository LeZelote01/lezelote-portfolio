#!/usr/bin/env python3
"""
Script pour initialiser les données personnelles par défaut
Usage: python init_personal_data.py
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from datetime import datetime

# Add current directory to path to import models
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from models import PersonalInfo

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

async def init_personal_data():
    """Initialize personal data if it doesn't exist"""
    print("🔄 Initializing personal data...")
    
    # Check if personal data already exists
    existing = await db.personal_info.find_one()
    if existing:
        print("ℹ️ Personal data already exists, skipping...")
        return
    
    # Create personal info with placeholder data
    personal_info = PersonalInfo(
        name="[Votre Nom] (LeZelote)",  # Placeholder for full name + alias
        title="Spécialiste Cybersécurité & Développeur Python",
        subtitle="Expert en sécurité numérique et développement d'applications",
        bio="Passionné par la cybersécurité et le développement Python, je mets mon expertise technique au service de votre sécurité numérique. Formé aux dernières technologies et constamment en veille sur les menaces émergentes, j'accompagne les entreprises dans leur transformation digitale sécurisée.",
        email="contact@lezelote.dev",
        phone=None,
        location="[Votre Localisation]",  # Placeholder for location
        availability="Disponible pour de nouveaux projets",
        website="https://lezelote-portfolio.vercel.app/",
        age=None,  # To be filled via admin dashboard
        birth_date=None,
        profile_image_url=None,  # To be added later
        years_experience=5,
        certifications=[
            "Python Developer Certification",
            "Cybersecurity Fundamentals",
            "Network Security Professional"
        ],
        languages=[
            "Français (Natif)",
            "Anglais (Courant)",
            "Espagnol (Intermédiaire)"
        ],
        education="Formation en Cybersécurité et Développement Python"
    )
    
    await db.personal_info.insert_one(personal_info.dict())
    print("✅ Personal data initialized successfully")
    print("   You can now update this data via the admin dashboard at /admin/personal")

async def main():
    """Main function"""
    print("🚀 Initializing personal data...")
    print(f"📍 MongoDB URL: {mongo_url}")
    print(f"📍 Database: {os.environ.get('DB_NAME', 'test_database')}")
    print()
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
        print()
        
        # Initialize personal data
        await init_personal_data()
        
        print()
        print("🎉 Personal data initialization completed!")
        print("📝 Next steps:")
        print("   1. Go to http://localhost:3000/admin/login")
        print("   2. Login with: admin / admin123")
        print("   3. Navigate to 'Informations personnelles'")
        print("   4. Update your name, age, location, and photo URL")
        
    except Exception as e:
        print(f"❌ Failed to initialize personal data: {str(e)}")
        sys.exit(1)
    
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(main())