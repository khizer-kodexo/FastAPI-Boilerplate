from app.models.domain.profile import ProfileBase
from app.models.domain.user import UserCreate

class SignupRequest(ProfileBase, UserCreate):
    class Config:
        from_attributes = True