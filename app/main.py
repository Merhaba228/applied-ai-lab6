import pickle
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field

MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "taxi_model.pkl"


class Trip(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)

    vendor_id: int = Field(ge=1, le=2, examples=[1])
    passenger_count: int = Field(ge=1, le=6, examples=[2])
    pickup_longitude: float = Field(ge=-75, le=-72, examples=[-74.0064])
    pickup_latitude: float = Field(ge=39, le=42, examples=[40.7337])
    pickup_hour: int = Field(ge=0, le=23, examples=[20])
    pickup_weekday: int = Field(ge=0, le=6, examples=[5], description="0 — понедельник")


class Prediction(BaseModel):
    predicted_class: Literal[0, 1]
    long_trip_probability: float = Field(ge=0, le=1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with MODEL_PATH.open("rb") as file:
        app.state.model = pickle.load(file)
    yield


app = FastAPI(title="NYC Taxi. Лабораторная работа №6", lifespan=lifespan)


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse("/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=Prediction)
def predict(trip: Trip, request: Request):
    model = request.app.state.model
    features = pd.DataFrame([trip.model_dump()], columns=model.feature_names_in_)
    probability = float(model.predict_proba(features)[0, 1])
    return Prediction(
        predicted_class=int(probability > 0.5),
        long_trip_probability=probability,
    )
