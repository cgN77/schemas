from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID

# UI Components (Frontend Rendering)

class ButtonAction(BaseModel):
    """Button configuration for UI actions"""
    label: str = Field(..., description="Button text")
    action_id: str = Field(..., description="Unique action identifier (e.g., 'export_pdf', 'download_chart')")
    style: Optional[Literal["primary", "secondary", "danger", "outline"]] = Field(
        default=None, description="Button visual style"
    )
    disabled: bool = Field(default=False, description="Whether button is disabled")

class RichDisplayContent(BaseModel):
    """Rich content for enhanced UI display"""
    html: Optional[str] = Field(default=None, description="HTML content")
    markdown: Optional[str] = Field(default=None, description="Markdown content")
    chart_config: Optional[Dict[str, Any]] = Field(default=None, description="Chart configuration")

class UILayout(BaseModel):
    """Complete UI specification for frontend rendering"""
    rich_content: Optional[RichDisplayContent] = Field(default=None, description="Enhanced display content")
    primary_buttons: List[ButtonAction] = Field(default_factory=list, description="Primary action buttons")
    secondary_buttons: List[ButtonAction] = Field(default_factory=list, description="Secondary action buttons")


# Analytics Core Models

class ChartVisualization(BaseModel):
    """Chart specification for data visualization"""
    type: Literal["bar", "line", "pie", "scatter", "area", "table", "metric"] = Field(..., description="Chart type")
    title: Optional[str] = Field(default=None, description="Chart title")
    data: List[Dict[str, Any]] = Field(..., description="Chart data")
    x_axis_config: Optional[Dict[str, str]] = Field(default=None, description="X-axis configuration")
    y_axis_config: Optional[Dict[str, str]] = Field(default=None, description="Y-axis configuration")
    color_palette: Optional[List[str]] = Field(default=None, description="Color palette")
    embedded_image: Optional[str] = Field(default=None, description="Base64 encoded chart image")

class GeneratedSQL(BaseModel):
    """SQL query generated from natural language"""
    query_text: str = Field(..., description="Generated SQL query")
    source_tables: List[str] = Field(..., description="Tables accessed")
    target_columns: List[str] = Field(..., description="Columns accessed")
    aggregation_methods: List[str] = Field(default_factory=list, description="Aggregation functions used")
    run_time_ms: Optional[int] = Field(default=None, description="Query execution time in milliseconds")
    result_count: Optional[int] = Field(default=None, description="Number of rows returned")

class DataInsight(BaseModel):
    """Individual insight extracted from query results"""
    category: Literal["trend", "anomaly", "comparison", "summary", "recommendation"] = Field(..., description="Insight category")
    importance: Literal["low", "medium", "high", "critical"] = Field(default="medium", description="Insight importance level")
    headline: str = Field(..., description="Short insight title")
    description: str = Field(..., description="Detailed insight explanation")
    key_value: Optional[Any] = Field(default=None, description="Key metric value if applicable")
    confidence_score: Optional[float] = Field(default=None, description="Confidence score (0-1)", ge=0, le=1)


# Execution Tracking


class ExecutionTrace(BaseModel):
    """Execution trace for a single processing step"""
    component_name: str = Field(..., description="Component that executed", examples=['sql_generator', 'chart_builder'])
    status: Literal["pending", "running", "completed", "failed"] = Field(..., description="Execution status")
    duration_seconds: float = Field(..., description="Execution time in seconds")
    log_messages: List[str] = Field(default_factory=list, description="Execution log messages")

class ProcessingIssue(BaseModel):
    """Issue or warning encountered during processing"""
    source_component: str = Field(..., description="Component that raised the issue")
    severity: Literal["info", "warning", "error"] = Field(..., description="Issue severity")
    error_code: str = Field(..., description="Error code (e.g., 'SQL_PARSE_ERROR', 'NO_DATA_FOUND')")
    user_message: str = Field(..., description="User-friendly error message")
    technical_details: Dict[str, Any] = Field(default_factory=dict, description="Technical details for debugging")

class ComponentMetadata(BaseModel):
    """Metadata for a single processing component"""
    component_name: str = Field(..., description="Name of the component")
    execution_details: Dict[str, Any] = Field(..., description="Component-specific execution details")


# ============================================
# Response Metadata
# ============================================

class ResponseTrackingInfo(BaseModel):
    """Complete tracking metadata for the response"""
    conv_id: UUID = Field(..., description="Conversation identifier")
    session_id: UUID = Field(..., description="Session identifier")
    session_name: Optional[str] = Field(default=None, description="Project identifier")
    request_id: str = Field(..., description="Request identifier for tracing")
    total_duration_seconds: float = Field(..., description="Total processing time in seconds")
    generated_at: datetime = Field(..., description="Response timestamp")
    
    # Execution details
    execution_traces: List[ExecutionTrace] = Field(default_factory=list, description="Component execution traces")
    processing_issues: List[ProcessingIssue] = Field(default_factory=list, description="Issues encountered")
    component_metadata: List[ComponentMetadata] = Field(default_factory=list, description="Component execution metadata")



# Main Analytics Response

class AnalyticsQueryResponse(BaseModel):
    """Complete response from analytics agent"""
    
    # Core response
    status: Literal["success", "error", "partial"] = Field(..., description="Response status")
    
    # Query information
    original_query: str = Field(..., description="Original user query")
    detected_intent: str = Field(..., description="Detected intent: data_analysis, comparison, aggregation, etc.")
    
    # SQL (if generated)
    sql_details: Optional[GeneratedSQL] = Field(default=None, description="Generated SQL and metadata")
    
    # Results
    narrative_explanation: str = Field(..., description="Natural language explanation")
    key_insights: List[DataInsight] = Field(default_factory=list, description="Extracted insights from data")
    
    # Visualization
    chart_data: Optional[List[ChartVisualization]] = Field(default=None, description="Chart visualization data")
    
    # UI controls
    ui_configuration: Optional[UILayout] = Field(default=None, description="UI configuration for frontend")
    
    # Tracking
    tracking_info: ResponseTrackingInfo = Field(..., description="Response tracking metadata")

    class Config:

        json_extra_schema = {
            "status": "success",
            "original_query": "Show me sales revenue by region",
            "detected_intent": "data_analysis",
            "sql_details": {
                "sql_query": "SELECT region, SUM(amount) FROM sales GROUP BY region",
                "source_tables": ["sales"],
                "target_columns": ["region", "amount"],
                "aggregation_methods": ["SUM"],
                "run_time_ms": 45,
                "result_count": 4,
                "sql_query_narrative": None
            },
            "chart_data": [
                {
                    "type": "bar",
                    "title": "State Revenure by region",
                    "data": [
                        {"region": "North", "revenue": 520000},
                        {"region": "South", "revenue": 380000}
                    ],
                    "x_axis": "Region",
                    "y_axis": "Sales Revenue",
                    "embedded_image": None
                }
            ],
            "narrative_explanation": "Total Sales revenue is ₹12,50,000. North region leads with ₹5,20,000",
            "key_insights": [{
                "category": "comparsion",
                "importance": "high",
                "headline": "Top performing region",
                "decription": "North region contributes 41.6%, of total sales",
                "key_value": "520000",
                "confidence": "0.95"
            }],
            "ui_configuration": None,
            "tracking_info": {"conversation_id": "conv_a1b2c3d4e5f6",
                              "session_id": "sess_789xyz123",
                              "project_id": "proj_sales_analytics_2026",
                              "request_id": "req_20260609_143022_a1b2c3d4",
                              "total_duration_seconds": 2.847,
                              "generated_at": "2026-06-09T14:30:22.123Z",
                              
                              "execution_traces": [
                                {
                                  "component_name": "intent_analyzer",
                                  "status": "completed",
                                  "duration_seconds": 0.234,
                                  "log_messages": [
                                    "Starting intent analysis for query: 'Show me sales revenue by region'",
                                    "Detected intent: data_analysis (confidence: 0.94)",
                                    "Extracted entities: metric=revenue, dimension=region, time_period=last_quarter"
                                  ]
                                },
                                {
                                  "component_name": "schema_retriever",
                                  "status": "completed",
                                  "duration_seconds": 0.156,
                                  "log_messages": [
                                    "Querying vector DB for relevant schema",
                                    "Retrieved 3 relevant tables: sales, customers, products",
                                    "Similarity scores: sales(0.92), customers(0.45), products(0.23)"
                                  ]
                                },
                                {
                                  "component_name": "sql_generator",
                                  "status": "completed",
                                  "duration_seconds": 1.234,
                                  "log_messages": [
                                    "Building SQL generation prompt with 2 few-shot examples",
                                    "Generated SQL: SELECT region, SUM(amount) FROM sales GROUP BY region",
                                    "SQL validation passed"
                                  ]
                                },
                                {
                                  "component_name": "data_executor",
                                  "status": "completed",
                                  "duration_seconds": 0.089,
                                  "log_messages": [
                                    "Executing SQL on PostgreSQL database",
                                    "Query returned 4 rows in 89ms"
                                  ]
                                },
                        
                              ],
                              
                              "processing_issues": [
                                {
                                  "source_component": "sql_generator",
                                  "severity": "warning",
                                  "error_code": "AMBIGUOUS_COLUMN",
                                  "user_message": "Column 'amount' exists in multiple tables. Using sales.amount.",
                                  "technical_details": {
                                    "ambiguous_columns": ["amount"],
                                    "possible_tables": ["sales", "transactions"],
                                    "resolved_table": "sales"
                                  }
                                },
                                {
                                  "source_component": "data_executor",
                                  "severity": "error",
                                  "error_code": "DATA_BASE_EXECUTION_ERROR",
                                  "user_message": "sql execution is not successful",
                                }
                              ],
                              
                              "component_metadata": [
                                {
                                  "component_name": "intent_analyzer",
                                  "execution_details": {
                                    "model_used": "gemini-2.0-flash-exp",
                                    "confidence_score": 0.94,
                                    "entities_extracted": 3,
                                    "prompt_tokens": 245,
                                    "completion_tokens": 89
                                  }
                                },
                                {
                                  "component_name": "schema_retriever",
                                  "execution_details": {
                                    "vector_db_type": "chromadb",
                                    "collection_name": "schema_embeddings",
                                    "top_k": 5,
                                    "similarity_threshold": 0.65,
                                    "results_count": 3
                                  }
                                },
                                {
                                  "component_name": "sql_generator",
                                  "execution_details": {
                                    "model_used": "gemini-2.0-flash-exp",
                                    "temperature": 0.1,
                                    "few_shot_examples_used": 2,
                                    "sql_length": 87,
                                    "validation_passed": False,
                                    "prompt_tokens": 1250,
                                    "completion_tokens": 180
                                  }
                                },
                                {
                                  "component_name": "data_executor",
                                  "execution_details": {
                                    "database_type": "databricks",
                                    "query_time_ms": 89,
                                    "rows_returned": 4,
                                    "data_size_bytes": 2048,
                                    "index_used": "idx_sales_region"
                                  }
                                },
                        
                              ]
                            }
        }
        

        extra = "forbid"
