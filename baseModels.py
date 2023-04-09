from typing import Optional
from pydantic import BaseModel

class SignUp(BaseModel):
    email : Optional[str]
    pw : Optional[str]