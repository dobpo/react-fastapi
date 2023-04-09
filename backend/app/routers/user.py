from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app.database import get_db
from app.oauth2 import require_superuser

router = APIRouter()


@router.get('/me', response_model=schemas.UserResponse)
def get_me(
        db: Session = Depends(get_db),
        user_id: str = Depends(require_superuser)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user
