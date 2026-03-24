from pydantic import BaseModel
from typing import Optional

class DriverInfo(BaseModel):
    name    : str
    position: int
    gap     : str
    tyre    : Optional[str] = "unknown"