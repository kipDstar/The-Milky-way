"""
Seed data script for development.

Creates sample companies, stations, farmers, and users for testing.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
import uuid

from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.company import Company
from app.models.station import Station
from app.models.farmer import Farmer
from app.models.officer import Officer, UserRole
from app.models.delivery import Delivery, QualityGrade, DeliverySource
from app.core.config import settings


def create_seed_data():
    """Create seed data for development."""
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_companies = db.query(Company).count()
        if existing_companies > 0:
            print("Seed data already exists. Skipping...")
            return
        
        print("Creating seed data...")
        
        # Create companies
        brookside = Company(
            name="Brookside Dairy Limited",
            code="BROOKSIDE",
            address="Ruiru, Kiambu County",
            contact_phone="+254712000000",
            contact_email="info@brookside.co.ke"
        )
        db.add(brookside)
        db.flush()
        
        # Create stations
        kipkaren = Station(
            name="Kipkaren Collection Centre",
            code="KIP001",
            company_id=brookside.id,
            address="Kipkaren, Nandi County",
            latitude=-0.1807,
            longitude=35.0557,
            contact_phone="+254712111111"
        )
        
        nairobi = Station(
            name="Nairobi Central Station",
            code="NRB001",
            company_id=brookside.id,
            address="Industrial Area, Nairobi",
            latitude=-1.3032,
            longitude=36.8437,
            contact_phone="+254712222222"
        )
        
        db.add_all([kipkaren, nairobi])
        db.flush()
        
        # Create officers (users)
        admin = Officer(
            name="Admin User",
            email=settings.SEED_ADMIN_EMAIL,
            phone="+254712999999",
            password_hash=hash_password(settings.SEED_ADMIN_PASSWORD),
            role=UserRole.ADMIN
        )
        
        manager = Officer(
            name="Jane Manager",
            email="manager@ddcpts.test",
            phone="+254712888888",
            password_hash=hash_password("Manager@123"),
            role=UserRole.MANAGER,
            station_id=kipkaren.id
        )
        
        officer = Officer(
            name="John Officer",
            email="officer@ddcpts.test",
            phone="+254712777777",
            password_hash=hash_password("Officer@123"),
            role=UserRole.OFFICER,
            station_id=kipkaren.id
        )
        
        db.add_all([admin, manager, officer])
        db.flush()
        
        # Create farmers
        farmers_data = [
            {
                "farmer_code": "FARM-00001",
                "name": "John Kiprop",
                "national_id": "12345678",
                "phone": "+254712345001",
                "station_id": kipkaren.id,
                "village": "Kipkaren West"
            },
            {
                "farmer_code": "FARM-00002",
                "name": "Mary Wanjiru",
                "national_id": "23456789",
                "phone": "+254712345002",
                "station_id": kipkaren.id,
                "village": "Kipkaren East"
            },
            {
                "farmer_code": "FARM-00003",
                "name": "Peter Ochieng",
                "national_id": "34567890",
                "phone": "+254712345003",
                "station_id": nairobi.id,
                "village": "Dagoretti"
            },
            {
                "farmer_code": "FARM-00004",
                "name": "Grace Njeri",
                "national_id": "45678901",
                "phone": "+254712345004",
                "station_id": kipkaren.id,
                "village": "Kipkaren Central"
            },
            {
                "farmer_code": "FARM-00005",
                "name": "Samuel Kamau",
                "national_id": "56789012",
                "phone": "+254712345005",
                "station_id": nairobi.id,
                "village": "Kawangware"
            },
        ]
        
        farmers = []
        for farmer_data in farmers_data:
            farmer = Farmer(**farmer_data)
            farmers.append(farmer)
            db.add(farmer)
        
        db.flush()
        
        # Create sample deliveries (last 7 days)
        import random
        from decimal import Decimal
        
        today = date.today()
        for i in range(7):
            delivery_date = today - timedelta(days=i)
            
            for farmer in farmers:
                # Random quantity between 5 and 20 liters
                quantity = Decimal(str(random.uniform(5, 20))).quantize(Decimal("0.001"))
                
                # Random fat content between 3.0 and 4.5
                fat_content = Decimal(str(random.uniform(3.0, 4.5))).quantize(Decimal("0.01"))
                
                # Determine quality grade based on fat content
                if fat_content >= Decimal("3.5"):
                    quality_grade = QualityGrade.A
                elif fat_content >= Decimal("3.0"):
                    quality_grade = QualityGrade.B
                else:
                    quality_grade = QualityGrade.C
                
                delivery = Delivery(
                    farmer_id=farmer.id,
                    station_id=farmer.station_id,
                    officer_id=officer.id,
                    delivery_date=delivery_date,
                    quantity_liters=quantity,
                    fat_content=fat_content,
                    quality_grade=quality_grade,
                    source=DeliverySource.MOBILE
                )
                db.add(delivery)
        
        # Commit all changes
        db.commit()
        
        print("Seed data created successfully!")
        print("\n" + "="*50)
        print("DEVELOPMENT CREDENTIALS")
        print("="*50)
        print(f"Admin: {settings.SEED_ADMIN_EMAIL} / {settings.SEED_ADMIN_PASSWORD}")
        print(f"Manager: manager@ddcpts.test / Manager@123")
        print(f"Officer: officer@ddcpts.test / Officer@123")
        print("="*50 + "\n")
    
    except Exception as e:
        print(f"Error creating seed data: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
