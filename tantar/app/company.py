from typing import List
from schemas.model import Company, User, CompanyInputModel, CompanyAPIModel
from tantar.database import get_db, Session
from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from .authenticate import get_current_user
from .websocket import notify
from schemas.websocket import WebSocketNewCompanyMessage
from tantar.pappers import create_company_details
from sqlmodel import select
from tantar.utils.logger import get_logger

logger = get_logger(__name__)

company_router = APIRouter()


@company_router.post("/company", status_code=201, response_model=CompanyAPIModel)
async def create_company(
    company: CompanyInputModel,
    client: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = client.account if isinstance(client, User) else client
    new_company = Company(
        name=company.name,
        siren=company.siren,
        account=account,
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    try:
        logger.info(f"Creating company details for company {new_company.original_id}")
        company_details = create_company_details(new_company)
        db.add(company_details)
        db.commit()
    except Exception as e:
        logger.info(f"Error while creating company details: {e}")

    validated_company = CompanyAPIModel.model_validate(new_company)
    message = WebSocketNewCompanyMessage(company=validated_company)
    await notify(company_id=validated_company.original_id, message=message, db=db)
    return validated_company


@company_router.get("/company/{company_id}")
def get_company(
    company_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = db.exec(select(Company).where(Company.original_id == company_id)).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyAPIModel.model_validate(company)


@company_router.get("/companies", response_model=List[CompanyAPIModel])
def get_companies(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return [CompanyAPIModel.model_validate(c) for c in user.account.companies]


@company_router.delete("/company/{company_id}", status_code=204)
def delete_company(
    company_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_company = db.exec(
        select(Company).where(Company.original_id == company_id)
    ).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(db_company)
    db.commit()


class CompanyUpdateModel(BaseModel):
    name: str
    siren: str


@company_router.put("/company/{company_id}")
def update_company(
    company_id: str,
    company: CompanyUpdateModel,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_company = db.query(Company).filter(Company.original_id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db_company.name = company.name
    db_company.siren = company.siren
    db.commit()
    db.refresh(db_company)
    return CompanyAPIModel.model_validate(db_company).model_dump(exclude={"id"})
