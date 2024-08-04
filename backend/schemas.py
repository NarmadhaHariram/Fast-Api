from typing import List, Optional
from pydantic import BaseModel

class House(BaseModel):
    longitude:float
    latitude:float
    housing_median_age:float
    total_rooms:float
    total_bedrooms:float
    population:float
    households:float
    # median_house_value: float
    median_income:float
    ocean_proximity: str
    
class PredictionsHouse(BaseModel):
    longitude:float
    latitude:float
    housing_median_age:float
    total_rooms:float
    total_bedrooms:float
    population:float
    households:float
    median_income:float
    ocean_proximity: str
    