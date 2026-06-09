from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from uuid import UUID



class SQLAgentQueryRequest(BaseModel):

    user_intent: str = Field(
        ...,
        min_length  = 1,
        max_length  = 1000,
        description =  "user intent is more refined version of user query request from the Intent Analyzer"
    )

    table_schemas: List[TableSchema] =  Field (
        ...,
        min_length=1,
        max_length=200,
        description="List of Relevant Table Schemas for SQL generation"
    )

    few_shot_prompts: List[FewShotPromptSchema] = Field(
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

    
class SQLAgentQueryResponse(BaseModel):




    pass