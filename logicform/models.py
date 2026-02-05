from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field as PydanticField

class Filter(BaseModel):
    field: str
    op: str  # ==, !=, >, <, in, like
    value: Any

class TimeRange(BaseModel):
    field: str
    start: str
    end: str

class Logicform(BaseModel):
    """
    The intermediate representation of the user's intent.
    This is what the LLM produces.
    """
    target_metrics: List[str] = PydanticField(description="List of metric names to calculate")
    dimensions: List[str] = PydanticField(default=[], description="List of dimensions to group by (e.g. shop.region)")
    filters: List[Filter] = PydanticField(default=[], description="List of filters to apply")
    limit: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_metrics": ["achievement_rate"],
                "dimensions": ["shop.region"],
                "filters": [{"field": "shop.region", "op": "==", "value": "North"}],
            }
        }
