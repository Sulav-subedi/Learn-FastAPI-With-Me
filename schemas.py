from pydantic import BaseModel
from typing import List
from datetime import datetime


class NoteBase(BaseModel):
    title : str = ""
    body : str = ""
    tags : List[str] = []
    pinned: bool = False

    model_config = { 
        "from_attributes": True
    }


class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserCreate(BaseModel):
    username: str
    password: str

    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    username: str
    password: str

    model_config = {
        "from_attributes": True
    }

class UserInfo(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = {
        "from_attributes": True
    }
