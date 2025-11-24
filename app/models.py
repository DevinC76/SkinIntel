from pydantic import BaseModel, EmailStr

# Authentication models
class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str

# Analysis models
class AnalysisResponse(BaseModel):
    id: str
    filename: str
    acne_count: int
    avg_acne_width: float
    avg_acne_height: float
    avg_acne_area: float
    papules_count: int
    pustules_count: int
    comedone_count: int
    nodules_count: int
    avg_redness: float
    global_redness: float
    skin_disease_label: str | None
    skin_disease_confidence: float | None
    skin_classification_labels: str
    acne_detected: bool
