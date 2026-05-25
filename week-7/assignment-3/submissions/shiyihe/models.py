from typing import List
from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    features: List[float] = Field(..., description="Input features: [wt, hp, cyl]")
    model_version: str = Field(default="v1", description="Model version")

    @field_validator("features")
    @classmethod
    def validate_features(cls, value: List[float]) -> List[float]:
        if len(value) != 3:
            raise ValueError("features must contain exactly 3 values: wt, hp, cyl")
        return value


class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    model_version: str
    request_id: str


class BatchPredictionRequest(BaseModel):
    instances: List[List[float]] = Field(..., max_length=100)

    @field_validator("instances")
    @classmethod
    def validate_instances(cls, value: List[List[float]]) -> List[List[float]]:
        if len(value) == 0:
            raise ValueError("instances cannot be empty")
        for row in value:
            if len(row) != 3:
                raise ValueError("each instance must contain exactly 3 values")
        return value


class BatchPredictionResponse(BaseModel):
    predictions: List[float]
    confidences: List[float]
    count: int
    model_version: str
