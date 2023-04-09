from datetime import timedelta

from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
    Depends,
    HTTPException
)
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import models
from app import oauth2
from app import schemas
from app import utils
from app.config import settings
from app.database import get_db
from app.oauth2 import AuthJWT

router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
ACCESS_TOKEN_EXPIRES_IN_SEC = ACCESS_TOKEN_EXPIRES_IN * 60
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN_SEC = REFRESH_TOKEN_EXPIRES_IN * 60


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserResponse
)
async def create_user(
        payload: schemas.CreateUserSchema,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.name == payload.name).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Аккаунт уже существует'
        )

    payload.password = utils.hash_password(payload.password)
    payload.email = EmailStr(payload.email.lower())
    new_user = models.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post('/login', response_model=schemas.LoginUserResponse)
def login(
        payload: schemas.LoginUserSchema,
        response: Response,
        db: Session = Depends(get_db),
        Authorize: AuthJWT = Depends()
):
    user = db.query(models.User).filter(
        models.User.name == payload.name).first()

    if not user or not utils.verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверное имя или пароль'
        )

    access_token = Authorize.create_access_token(
        subject=str(user.id),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    )

    refresh_token = Authorize.create_refresh_token(
        subject=str(user.id),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN)
    )

    response.set_cookie(
        'access_token',
        access_token,
        ACCESS_TOKEN_EXPIRES_IN_SEC,
        ACCESS_TOKEN_EXPIRES_IN_SEC
    )
    response.set_cookie(
        'refresh_token',
        refresh_token,
        REFRESH_TOKEN_EXPIRES_IN_SEC,
        REFRESH_TOKEN_EXPIRES_IN_SEC
    )
    response.set_cookie(
        'logged_in',
        'True',
        ACCESS_TOKEN_EXPIRES_IN_SEC,
        ACCESS_TOKEN_EXPIRES_IN_SEC
    )

    return {
        'status': 'success',
        'is_superuser': user.is_superuser,
        'access_token': access_token
    }


@router.get('/refresh')
def refresh_token(
        response: Response,
        request: Request,
        Authorize: AuthJWT = Depends(),
        db: Session = Depends(get_db)
):
    try:
        Authorize.jwt_refresh_token_required()

        user_id = Authorize.get_jwt_subject()
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Не удалось обновить токен'
            )

        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Пользователь, принадлежащий этому токену, не существует'
            )

        access_token = Authorize.create_access_token(
            subject=str(user.id),
            expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
        )
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Предоставьте токен обновления'
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    response.set_cookie(
        'access_token',
        access_token,
        ACCESS_TOKEN_EXPIRES_IN_SEC,
        ACCESS_TOKEN_EXPIRES_IN_SEC
    )
    response.set_cookie(
        'logged_in',
        'True',
        ACCESS_TOKEN_EXPIRES_IN_SEC,
        ACCESS_TOKEN_EXPIRES_IN_SEC
    )
    return {'access_token': access_token}


@router.get('/logout', status_code=status.HTTP_200_OK)
def logout(
        response: Response,
        Authorize: AuthJWT = Depends(),
        user_id: str = Depends(oauth2.require_user)
):
    Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', 0)
    return {'status': 'success'}
