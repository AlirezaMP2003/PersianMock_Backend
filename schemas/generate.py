from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

class GenerateRequest(BaseModel):
    table_name: str = Field(..., pattern=r'^[A-Za-z_][A-Za-z0-9_]*$', description="SQL table name (only letters/numbers/_ , must start with letter or _)")
    fields: List[str]
    count: int = Field(default=5, ge=1, le=10000)
    include_create_table: bool = False
    format: Literal["json", "csv", "sql", "excel"] = "sql"

class GenerateResponse(BaseModel):
    data: List[Dict[str, Any]]
    ddl: Optional[str] = None
    format: Literal["json", "csv", "sql", "excel"]