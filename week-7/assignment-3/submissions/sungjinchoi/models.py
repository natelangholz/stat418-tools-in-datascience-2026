"""Pydantic request and response models for the prediction API."""
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator

N_FEATURES = 7
FEATURE_ORDER = "age, appearances, goals, assists, minutes, yellow_cards, red_cards"


class PredictionRequest(BaseModel):
    """A single prediction request."""

    model_config = ConfigDict(protected_namespaces=())

    features: List[float] = Field(..., description=f"Exactly {N_FEATURES} values: {FEATURE_ORDER}")
    model_version: str = Field(default="v1", description="Requested model version")

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: List[float]) -> List[float]:
        """Require exactly N_FEATURES non-negative values."""
        if len(v) != N_FEATURES:
            raise ValueError(f"features must have exactly {N_FEATURES} values ({FEATURE_ORDER})")
        if any(x < 0 for x in v):
            raise ValueError("features must be non-negative")
        return v


class PredictionResponse(BaseModel):
    """A single prediction result."""

    model_config = ConfigDict(protected_namespaces=())

    prediction: float = Field(..., description="Predicted market value in EUR")
    confidence: float = Field(..., description="Confidence score in [0, 1]")
    model_version: str
    request_id: str


class BatchPredictionRequest(BaseModel):
    """A batch of prediction requests."""

    model_config = ConfigDict(protected_namespaces=())

    instances: List[List[float]] = Field(..., max_length=100, description="Up to 100 feature vectors")

    @field_validator("instances")
    @classmethod
    def validate_instances(cls, v: List[List[float]]) -> List[List[float]]:
        """Require a non-empty batch where every row has N_FEATURES non-negative values."""
        if not v:
            raise ValueError("instances must not be empty")
        for i, row in enumerate(v):
            if len(row) != N_FEATURES:
                raise ValueError(f"instance {i} must have exactly {N_FEATURES} values")
            if any(x < 0 for x in row):
                raise ValueError(f"instance {i} has negative values")
        return v


class BatchPredictionResponse(BaseModel):
    """A batch of prediction results."""

    model_config = ConfigDict(protected_namespaces=())

    predictions: List[float] = Field(..., description="Predicted market values in EUR")
    count: int
    model_version: str
