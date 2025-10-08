"""Sample tests for delivery endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import date
from decimal import Decimal

from app.main import app
from app.core.database import get_db
from app.models.farmer import Farmer
from app.models.station import Station
from app.models.company import Company
from app.models.delivery import Delivery

client = TestClient(app)


class TestDeliveryEndpoints:
    """Test delivery management endpoints."""
    
    def test_create_delivery_success(self, db_session, auth_headers):
        """Test successful delivery creation."""
        # Setup test data
        company = Company(name="Test Co", code="TEST")
        db_session.add(company)
        db_session.flush()
        
        station = Station(
            name="Test Station",
            code="TS001",
            company_id=company.id
        )
        db_session.add(station)
        db_session.flush()
        
        farmer = Farmer(
            farmer_code="FARM-TEST-001",
            name="Test Farmer",
            phone="+254712345678",
            station_id=station.id
        )
        db_session.add(farmer)
        db_session.commit()
        
        # Create delivery
        delivery_data = {
            "farmer_code": "FARM-TEST-001",
            "station_id": str(station.id),
            "delivery_date": date.today().isoformat(),
            "quantity_liters": 10.5,
            "fat_content": 3.5,
            "quality_grade": "A",
            "remarks": "Good quality"
        }
        
        response = client.post(
            "/api/v1/deliveries",
            json=delivery_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["farmer_code"] == "FARM-TEST-001"
        assert float(data["quantity_liters"]) == 10.5
        assert data["quality_grade"] == "A"
    
    def test_create_delivery_invalid_farmer(self, auth_headers):
        """Test delivery creation with non-existent farmer."""
        delivery_data = {
            "farmer_code": "INVALID-CODE",
            "station_id": "00000000-0000-0000-0000-000000000000",
            "delivery_date": date.today().isoformat(),
            "quantity_liters": 10.5,
            "quality_grade": "B"
        }
        
        response = client.post(
            "/api/v1/deliveries",
            json=delivery_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_delivery_validation_error(self, db_session, auth_headers):
        """Test delivery creation with invalid quantity."""
        # Setup test data
        company = Company(name="Test Co", code="TEST")
        db_session.add(company)
        db_session.flush()
        
        station = Station(
            name="Test Station",
            code="TS001",
            company_id=company.id
        )
        db_session.add(station)
        db_session.flush()
        
        farmer = Farmer(
            farmer_code="FARM-TEST-002",
            name="Test Farmer 2",
            phone="+254712345679",
            station_id=station.id
        )
        db_session.add(farmer)
        db_session.commit()
        
        delivery_data = {
            "farmer_code": "FARM-TEST-002",
            "station_id": str(station.id),
            "delivery_date": date.today().isoformat(),
            "quantity_liters": -5.0,  # Invalid: negative
            "quality_grade": "B"
        }
        
        response = client.post(
            "/api/v1/deliveries",
            json=delivery_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_get_deliveries_list(self, db_session, auth_headers):
        """Test retrieving list of deliveries."""
        response = client.get(
            "/api/v1/deliveries",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_deliveries_filter_by_date(self, db_session, auth_headers):
        """Test filtering deliveries by date."""
        today = date.today().isoformat()
        
        response = client.get(
            f"/api/v1/deliveries?date={today}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        deliveries = response.json()
        
        for delivery in deliveries:
            assert delivery["delivery_date"] == today


# Fixtures

@pytest.fixture
def db_session():
    """Provide database session for tests."""
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_headers():
    """Provide authentication headers for tests."""
    # Mock authentication - in real tests, log in first
    return {
        "Authorization": "Bearer test-token"
    }
