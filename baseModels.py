from typing import Optional
from pydantic import BaseModel

class SignInfor(BaseModel):
    email : Optional[str]
    pw : Optional[str]