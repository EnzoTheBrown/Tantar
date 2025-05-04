import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from tantar.utils.logger import get_logger
from tantar.settings import SETTINGS
from fastapi import HTTPException, status, Depends
from schemas.relational import User, Account
from tantar.database import get_db, Session
from sqlmodel import select
from .utils import ALGORITHM

logger = get_logger(__name__)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):
    user = db.exec(select(User).where(User.email == email)).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


def decode_token(token: str):
    logger.info("Verifying token")
    try:
        payload = jwt.decode(token, SETTINGS.app.secret, algorithms=[ALGORITHM])
        logger.info("Token has been succesfully decoded")
        return payload
    except jwt.PyJWTError:
        logger.info("Token is not decodable")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str):
    logger.info("Verifying token")
    try:
        payload = jwt.decode(token, SETTINGS.app.secret, algorithms=[ALGORITHM])
        uuid: str = payload.get("sub")
    except jwt.PyJWTError:
        logger.info("Token is not decodable")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("Token has been succesfully decoded")
    return uuid


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_db),
) -> User:
    """
    use the token to return the current user
    """
    logger.info("Getting current user based on bearer token.")
    original_id = verify_token(token)
    logger.info(f"Current user is {original_id}")
    user = db.exec(select(User).where(User.original_id == original_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def authenticate_service(
    token: str = Depends(oauth2_scheme), db=Depends(get_db)
) -> User | Account:
    """
    use the token to return the current user or account
    """
    logger.info("Getting current user based on bearer token.")
    payload = decode_token(token)
    original_id = payload.get("sub")
    if payload.get("origin") == "service":
        return db.exec(
            select(Account).where(Account.original_id == original_id)
        ).first()
    else:
        return db.exec(select(User).where(User.original_id == original_id)).first()
