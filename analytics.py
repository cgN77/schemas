
"""
Request and Response schemas for the Analytics Generation endpoint.

POST /internal/analytics/generate

This endpoint receives query results after SQL execution and generates:

- Analytical insights
- Statistical summaries
- Charts
- Narratives
- Forecasts (if requested)
- Anomaly detection results

The output is consumed by the response formatter
and frontend visualization layer.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================
# Request Models
# ============================================================

class IntentEntity(BaseModel):
    """Entity extracted during intent analysis."""

    type: str

    value: str

    field: str

    class Config:
        extra = "forbid"


class AnalyticsIntent(BaseModel):
    """Intent information from Intent Analyzer."""

    primary: str

    entities: List[IntentEntity] = []

    class Config:
        extra = "forbid"


class AxisSpec(BaseModel):

    field: str

    label: str

    class Config:
        extra = "forbid"


class ChartConfig(BaseModel):

    x_axis: Optional[AxisSpec] = None

    y_axis: Optional[AxisSpec] = None

    class Config:
        extra = "forbid"


class ChartSpec(BaseModel):

    recommended_chart_type: str

    chart_config: ChartConfig

    class Config:
        extra = "forbid"


class QueryResultData(BaseModel):
    """
    SQL execution result.
    """

    rows: List[Dict[str, Any]]

    row_count: int

    execution_time_ms: int

    class Config:
        extra = "forbid"


class ChartPreferences(BaseModel):

    type: str = "auto"

    format: str = "png"

    width: int = 800

    height: int = 400

    dpi: int = 96

    class Config:
        extra = "forbid"


class NarrativePreferences(BaseModel):

    length: str = "medium"

    include_insights: bool = True

    tone: str = "professional"

    class Config:
        extra = "forbid"


class AnalyticsGenerateRequest(BaseModel):
    """
    Request schema for analytics generation.
    """

    request_id: str = Field(
        ...,
        description="Unique request identifier"
    )

    intent: AnalyticsIntent

    chart_spec: Optional[ChartSpec] = None

    data: QueryResultData

    chart_preferences: ChartPreferences

    narrative_preferences: NarrativePreferences

    class Config:
        extra = "forbid"


# ============================================================
# Response Models
# ============================================================

class GeneratedChart(BaseModel):
    """
    Generated visualization.
    """

    type: str

    format: str

    width: int

    height: int

    base64: str

    alt_text: str

    size_bytes: int

    generation_time_ms: int

    class Config:
        extra = "forbid"


class ForecastResult(BaseModel):
    """
    Forecasting output.
    """

    method: str

    horizon: str

    confidence_interval: str

    predictions: List[Dict[str, Any]]

    disclaimer: str

    class Config:
        extra = "forbid"


class AnomalyResult(BaseModel):
    """
    Detected anomalies.
    """

    field: str

    value: Any

    anomaly_score: float

    reason: str

    class Config:
        extra = "forbid"


class NarrativeMetadata(BaseModel):

    length: int

    sentences: int

    insights_included: bool

    generation_time_ms: int

    class Config:
        extra = "forbid"


class AnalyticsPerformance(BaseModel):

    total_time_ms: int

    chart_generation_ms: int

    narrative_generation_ms: int

    model_used: str

    class Config:
        extra = "forbid"


class AnalyticsGenerateResponse(BaseModel):
    """
    Response schema for analytics generation.
    """

    status: str

    request_id: str

    chart: Optional[GeneratedChart] = None

    narrative: str

    narrative_metadata: NarrativeMetadata

    forecast: Optional[ForecastResult] = None

    anomalies: List[AnomalyResult] = []

    key_insights: List[str] = []

    performance: AnalyticsPerformance

    class Config:
        extra = "forbid"

        json_schema_extra = {
            "example": {
                "status": "success",
                "request_id": "req_20260605_143022_a1b2c3d4",
                "narrative": "Revenue increased 12% quarter over quarter.",
                "key_insights": [
                    "North region contributed 41.6% of total revenue.",
                    "Revenue concentration is highest in two regions."
                ]
            }
        }
