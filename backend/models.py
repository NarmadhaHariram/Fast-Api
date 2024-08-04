from datetime import datetime
from sqlalchemy import  Column, Integer, Float, String, DateTime
from database import Base
from typing import Optional


class House(Base):
    __tablename__ = 'housing'
    
    id=Column(Integer, primary_key=True, index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    housing_median_age= Column(Float)
    total_rooms= Column(Float)
    total_bedrooms= Column(Float)
    population= Column(Float)
    households= Column(Float)
    median_income= Column(Float)
    median_house_value= Column(Float)
    ocean_proximity= Column(String)

# Define the prediction model
class PredictionsHouse(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    longitude = Column(Float)
    latitude = Column(Float)
    housing_median_age = Column(Float)
    total_rooms = Column(Float)
    total_bedrooms = Column(Float)
    population = Column(Float)
    households = Column(Float)
    median_income = Column(Float)
    median_house_value= Column(Float)
    ocean_proximity = Column(String)
    median_house_value= Column(Float)
    predicted_house_value = Column(Float, nullable=True)  # Allow None values
    timestamp = Column(DateTime, default=datetime.utcnow)