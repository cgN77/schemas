"""
Request and Response schemas for the Intent Analysis endpoint.

POST /internal/intent/analyze

This endpoint analyzes a user's natural language analytics query and determines:

- Primary intent
- Query classification
- Query execution plan
- Extracted entities
- Recommended visualization
- Clarification requirements

The output is consumed by the SQL Generator, Analytics Engine,
and Visualization Selector services.
"""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


# ============================================================
# Request Models
# ============================================================

from typing import List, Optional

from src.api.schemas.chat_request import (
    ChatMessage,
    ChatMetaData
)


class ConversationContext(BaseModel):
    """
    Previous conversation context used for
    intent disambiguation and follow-up analysis.
    """

    current_message: ChatMessage = Field(
        ...,
        description="Current user message being analyzed"
    )

    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation messages"
    )

    metadata: Optional[ChatMetaData] = Field(
        default=None,
        description="Session and conversation metadata"
    )

    class Config:
        extra = "forbid"

class UserPreferences(BaseModel):
    """User visualization and presentation preferences."""

    default_chart_type: Optional[str] = None
    preferred_color_scheme: Optional[str] = None


class UserContext(BaseModel):
    """Information about the requesting user."""

    user_id: str

    role: Optional[str] = Field(
        default=None,
        description="User role such as analyst, executive, or data_scientist"
    )

    preferences: Optional[UserPreferences] = None


class IntentOptions(BaseModel):
    """Feature flags controlling analysis behavior."""

    extract_entities: bool = True

    detect_chart_type: bool = True

    return_confidence_scores: bool = True

    return_alternatives: bool = True


class IntentAnalyzeRequest(BaseModel):
    """
    Request schema for intent analysis.

    Receives a natural language analytics query and
    determines how downstream services should process it.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language analytics query"
    )

    conversation_context: Optional[ConversationContext] = None

    user_context: Optional[UserContext] = None

    domain: str = Field(
        default="analytics",
        description="Business domain"
    )

    options: IntentOptions = Field(
        default_factory=IntentOptions
    )

    class Config:
        extra = "forbid"

        json_schema_extra = {
            "example": {
                "query": "Show revenue by region for last quarter",
                "conversation_context": {
                    "previous_query": "Show total revenue",
                    "previous_intent": "aggregation",
                    "session_id": "sess_123"
                },
                "user_context": {
                    "user_id": "user_789",
                    "role": "analyst"
                },
                "domain": "analytics"
            }
        }


# ============================================================
# Response Models
# ============================================================

class IntentAlternative(BaseModel):
    """Alternative intent prediction."""

    intent: str

    confidence: float


class IntentResult(BaseModel):
    """Primary intent classification."""

    primary: str

    confidence: float

    alternatives: List[IntentAlternative] = []


class QueryClassification(BaseModel):
    """
    High-level execution classification.

    Used by orchestration services to determine
    downstream processing requirements.
    """

    query_type: str = Field(
        ...,
        description=(
            "aggregation, comparison, forecasting, "
            "trend_analysis, anomaly_detection, "
            "information_retrieval, visualization"
        )
    )

    requires_sql: bool

    requires_chart: bool

    requires_forecast: bool

    requires_narrative: bool

    requires_clarification: bool


class QueryFilter(BaseModel):
    """Structured filter extracted from the query."""

    field: str

    operator: str

    value: Any


class QueryPlan(BaseModel):
    """
    Structured execution plan generated from
    the user's natural language request.
    """

    metric: Optional[str] = None

    dimensions: List[str] = []

    filters: List[QueryFilter] = []

    aggregations: List[str] = []

    time_grain: Optional[str] = None

    forecast_horizon: Optional[str] = None


class ExtractedEntity(BaseModel):
    """Entity extracted from the user query."""

    type: str

    value: str

    confidence: float

    normalized_value: Optional[Dict[str, Any]] = None

    chart_mapping: Optional[str] = None


class AxisSpec(BaseModel):
    """Axis configuration for visualization."""

    field: str

    label: str

    data_type: str

    aggregation: Optional[str] = None


class ChartConfig(BaseModel):
    """Recommended chart configuration."""

    x_axis: Optional[AxisSpec] = None

    y_axis: Optional[AxisSpec] = None

    color: Optional[str] = None

    facet: Optional[str] = None


class ChartAlternative(BaseModel):
    """Alternative chart recommendation."""

    chart_type: str

    confidence: float


class ChartSpec(BaseModel):
    """Visualization recommendation."""

    recommended_chart_type: str

    confidence: float

    alternatives: List[ChartAlternative] = []

    chart_config: Optional[ChartConfig] = None

    reasoning: Optional[str] = None


class LanguageAnalysis(BaseModel):
    """Natural language characteristics."""

    complexity: str

    has_negation: bool

    has_comparison: bool

    has_condition: bool


class IntentAnalysisMetadata(BaseModel):
    """Execution metadata."""

    processing_time_ms: int

    model_used: str


class IntentAnalyzeResponse(BaseModel):
    """
    Response schema for intent analysis.

    Returned after the query has been analyzed
    and prepared for SQL generation.
    """

    status: str = Field(
        ...,
        description="success or failure"
    )

    conversation_context=ConversationContext

    user_context=Optional[UserContext] = None

    intent: IntentResult

    classification: QueryClassification

    query_plan: QueryPlan

    entities: List[ExtractedEntity] = []

    chart_spec: Optional[ChartSpec] = None

    language_analysis: Optional[LanguageAnalysis] = None

    clarification_required: bool = False

    clarification_questions: List[str] = []

    performance: IntentAnalysisMetadata

    class Config:
        extra = "forbid"

        json_schema_extra = {
            "example": {
                "status": "success",
                "query": "Show revenue by region for last quarter",
                "intent": {
                    "primary": "aggregation",
                    "confidence": 0.94
                },
                "classification": {
                    "query_type": "aggregation",
                    "requires_sql": True,
                    "requires_chart": True,
                    "requires_forecast": False,
                    "requires_narrative": True,
                    "requires_clarification": False
                },
                "query_plan": {
                    "metric": "revenue",
                    "dimensions": ["region"],
                    "aggregations": ["sum"],
                    "time_grain": "quarter"
                },
                "clarification_required": False,
                "clarification_questions": [],
                "performance": {
                    "processing_time_ms": 45,
                    "model_used": "gemini-2.5-flash"
                }
            }
        }
