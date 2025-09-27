from pydantic import BaseModel, RootModel
from typing import List, Dict, Any

class GenerateRequest(BaseModel):
    fields: List[str]
    count: int = 5

class GenerateResponse(RootModel[List[Dict[str, Any]]]):
    pass