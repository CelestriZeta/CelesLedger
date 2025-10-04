from langmem import create_memory_manager
from pydantic import BaseModel
from typing import Optional
from src.agent import llm

# Define profile structure
class UserProfile(BaseModel):
    """Represents the full profile of a user."""
    name: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

# Configure extraction
manager = create_memory_manager(
    llm,
    schemas=None,
    instructions="提取用户的各方面信息",
    enable_inserts=True
)
