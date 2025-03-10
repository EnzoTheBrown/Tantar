from fastapi import HTTPException, status, Depends, Response, APIRouter
from tantar.database import User, get_db
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from .utils import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from .authenticate import verify_password
from tantar.utils.logger import get_logger
from sqlmodel import select
import logfire

logger = get_logger(__name__)

connection_attempts = logfire.metric_counter('connection_attempts')
connection_successes = logfire.metric_counter('connection_successes')
user_count = logfire.metric_counter('user_count')
company_count = logfire.metric_counter('company_count')
file_count = logfire.metric_counter('file_count')
event_count = logfire.metric_counter('event_count')

login_router = APIRouter()

@login_router.post(
    '/login',
    status_code=status.HTTP_201_CREATED
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = Response(),
    db = Depends(get_db)
) -> dict:
    connection_attempts.add(1)
    logger.info(f"Login attempt for {form_data.username}")
    user = db.exec(select(User).where(User.email == form_data.username)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_uuid = str(user.original_id)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user_uuid,
            "companies": [str(company.original_id) for company in user.account.companies],
            "account_id": str(user.account.original_id),
        },
        expires_delta=access_token_expires
    )
    connection_successes.add(1)
    return {"access_token": access_token, "token_type": "bearer"}


