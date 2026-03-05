from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="The user's message to the chatbot. Cannot be empty or exceed 1000 characters.")
