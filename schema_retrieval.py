
"""
Request and Response schemas for the Schema Retrieval endpoint.

POST /internal/schema/retrieve

This endpoint performs semantic search against the schema vector index
and returns the most relevant database objects for SQL generation.

The output is consumed by:
- Intent Analyzer
- SQL Generator
- Query Planner
"""

from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# Request Models
# ============================================================

class SchemaFilter(BaseModel):
    """Optional metadata filters applied during retrieval."""

    object_type: Optional[str] = Field(
        default=None,
        description="Filter by object type such as table or view"
    )

    schema_name: Optional[str] = Field(
        default=None,
        description="Database schema name"
    )

    class Config:
        extra = "forbid"


class HybridSearchConfig(BaseModel):
    """Configuration for hybrid keyword + vector search."""

    enabled: bool = False

    alpha: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Weight between vector similarity and keyword similarity"
    )

    class Config:
        extra = "forbid"


class SchemaRetrieveRequest(BaseModel):
    """
    Request schema for semantic schema retrieval.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language analytics query"
    )

    query_vector: Optional[List[float]] = Field(
        default=None,
        description="Embedding vector of the user query"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of schema objects to retrieve"
    )

    similarity_threshold: float = Field(
        default=0.65,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score required"
    )

    collection_name: str = Field(
        default="schema_embeddings",
        description="Target vector collection"
    )

    filter: Optional[SchemaFilter] = None

    include_metadata: bool = True

    include_vector: bool = False

    hybrid_search: HybridSearchConfig = Field(
        default_factory=HybridSearchConfig
    )

    class Config:
        extra = "forbid"

        json_schema_extra = {
            "example": {
                "query": "Show me sales revenue by region for last quarter",
                "top_k": 5,
                "similarity_threshold": 0.65,
                "collection_name": "schema_embeddings",
                "include_metadata": True,
                "include_vector": False
            }
        }


# ============================================================
# Response Models
# ============================================================

class ColumnSchema(BaseModel):
    """Column metadata."""

    name: str

    type: str

    is_primary_key: bool = False

    is_foreign_key: bool = False

    is_nullable: bool = True


class ForeignKeySchema(BaseModel):
    """Foreign key metadata."""

    column: str

    references: str


class TableSchemaMetadata(BaseModel):
    """Retrieved schema metadata."""

    table_name: str

    object_type: str

    schema_name: Optional[str] = None

    description: Optional[str] = None

    columns: List[ColumnSchema] = []

    primary_keys: List[str] = []

    foreign_keys: List[ForeignKeySchema] = []

    row_count: Optional[int] = None

    schema_text: Optional[str] = None


class SchemaSearchResult(BaseModel):
    """Single schema retrieval result."""

    record_id: str = Field(
        ...,
        description="Unique schema record identifier"
    )

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0
    )

    metadata: TableSchemaMetadata

    vector: Optional[List[float]] = None


class RetrievalPerformance(BaseModel):
    """Performance metrics."""

    vector_search_ms: int

    total_time_ms: int


class SchemaRetrieveResponse(BaseModel):
    """
    Response schema for semantic schema retrieval.
    """

    status: str = Field(
        ...,
        description="success or failure"
    )

    search_id: str = Field(
        ...,
        description="Unique search execution identifier"
    )

    query: str

    total_results: int

    results: List[SchemaSearchResult]

    performance: RetrievalPerformance

    class Config:
        extra = "forbid"

        json_schema_extra = {
            "example": {
                "status": "success",
                "search_id": "search_12345",
                "query": "Show revenue by region",
                "total_results": 3,
                "results": [],
                "performance": {
                    "vector_search_ms": 45,
                    "total_time_ms": 52
                }
            }
        }
