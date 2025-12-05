from pydantic import BaseModel, Field


class StartConsultationRequest(BaseModel):
    symptoms_text: str = Field(..., min_length=10, max_length=5000)

    class Config:
        json_schema_extra = {
            "example": {
                "symptoms_text": "I've been having headaches for the past 3 days, along with mild fever and fatigue."
            }
        }


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
