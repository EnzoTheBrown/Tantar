from typing import Annotated
from schemas.model import (
    Account,
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
    account = Account(name=account.name)
    db.add(account)
    db.commit()
    return AccountAPIModel.model_validate(account)


@account_router.get("/account/{account_id}", response_model=AccountAPIModel)
def get_account(
    account_id: str,
    user: Annotated[User, Security(get_current_user)],
    db: Session = Depends(get_db),
):
    account_id = db.exec(
        select(Account).where(Account.original_id == account_id)
    ).first()
    if account_id is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return AccountAPIModel.model_validate(account_id)
