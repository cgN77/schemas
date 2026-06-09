
"""
Request and Response schemas for the Few-Shot Retrieval endpoint.

POST /internal/fewshot/retrieve

This endpoint performs semantic search against the few-shot example
vector index and returns previously successful NL-to-SQL examples.

The output is consumed by:
- Prompt Builder
- SQL Generator
- SQL Validator
"""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field


# ============================================================
# Request Models
# ============================================================

class FewShotFilter(BaseModel):
    """Optional filters for few-shot retrieval."""

    database_type: Optional[str] = Field(
        default=None,
        description="SQL dialect such as postgres, snowflake, bigquery"
    )

    domain: Optional[str] = Field(
        default=None,
        description="Business domain such as sales, finance, healthcare"
    )

    class Config:
        extra = "forbid"


class HybridSearchConfig(BaseModel):
    """Hybrid keyword and vector search configuration."""

    enabled: bool = False

    alpha: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Weight between vector similarity and keyword similarity"
    )

    class Config:
        extra = "forbid"


class FewShotRetrieveRequest(BaseModel):
    """
    Request schema for few-shot retrieval.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language analytics query"
    )

    query_vector: Optional[List[float]] = Field(
        default=None,
        description="Embedding vector for semantic search"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of examples to retrieve"
    )

    similarity_threshold: float = Field(
        default=0.65,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score"
    )

    collection_name: str = Field(
        default="fewshot_embeddings",
        description="Target vector collection"
    )

    filter: Optional[FewShotFilter] = None

    include_metadata: bool = True

    include_vector: bool = False

    hybrid_search: HybridSearchConfig = Field(
        default_factory=HybridSearchConfig
    )

    class Config:
        extra = "forbid"

        json_schema_extra = {
            "example": {
                "query": "Show revenue by region for last quarter",
                "top_k": 5,
                "similarity_threshold": 0.70,
                "collection_name": "fewshot_embeddings"
            }
        }


# ============================================================
# Response Models
# ============================================================

class FewShotMetadata(BaseModel):
    """
    Metadata for a retrieved few-shot example.
    """

    query_text: str

    sql: str

    database_type: Optional[str] = None

    domain: Optional[str] = None

    usage_count: int = 0

    success_rate: Optional[float] = None

    avg_execution_time_ms: Optional[int] = None

    tables_used: List[str] = []

    columns_used: List[str] = []

    sql_explanation: Optional[str] = None

    created_at: Optional[datetime] = None

    last_used_at: Optional[datetime] = None


class FewShotSearchResult(BaseModel):
    """
    Single retrieved few-shot example.
    """

    record_id: str = Field(
        ...,
        description="Unique few-shot example identifier"
    )

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )

    metadata: FewShotMetadata

    vector: Optional[List[float]] = None


class RetrievalPerformance(BaseModel):
    """
    Retrieval performance metrics.
    """

    vector_search_ms: int

    total_time_ms: int


class FewShotRetrieveResponse(BaseModel):
    """
    Response schema for few-shot retrieval.
    """

    status: str = Field(
        ...,
        description="success or failure"
    )

    search_id: str = Field(
        ...,
        description="Unique retrieval execution identifier"
    )

    query: str

    total_results: int

    results: List[FewShotSearchResult]

    performance: RetrievalPerformance

    class Config:
        extra = "forbid"

        json_schema_extra = {
            "example": {
                "status": "success",
                "search_id": "fs_123456",
                "query": "Show revenue by region for last quarter",
                "total_results": 2,
                "results": [
                    {
                        "record_id": "past_q_001",
                        "similarity_score": 0.92,
                        "metadata": {
                            "query_text": "Revenue by region",
                            "sql": "SELECT region, SUM(revenue) FROM sales GROUP BY region",
                            "database_type": "postgres",
                            "domain": "sales",
                            "usage_count": 47,
                            "tables_used": ["sales"]
                        }
                    }
                ],
                "performance": {
                    "vector_search_ms": 18,
                    "total_time_ms": 24
                }
            }
        }
