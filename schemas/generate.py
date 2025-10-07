from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

class FieldItem(BaseModel):
    type: str = Field(..., description="Field type, e.g. firstname, lastname, email, ...")
    name: str = Field(..., description="Custom field name for the column")

class GenerateRequest(BaseModel):
    table_name: str = Field(..., pattern=r'^[A-Za-z_][A-Za-z0-9_]*$', description="SQL table name (only letters/numbers/_ , must start with letter or _)")
    fields: List[FieldItem]
    count: int = Field(default=5, ge=1, le=10000)
    include_create_table: bool = False
    format: Literal["json", "csv", "sql", "excel"] = "sql"

class GenerateResponse(BaseModel):
    data: List[Dict[str, Any]]
    ddl: Optional[str] = None
    format: Literal["json", "csv", "sql", "excel"]