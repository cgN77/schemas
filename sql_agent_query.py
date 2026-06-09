from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from src.api.schemas.few_shot_schema import FewShotMetadata
from src.api.schemas.schema_retrieval import TableSchemaMetadata


#====================================
# SQL Agent Request
#===================================
class SQLAgentQueryRequest(BaseModel):

    user_intent: str = Field(
        ...,
        min_length  = 1,
        max_length  = 1000,
        description =  "user intent is more refined version of user query request from the Intent Analyzer"
    )
    table_schemas: List[TableSchemaMetadata] =  Field(
        ...,
        min_length=1,
        max_length=200,
        description="List of Relevant Table Schemas for SQL generation"
    )
    few_shot_prompts: List[FewShotMetadata] = Field(
        ...,
        min_length=10,
        max_length=50,
        few_shot_prompts="Few Shot prompts of user query and corresponding SQL, for generating SQL accurately for current user query"
    )
    user_id: UUID = Field(
        ...,
        description="UUID of the user making the request for tracking",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    session_id: str = Field(
        ...,
        description = "Topic for the users conversation",
        examples = ["Analyzing Sales for the previous Financial year"]
    )
    conv_id: UUID = Field(
        ...,
        description = "Conversation ID of the chat for tracking and monitoring",
        examples = ["520e8400-f23b-41d4-a716-443645440000"]
    )
    request_id: str = Field(
        ...,
        description="This ID can be used to track the SQL generation requests of a user in a particular session"
    )

#=============================
# Response Utility Models
#============================

class IterationMetaData(BaseModel):

    generated_sql: str = Field(
        ...,
        description="generated sql by LLM in a iteration"
    )
    llm_feedback: str = Field(
        ...,
        description="Feedback by validation LLM in an iteration"
    )
    sql_glot_logs: Optional[str] = Field(
        None,
        description="sql glot parsing logs of the generated sql"
    )
    validation_score: float = Field(
        None,
        description="Validation score given by the validation LLM"
    )
    generated_at: datetime = Field(
        ...,
        description="timestamp at which sql is generated"
    )

    


class ExecutionMetaData(BaseModel):

    conv_id: UUID = Field(
        ...,
        description="Conversation tracking ID"
    )

    user_id: UUID = Field(
        ...,
        description="User Identifier"
    )
    session_name: str = Field(..., description="Session Name")
    session_id: UUID = Field(
        ...,
        description="Session trackind ID"
    )
    request_id: str = Field(
        ...,
        description="Unique Identifier for SQL Generation request"
    )
    iteration_count: int = Field(
        ...,
        description="Number of times LLM, Validation LLM loop has happend"
    )
    iterations_meta_data: List[IterationMetaData] = Field(
        ...,
        description="Meta Data of each iteration (which includes generated sql, validation LLM feedback, SQL Glot parsing logs)"
    )
    started_at: datetime = Field(
        ...,
        description="Timestamp when generation is started"
    )
    completed_at: datetime = Field(
        ...,
        description="Timestamp when generation is completed"
    )



class SQLQueryDetails(BaseModel):

    generated_sql: str = Field(
        None,
        description="generated sql for the user query",
        examples=["SELECT region, SUM(amount) as total_revenue FROM sales \
         WHERE order_date >= '2026-01-01' AND \
        order_date <= '2026-03-31' GROUP BY region ORDER BY total_revenue DESC"
        ]
    )

    explanation: Optional[str] = Field(
        "",
        description="Briefly explains about the SQL query how it actually works",
        examples=[
        "This query calculates total revenue by region for the first quarter of 2026. \
        It filters sales between January 1 and March 31, groups by region, \
        sums the amount, and orders results from highest to lowest revenue."]
    )

    target_tables: List[str] = Field(..., description="Tables accessed")
    target_columns: List[str] = Field(..., description="Columns accessed")

    aggregation_methods: List[str] = Field(default_factory=list, description="Aggregation functions used")
    run_time_ms: Optional[float] = Field(default=None, description="Query execution time in milliseconds")




#=============================================
#   SQL Agent Response
#============================================

class SQLAgentQueryResponse(BaseModel):

    success: bool = Field(
        ...,
        description="Indicates whether SQL generation is completed, if false check error_messages"
    )

    sql_details: SQLQueryDetails = Field(
        ...,
        description="Contains relevant information for final accepted sql query"
    )

    execution_meta_data: ExecutionMetaData = Field(
        ...,
        description="Execution statistics including timing, iteration count, and query metrics and validation LLM Logs"
    )

    error_messages: Optional[str] = Field(
        ...,
        description="Detailed error message if success=false. Contains validation issues, or internal failures."
        )
    
    class Config:

        json_extra_schema = {
            "success": True,
            "sql_details": {
                "generated_sql": "SELECT region, SUM(amount) as total_revenue FROM sales \
         WHERE order_date >= '2026-01-01' AND \
        order_date <= '2026-03-31' GROUP BY region ORDER BY total_revenue DESC",

            "explanation": "This query calculates total revenue by region for the first quarter of 2026. \
        It filters sales between January 1 and March 31, groups by region, \
        sums the amount, and orders results from highest to lowest revenue.",

            "target_tables": ["sales"],
            "target_columns": ["region", "amount", "order_date"],
            "aggregation_methods": ["SUM"],
            "run_time_ms": 45

            },
            "execution_meta_data": {
                "conv_id": "conv_123",
                "session_id": "session_123",
                "session_name": "sales analysis",
                "request_id": "request_123",
                "iteration_count": 1,
                "iteration_meta_data": {
                    "generated_sql": "SELECT region, SUM(amount) as total_revenue FROM sales \
         WHERE order_date >= '2026-01-01' AND \
        order_date <= '2026-03-31' GROUP BY region ORDER BY total_revenue DES",

                    "llm_feedback": {
                        "Generated SQL aligns with the user request, There is no need for another iteration"
                    },
                    "validation_score": 0.92,
                    "generated_at": "2026-06-09T14:30:22.123456Z"
                }

            }
        }

        extra = "forbid"
