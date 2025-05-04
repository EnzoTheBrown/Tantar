from fastapi import Depends, APIRouter, HTTPException
from schemas.relational import User, UserInputModel, UserAPIModel, Account
from tantar.database import get_db, Session
from sqlmodel import select
from tantar.utils.logger import get_logger

from .authenticate import get_password_hash, get_current_user

logger = get_logger(__name__)
user_router = APIRouter()


def check_user_exists(db, email):
    results = db.exec(select(User).where(User.email == email)).first()
    return results is not None


@user_router.post("/user", status_code=201, response_model=UserAPIModel)
def create_user(user: UserInputModel, db: Session = Depends(get_db)):
    logger.info(f"AUDIT: Creating user {user.email}")
    account = Account(name="")
    db.add(account)
    db.commit()
    if check_user_exists(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        account_id=account.id,
    )
    db.add(new_user)
    db.commit()
    return UserAPIModel.model_validate(new_user)


@user_router.get(
    "/users",
)
def get_users(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    users = db.exec(select(User).where(User.account_id == user.account_id))
    return [UserAPIModel.model_validate(user) for user in users]


@user_router.get("/user", response_model=UserAPIModel)
def get_user(
    user: User = Depends(get_current_user),
):
    return UserAPIModel.model_validate(user)


@user_router.delete("/user/{original_id}", status_code=204)
def delete_user(original_id: str, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.original_id == original_id)).first()
    db.delete(user)
    db.commit()
    return None
