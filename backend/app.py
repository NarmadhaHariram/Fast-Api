from fastapi import FastAPI, Depends, status, Request, Response, HTTPException
import schemas as schemas  
import models as models  
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import joblib

# Initialize FastAPI app
app = FastAPI()

# Configure Jinja2 templates
templates = Jinja2Templates(directory="../frontend/templates")

# Serve static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Create tables in the database
models.Base.metadata.create_all(bind=engine)

# Load the trained model
MODEL_NAME = 'model.joblib'  # Adjusted path to point to the model correctly

try:
    loaded_model = joblib.load(MODEL_NAME)  # Ensure the correct path
except Exception as e:
    print("Error loading model:", e)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# User defined functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def dict_to_dataframe(data_dict):
    # Convert a dictionary to a DataFrame
    df = pd.DataFrame([data_dict])  # Wrapping the dict in a list to create a DataFrame
    return df

@app.post("/predict/", status_code=status.HTTP_201_CREATED)
async def create(data: schemas.PredictionsHouse, db: Session = Depends(get_db)):
    """Gets the User data and predicts the house value"""
    try:
        df = dict_to_dataframe(data.dict())
        df = pd.get_dummies(df)

        # Make sure all expected features are present and fill missing columns with 0
        expected_columns = [
            'longitude', 'latitude', 'housing_median_age', 'total_rooms', 
            'total_bedrooms', 'population', 'households', 'median_income',
            'ocean_proximity_<1H OCEAN', 'ocean_proximity_INLAND',
            'ocean_proximity_ISLAND', 'ocean_proximity_NEAR BAY',
            'ocean_proximity_NEAR OCEAN'
        ]

        # Reindex the final DataFrame to ensure it has all expected columns
        df_final = df.reindex(columns=expected_columns, fill_value=0)

        # Make prediction
        predicted_value = loaded_model.predict(df_final)[0]

        new_prediction = models.PredictionsHouse(
            longitude=data.longitude,
            latitude=data.latitude,
            housing_median_age=data.housing_median_age,
            total_rooms=data.total_rooms,
            total_bedrooms=data.total_bedrooms,
            population=data.population,
            households=data.households,
            median_income=data.median_income,
            ocean_proximity=data.ocean_proximity,
            predicted_house_value=predicted_value
        )
        db.add(new_prediction)
        db.commit()
        db.refresh(new_prediction)
        return new_prediction  # Return as JSON response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/predictions')
def get_all_houseData(db: Session = Depends(get_db)):
    """Gets all previous predictions"""
    data = db.query(models.PredictionsHouse).all()
    return data

@app.get('/predictions/{id}', status_code=status.HTTP_200_OK)
def get_prediction_by_id(id: int, response: Response, db: Session = Depends(get_db)):
    """Gets all previous predictions and filters based on id"""
    data = db.query(models.PredictionsHouse).filter(models.PredictionsHouse.id == id).first()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Id not Found")
    return data

@app.get("/visualizations/{case}")
async def visualizations(case: str, db: Session = Depends(get_db)):
    """Gets the visualization based on predictions"""
    results = db.query(models.PredictionsHouse).all()

    # Convert the SQLAlchemy results to a list of dictionaries
    records = [record.__dict__ for record in results]

    # Remove the SQLAlchemy internal attributes like '_sa_instance_state'
    for record in records:
        record.pop('_sa_instance_state', None)

    # Create a DataFrame
    df = pd.DataFrame(records)
    
    if case == "top_5_house_values":
        # Sort the DataFrame by 'predicted_house_value' in descending order
        top_5 = df.sort_values(by='predicted_house_value', ascending=False).head(5)
        return top_5.to_dict(orient='records')

    elif case == "top_prices_by_location":
        top_prices = df.groupby(['longitude', 'latitude'])['predicted_house_value'].max().reset_index()
        return top_prices.to_dict(orient='records')

    elif case == "top_median_income":
        top_income = df.sort_values(by='median_income', ascending=False).head(5)
        return top_income.to_dict(orient='records')

    elif case == "most_populated_locations":
        most_populated = df.sort_values(by='population', ascending=False).head(5)
        return most_populated.to_dict(orient='records')

    elif case == "max_ocean_proximity":
        max_proximity = df.groupby('ocean_proximity')['predicted_house_value'].max().reset_index()
        return max_proximity.to_dict(orient='records')
