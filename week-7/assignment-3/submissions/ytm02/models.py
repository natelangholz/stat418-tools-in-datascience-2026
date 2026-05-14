"""Pydantic request/response models for the ML API."""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    """Single prediction request with 4 Iris features."""

    features: List[float] = Field(
        ...,
        description="Input features: [sepal_length, sepal_width, petal_length, petal_width]",
        min_length=4,
        max_length=4,
    )
    model_version: str = Field(default="v1", description="Model version to use")

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: List[float]) -> List[float]:
        """Ensure exactly 4 non-negative feature values are provided."""
        if len(v) != 4:
            raise ValueError("Exactly 4 features required: sepal_length, sepal_width, petal_length, petal_width")
        if any(f < 0 for f in v):
            raise ValueError("All feature values must be non-negative")
        return v


class PredictionResponse(BaseModel):
    """Response for a single prediction."""

    prediction: float = Field(..., description="Predicted class index (0=setosa, 1=versicolor, 2=virginica)")
    predicted_class: str = Field(..., description="Human-readable class name")
    confidence: float = Field(..., description="Confidence score (0-1)")
    model_version: str = Field(..., description="Model version used")
    request_id: str = Field(..., description="Unique request identifier")


class BatchPredictionRequest(BaseModel):
    """Batch prediction request supporting up to 100 instances."""

    instances: List[List[float]] = Field(
        ...,
        description="List of feature arrays, each with 4 values",
        max_length=100,
    )

    @field_validator("instances")
    @classmethod
    def validate_instances(cls, v: List[List[float]]) -> List[List[float]]:
        """Ensure each instance has exactly 4 features."""
        if len(v) == 0:
            raise ValueError("At least one instance required")
        for i, instance in enumerate(v):
            if len(instance) != 4:
                raise ValueError(f"Instance {i}: expected 4 features, got {len(instance)}")
        return v


class BatchPredictionResponse(BaseModel):
    """Response for a batch prediction."""

    predictions: List[float] = Field(..., description="Predicted class indices")
    predicted_classes: List[str] = Field(..., description="Human-readable class names")
    count: int = Field(..., description="Number of predictions returned")
    model_version: str = Field(..., description="Model version used")


class ModelInfo(BaseModel):
    """Model metadata response."""

    name: str
    version: str
    description: str
    features: List[str]
    classes: List[str]
    accuracy: float


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class ReadyResponse(BaseModel):
    """Readiness check response."""

    status: str
    model_loaded: bool
