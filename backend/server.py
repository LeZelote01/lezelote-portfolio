from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

# Import admin routes, auth routes and analytics routes
from admin_routes import admin_router
from auth_routes import auth_router
from analytics_routes import analytics_router


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Quote Models
class QuoteData(BaseModel):
    project_type: str
    complexity: str
    timeline: str
    features: List[str] = []
    maintenance: bool = False
    training: bool = False
    documentation: bool = False
    base_price: float
    features_price: float
    extras_price: float
    total_price: float
    min_price: float
    max_price: float

class ContactInfo(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None

class Quote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quote_data: QuoteData
    contact_info: Optional[ContactInfo] = None
    status: str = "draft"  # draft, sent, accepted, rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class QuoteCreate(BaseModel):
    quote_data: QuoteData
    contact_info: Optional[ContactInfo] = None

# Booking Models
class BookingData(BaseModel):
    service_id: str
    service_name: str
    date: str  # ISO format
    time: str
    duration: str

class BookingContact(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_data: BookingData
    contact_info: BookingContact
    status: str = "confirmed"  # confirmed, cancelled, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BookingCreate(BaseModel):
    booking_data: BookingData
    contact_info: BookingContact

# Resource Models
class Resource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    type: str
    size: str
    pages: Optional[int] = None
    downloads: int = 0
    rating: float = 0.0
    featured: bool = False
    tags: List[str] = []
    difficulty: str
    file_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResourceDownload(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    downloaded_at: datetime = Field(default_factory=datetime.utcnow)

class NewsletterSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    status: str = "active"  # active, unsubscribed
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)

class NewsletterSubscribe(BaseModel):
    email: EmailStr

# Contact Message Models
class ContactMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    subject: str
    message: str
    service: Optional[str] = None
    status: str = "new"  # new, read, replied
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    replied_at: Optional[datetime] = None

class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    service: Optional[str] = None

class ContactStatusUpdate(BaseModel):
    status: str

# Testimonial Models
class PublicTestimonialSubmission(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    role: Optional[str] = None
    content: str
    rating: int = Field(ge=1, le=5)
    service_used: Optional[str] = None

class PendingTestimonial(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    company: Optional[str] = None
    role: Optional[str] = None
    content: str
    rating: int = Field(ge=1, le=5)
    service_used: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None



# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Quote endpoints
@api_router.post("/quotes", response_model=Quote)
async def create_quote(quote_input: QuoteCreate):
    quote_dict = quote_input.dict()
    quote_obj = Quote(**quote_dict)
    _ = await db.quotes.insert_one(quote_obj.dict())
    return quote_obj

@api_router.get("/quotes", response_model=List[Quote])
async def get_quotes():
    quotes = await db.quotes.find().sort("created_at", -1).to_list(100)
    return [Quote(**quote) for quote in quotes]

@api_router.get("/quotes/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str):
    quote = await db.quotes.find_one({"id": quote_id})
    if not quote:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Quote not found")
    return Quote(**quote)

@api_router.put("/quotes/{quote_id}", response_model=Quote)
async def update_quote(quote_id: str, quote_input: QuoteCreate):
    quote_dict = quote_input.dict()
    quote_dict["updated_at"] = datetime.utcnow()
    
    result = await db.quotes.update_one(
        {"id": quote_id}, 
        {"$set": quote_dict}
    )
    
    if result.matched_count == 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Quote not found")
    
    updated_quote = await db.quotes.find_one({"id": quote_id})
    return Quote(**updated_quote)

# Booking endpoints
@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking_input: BookingCreate):
    booking_dict = booking_input.dict()
    booking_obj = Booking(**booking_dict)
    _ = await db.bookings.insert_one(booking_obj.dict())
    return booking_obj

@api_router.get("/bookings", response_model=List[Booking])
async def get_bookings():
    bookings = await db.bookings.find().sort("created_at", -1).to_list(100)
    return [Booking(**booking) for booking in bookings]

@api_router.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str):
    booking = await db.bookings.find_one({"id": booking_id})
    if not booking:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Booking not found")
    return Booking(**booking)

@api_router.get("/bookings/availability/{date}")
async def get_availability(date: str):
    """Get available time slots for a specific date"""
    bookings = await db.bookings.find({
        "booking_data.date": date,
        "status": {"$ne": "cancelled"}
    }).to_list(100)
    
    booked_times = [booking["booking_data"]["time"] for booking in bookings]
    
    # All possible time slots
    all_slots = [
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
    ]
    
    available_slots = [slot for slot in all_slots if slot not in booked_times]
    
    return {
        "date": date,
        "available_slots": available_slots,
        "booked_slots": booked_times
    }

# Resource endpoints
@api_router.get("/resources", response_model=List[Resource])
async def get_resources():
    resources = await db.resources.find().sort("created_at", -1).to_list(100)
    return [Resource(**resource) for resource in resources]

@api_router.get("/resources/{resource_id}", response_model=Resource)
async def get_resource(resource_id: str):
    resource = await db.resources.find_one({"id": resource_id})
    if not resource:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Resource not found")
    return Resource(**resource)

@api_router.post("/resources/{resource_id}/download")
async def download_resource(resource_id: str, user_email: Optional[str] = None):
    from fastapi import Request, HTTPException
    
    # Check if resource exists
    resource = await db.resources.find_one({"id": resource_id})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Record download
    download_record = ResourceDownload(
        resource_id=resource_id,
        user_email=user_email
    )
    await db.resource_downloads.insert_one(download_record.dict())
    
    # Increment download count
    await db.resources.update_one(
        {"id": resource_id},
        {"$inc": {"downloads": 1}}
    )
    
    # Return clean resource data without MongoDB ObjectId
    clean_resource = Resource(**resource)
    return {"message": "Download recorded", "resource": clean_resource.dict()}

@api_router.post("/newsletter/subscribe")
async def subscribe_newsletter(subscription: NewsletterSubscribe):
    # Check if already subscribed
    existing = await db.newsletter_subscriptions.find_one({"email": subscription.email})
    
    if existing:
        return {"message": "Email already subscribed", "status": "existing"}
    
    # Create new subscription
    sub_record = NewsletterSubscription(email=subscription.email)
    await db.newsletter_subscriptions.insert_one(sub_record.dict())
    
    return {"message": "Successfully subscribed to newsletter", "status": "new"}

@api_router.post("/contact", response_model=ContactMessage)
async def submit_contact_message(contact: ContactMessageCreate):
    """Submit a contact message"""
    contact_dict = contact.dict()
    contact_obj = ContactMessage(**contact_dict)
    _ = await db.contact_messages.insert_one(contact_obj.dict())
    return contact_obj

@api_router.get("/contact", response_model=List[ContactMessage])
async def get_contact_messages():
    """Get all contact messages (admin only in real scenario)"""
    messages = await db.contact_messages.find().sort("submitted_at", -1).to_list(100)
    return [ContactMessage(**message) for message in messages]

class ContactStatusUpdate(BaseModel):
    status: str

@api_router.put("/contact/{message_id}/status")
async def update_contact_status(message_id: str, status_update: ContactStatusUpdate):
    """Update contact message status"""
    result = await db.contact_messages.update_one(
        {"id": message_id}, 
        {"$set": {"status": status_update.status}}
    )
    
    if result.matched_count == 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"message": "Status updated successfully"}

@api_router.post("/testimonials/submit")
async def submit_testimonial(testimonial: PublicTestimonialSubmission):
    """Submit a testimonial from public user"""
    testimonial_dict = testimonial.dict()
    testimonial_obj = PendingTestimonial(**testimonial_dict)
    await db.pending_testimonials.insert_one(testimonial_obj.dict())
    
    return {"message": "Témoignage soumis avec succès. Il sera examiné avant publication.", "status": "submitted"}

@api_router.post("/resources/init")
async def init_default_resources():
    """Initialize default resources if they don't exist"""
    
    # Check if resources already exist
    existing_count = await db.resources.count_documents({})
    if existing_count > 0:
        return {"message": "Resources already initialized", "count": existing_count}
    
    # Default resources data
    default_resources = [
        {
            "title": "Guide complet de la cybersécurité pour PME",
            "description": "Un guide pratique de 50 pages pour sécuriser votre entreprise avec un budget limité.",
            "category": "Guide",
            "type": "PDF",
            "size": "2.8 MB",
            "pages": 50,
            "downloads": 1247,
            "rating": 4.8,
            "featured": True,
            "tags": ["PME", "Sécurité", "Guide", "Pratique"],
            "difficulty": "Débutant"
        },
        {
            "title": "Checklist sécurité pour développeurs",
            "description": "Liste de vérification complète pour sécuriser vos applications web.",
            "category": "Checklist",
            "type": "PDF",
            "size": "1.2 MB",
            "pages": 15,
            "downloads": 892,
            "rating": 4.9,
            "featured": True,
            "tags": ["Développement", "Web", "Sécurité", "Checklist"],
            "difficulty": "Intermédiaire"
        },
        {
            "title": "Scripts Python pour la cybersécurité",
            "description": "Collection de scripts Python prêts à l'emploi pour l'analyse de sécurité.",
            "category": "Scripts",
            "type": "ZIP",
            "size": "5.4 MB",
            "pages": None,
            "downloads": 1567,
            "rating": 4.7,
            "featured": True,
            "tags": ["Python", "Scripts", "Automatisation", "Outils"],
            "difficulty": "Avancé"
        },
        {
            "title": "Template de politique de sécurité",
            "description": "Modèle personnalisable de politique de sécurité informatique pour entreprises.",
            "category": "Template",
            "type": "DOC",
            "size": "890 KB",
            "pages": 25,
            "downloads": 634,
            "rating": 4.6,
            "featured": False,
            "tags": ["Politique", "Entreprise", "Conformité", "Template"],
            "difficulty": "Débutant"
        },
        {
            "title": "Guide d'audit de sécurité",
            "description": "Méthodologie complète pour réaliser un audit de sécurité informatique.",
            "category": "Guide",
            "type": "PDF",
            "size": "4.1 MB",
            "pages": 75,
            "downloads": 1089,
            "rating": 4.8,
            "featured": True,
            "tags": ["Audit", "Méthodologie", "Sécurité", "Entreprise"],
            "difficulty": "Avancé"
        }
    ]
    
    # Create Resource objects and insert them
    resources_to_insert = []
    for resource_data in default_resources:
        resource = Resource(**resource_data)
        resources_to_insert.append(resource.dict())
    
    result = await db.resources.insert_many(resources_to_insert)
    
    return {
        "message": "Default resources initialized successfully",
        "count": len(result.inserted_ids),
        "resource_ids": [str(id) for id in result.inserted_ids]
    }

# Include the admin router, auth router and analytics router
api_router.include_router(admin_router)
api_router.include_router(auth_router)
api_router.include_router(analytics_router)

# ================== PUBLIC PORTFOLIO ENDPOINTS ==================
# These endpoints are used to feed the public portfolio

@api_router.get("/public/personal", response_model=dict)
async def get_public_personal_info():
    """Get personal information for public portfolio"""
    personal = await db.personal_info.find_one()
    if not personal:
        return {}
    # Remove MongoDB _id field for JSON serialization
    personal.pop("_id", None)
    return personal

@api_router.get("/public/skills", response_model=List[dict])
async def get_public_skills():
    """Get skills for public portfolio"""
    skills = await db.skill_categories.find().to_list(100)
    # Remove MongoDB _id fields
    return [{k: v for k, v in skill.items() if k != "_id"} for skill in skills]

@api_router.get("/public/technologies", response_model=List[dict])
async def get_public_technologies():
    """Get technologies for public portfolio"""
    techs = await db.technologies.find().sort("name", 1).to_list(100)
    return [{k: v for k, v in tech.items() if k != "_id"} for tech in techs]

@api_router.get("/public/projects", response_model=List[dict])
async def get_public_projects():
    """Get projects for public portfolio"""
    projects = await db.projects.find().sort("order_index", 1).to_list(100)
    return [{k: v for k, v in project.items() if k != "_id"} for project in projects]

@api_router.get("/public/services", response_model=List[dict])
async def get_public_services():
    """Get services for public portfolio"""
    services = await db.services.find().sort("order_index", 1).to_list(100)
    return [{k: v for k, v in service.items() if k != "_id"} for service in services]

@api_router.get("/public/testimonials", response_model=List[dict])
async def get_public_testimonials():
    """Get testimonials for public portfolio"""
    testimonials = await db.testimonials.find().sort("order_index", 1).to_list(100)
    return [{k: v for k, v in testimonial.items() if k != "_id"} for testimonial in testimonials]

@api_router.get("/public/statistics", response_model=List[dict])
async def get_public_statistics():
    """Get curated statistics for public portfolio - only the most impressive ones"""
    try:
        # Import analytics functions
        from analytics_routes import (
            calculate_content_stats, 
            calculate_engagement_stats, 
            calculate_technical_stats, 
            calculate_business_stats
        )
        
        # Calculate all statistics
        all_stats = []
        try:
            content_stats = await calculate_content_stats()
            all_stats.extend(content_stats)
        except:
            pass
            
        try:
            engagement_stats = await calculate_engagement_stats()
            all_stats.extend(engagement_stats)
        except:
            pass
            
        try:
            technical_stats = await calculate_technical_stats()
            all_stats.extend(technical_stats)
        except:
            pass
            
        try:
            business_stats = await calculate_business_stats()
            all_stats.extend(business_stats)
        except:
            pass
        
        # Select only the most impressive statistics for public display
        public_worthy_stats = []
        
        for stat in all_stats:
            value = int(stat.value) if stat.value.isdigit() else 0
            
            # Criteria for public display - only show impressive numbers
            show_stat = False
            
            if stat.title == "Projets Totaux" and value >= 1:
                show_stat = True
            elif stat.title == "Taux d'Achèvement" and value >= 85:
                show_stat = True
            elif stat.title == "Articles Publiés" and value >= 3:
                show_stat = True
            elif stat.title == "Technologies" and value >= 5:
                show_stat = True
            elif stat.title == "Témoignages" and value >= 3:
                show_stat = True
            elif stat.title == "Niveau Expert" and value >= 1:
                show_stat = True
            elif stat.title == "Services" and value >= 2:
                show_stat = True
            elif stat.title == "Téléchargements" and value >= 100:
                show_stat = True
            elif stat.title == "Réservations" and value >= 5:
                show_stat = True
            elif stat.title == "Note Moyenne" and value >= 4:
                show_stat = True
            elif stat.title == "Abonnés Newsletter" and value >= 50:
                show_stat = True
            elif stat.title == "Compétences" and value >= 10:
                show_stat = True
            
            if show_stat:
                public_worthy_stats.append({
                    "title": stat.title,
                    "value": stat.value,
                    "suffix": stat.suffix,
                    "description": stat.description,
                    "icon": stat.icon,
                    "color": stat.color,
                    "order_index": len(public_worthy_stats)
                })
        
        # If we don't have enough impressive stats, add some default professional ones
        if len(public_worthy_stats) < 3:
            # Add some baseline professional stats
            default_stats = [
                {
                    "title": "Années d'Expérience",
                    "value": "5",
                    "suffix": "+",
                    "description": "Années d'expertise en cybersécurité",
                    "icon": "Award",
                    "color": "#10b981",
                    "order_index": 0
                },
                {
                    "title": "Projets Sécurisés", 
                    "value": "20",
                    "suffix": "+",
                    "description": "Infrastructures sécurisées avec succès",
                    "icon": "Shield",
                    "color": "#3b82f6",
                    "order_index": 1
                },
                {
                    "title": "Certifications",
                    "value": "3",
                    "suffix": "",
                    "description": "Certifications professionnelles obtenues",
                    "icon": "Award",
                    "color": "#f59e0b",
                    "order_index": 2
                },
                {
                    "title": "Satisfaction Client",
                    "value": "100",
                    "suffix": "%",
                    "description": "Taux de satisfaction des clients",
                    "icon": "Star",
                    "color": "#10b981",
                    "order_index": 3
                }
            ]
            
            # Merge with existing stats, avoiding duplicates
            existing_titles = {stat["title"] for stat in public_worthy_stats}
            for default_stat in default_stats:
                if default_stat["title"] not in existing_titles and len(public_worthy_stats) < 4:
                    public_worthy_stats.append(default_stat)
        
        # Limit to top 4 most impressive stats for clean display
        return public_worthy_stats[:4]
        
    except Exception as e:
        # Fallback to professional default stats if there's an error
        return [
            {
                "title": "Années d'Expérience",
                "value": "5",
                "suffix": "+",
                "description": "Années d'expertise en cybersécurité",
                "icon": "Award",
                "color": "#10b981",
                "order_index": 0
            },
            {
                "title": "Projets Sécurisés",
                "value": "20", 
                "suffix": "+",
                "description": "Infrastructures sécurisées avec succès",
                "icon": "Shield",
                "color": "#3b82f6",
                "order_index": 1
            },
            {
                "title": "Certifications",
                "value": "3",
                "suffix": "",
                "description": "Certifications professionnelles obtenues", 
                "icon": "Award",
                "color": "#f59e0b",
                "order_index": 2
            },
            {
                "title": "Satisfaction Client",
                "value": "100",
                "suffix": "%",
                "description": "Taux de satisfaction des clients",
                "icon": "Star", 
                "color": "#10b981",
                "order_index": 3
            }
        ]

@api_router.get("/public/social-links", response_model=List[dict])
async def get_public_social_links():
    """Get social links for public portfolio"""
    links = await db.social_links.find().sort("order_index", 1).to_list(100)
    return [{k: v for k, v in link.items() if k != "_id"} for link in links]

@api_router.get("/public/process-steps", response_model=List[dict])
async def get_public_process_steps():
    """Get process steps for public portfolio"""
    steps = await db.process_steps.find().sort("step", 1).to_list(100)
    return [{k: v for k, v in step.items() if k != "_id"} for step in steps]

@api_router.get("/public/blog", response_model=List[dict])
async def get_public_blog_posts():
    """Get published blog posts for public blog"""
    posts = await db.blog_posts.find({"published": True}).sort("created_at", -1).to_list(100)
    return [{k: v for k, v in post.items() if k != "_id"} for post in posts]

# Configure CORS middleware BEFORE including routers (CRITICAL FIX)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router in the main app AFTER CORS configuration
app.include_router(api_router)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
