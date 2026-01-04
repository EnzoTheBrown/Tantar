from typing import Annotated
from schemas.relational import (
    AccountInputModel,
    AccountAPIModel,
    User,
)
from tantar.database import get_db, Session
from sqlmodel import select
from fastapi import Depends, APIRouter, Security, HTTPException
from .authenticate import get_current_user

account_router = APIRouter()


@account_router.post("/account", response_model=AccountAPIModel, status_code=201)
def create_account(
    account: AccountInputModel,
    user: Annotated[User, Security(get_current_user)],
    db: Session = Depends(get_db),
):
    user.account_name = account.name
    db.add(user)
    db.commit()
    db.refresh(user)
    return AccountAPIModel(original_id=user.original_id, name=user.account_name or "")


@account_router.get("/account/{account_id}", response_model=AccountAPIModel)
def get_account(
    account_id: str,
    user: Annotated[User, Security(get_current_user)],
    db: Session = Depends(get_db),
):
    db_user = db.exec(select(User).where(User.original_id == account_id)).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountAPIModel(
        original_id=db_user.original_id, name=db_user.account_name or ""
    )
