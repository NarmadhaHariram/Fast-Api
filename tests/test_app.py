import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app import app, get_db
from backend import models
from backend.database import Base
from backend import schemas
from backend.database import SessionLocal

# Create a new database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a testing database session
@pytest.fixture(scope="module")
def test_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    # Drop the testing database tables after tests
    Base.metadata.drop_all(bind=engine)

# Dependency override for testing
app.dependency_overrides[get_db] = lambda: test_db

@pytest.fixture(scope="module")
def client():
    yield TestClient(app)

# Example test case
def test_get_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "html" in response.headers["content-type"]

def test_get_all_predictions(client):
    response = client.get("/predictions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.parametrize("case, expected_count", [
    ("top_5_house_values", 5),
    ("top_prices_by_location", 1),
    ("top_median_income", 5),
    ("most_populated_locations", 5),
    ("max_ocean_proximity", 5),
])
def test_visualizations_all(client, case, expected_count):
    response = client.get(f"/visualizations/{case}")
    assert response.status_code == 200
    assert len(response.json()) <= expected_count

# Create a testing database session
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# Example test case
def test_predict(client):
    # Prepare your data
    data = {
        "longitude": -118.24,
        "latitude": 34.12,
        "housing_median_age": 30,
        "total_rooms": 1000,
        "total_bedrooms": 200,
        "population": 5000,
        "households": 1500,
        "median_income": 3.5,
        "ocean_proximity": "<1H OCEAN"
    }
    
    response = client.post("/predict/", json=data)
    assert response.status_code == 201  # Changed from 500 to 201

def test_get_prediction_by_id(client):
    # You need to create an entry first before you can query by ID
    new_data = {
        "longitude": -118.24,
        "latitude": 34.12,
        "housing_median_age": 30,
        "total_rooms": 1000,
        "total_bedrooms": 200,
        "population": 5000,
        "households": 1500,
        "median_income": 3.5,
        "ocean_proximity": "<1H OCEAN"
    }
    
    create_response = client.post("/predict/", json=new_data)
    created_id = create_response.json().get("id")
    
    response = client.get(f"/predictions/{created_id}")
    assert response.status_code == 200
    assert response.json()["id"] == created_id

def test_get_prediction_by_invalid_id(client):
    response = client.get("/predictions/999999")  # Assuming this ID does not exist
    assert response.status_code == 404

# Additional test for visualizations
def test_visualizations(client):
    response = client.get("/visualizations/top_5_house_values")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
