from pydantic import BaseModel

class User(BaseModel):
    email: str
    hashed_password: str
    refresh_token: str | None = None
