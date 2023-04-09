from typing import List

from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models
from app.config import settings
from app.database import get_db


class Settings(BaseModel):
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_secret_key: str = settings.JWT_SECRET_KEY


@AuthJWT.load_config
def get_config():
    return Settings()


class UserNotFound(Exception):
    pass


class NotSuperuserError(Exception):
    pass


def require_user(
        db: Session = Depends(get_db),
        Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            raise UserNotFound()

    except Exception as e:
        error = e.__class__.__name__
        print(error)
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Вы не авторизованы'
            )
        if error == 'UserNotFound':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Пользователь больше не существует'
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен недействителен или просрочен'
        )
    return user_id


def require_superuser(
        db: Session = Depends(get_db),
        Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            raise UserNotFound('User no longer exist')

        if not user.is_superuser:
            raise NotSuperuserError('NotSuperuserError')

    except Exception as e:
        error = e.__class__.__name__
        print(f'ERROR: {error}')
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='You are not logged in'
            )
        if error == 'UserNotFound':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User no longer exist'
            )
        if error == 'NotSuperuserError':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='NotSuperuserError'
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is invalid or has expired'
        )
    return user_id
