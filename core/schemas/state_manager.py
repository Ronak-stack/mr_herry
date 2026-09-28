from pydantic import BaseModel, Field

class Previous(BaseModel):
    intent: str
    prompt: str
    output: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)

class State(BaseModel):
    intent:str
    is_followup:bool
    current_prompt: str
    previous: Previous | None = None
    user_id:int | None = None