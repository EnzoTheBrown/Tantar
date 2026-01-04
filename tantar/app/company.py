from typing import List
from schemas.relational import (
    Company,
    User,
    CompanyInputModel,
    File,
)
from schemas.model_api import (
    CompanyAPIModel,
    PVAGAPIModel,
    StatusAPIModel,
    ContratAPIModel,
    OrdreDeMouvementAPIModel,
    FileAPIModel,
    RegistreDeMouvementAPIModel,
    CompanyDetailsAPIModel,
)
from schemas.file_model import FileType
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


def get_file_api_model(file: File) -> FileAPIModel:
    match file.type:
        case None:
            return PVAGAPIModel(
                name=file.name,
                id=file.original_id,
            )
        case FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE:
            return PVAGAPIModel(
                name=file.name,
                id=file.original_id,
                file_type=file.type,
            )
        case FileType.REGISTRE_DE_MOUVEMENT_DE_TITRES:
            return RegistreDeMouvementAPIModel(
                name=file.name,
                id=file.original_id,
                file_type=file.type,
            )
        case FileType.STATUTS:
            return StatusAPIModel(
                name=file.name,
                id=file.original_id,
                file_type=file.type,
            )
        case FileType.CONTRAT:
            return ContratAPIModel(
                name=file.name,
                id=file.original_id,
                file_type=file.type,
                offeror=None,
                offeree=None,
            )
        case FileType.ORDRE_DE_MOUVEMENT_DE_TITRES:
            return OrdreDeMouvementAPIModel(
                name=file.name,
                id=file.original_id,
                file_type=file.type,
            )


def get_company_details(company: Company) -> CompanyDetailsAPIModel | None:
    if (
        company.details_naf_code is None
        and company.details_activity is None
        and company.details_capital is None
        and company.details_juridic_form is None
    ):
        return None
    return CompanyDetailsAPIModel(
        siren=company.siren,
        name=company.name,
        naf_code=company.details_naf_code or "",
        activity=company.details_activity or "",
        capital=company.details_capital,
        juridic_form=company.details_juridic_form,
    )


def get_company_api_model(company: Company) -> CompanyAPIModel:
    return CompanyAPIModel(
        name=company.name,
        siren=company.siren,
        original_id=company.original_id,
        roles=[],
        shares=[],
        files=[get_file_api_model(file) for file in company.files],
        details=get_company_details(company),
    )


@company_router.post("/company", status_code=201, response_model=CompanyAPIModel)
async def create_company(
    company: CompanyInputModel,
    client: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_company = Company(
        name=company.name,
        siren=company.siren,
        user=client,
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    try:
        logger.info(f"Creating company details for company {new_company.original_id}")
        create_company_details(new_company, db=db)
        db.commit()
    except Exception as e:
        logger.info(f"Error while creating company details: {e}")

    validated_company = get_company_api_model(new_company)
    message = WebSocketNewCompanyMessage(company=validated_company)
    await notify(company_id=validated_company.original_id, message=message, db=db)
    return validated_company


@company_router.get("/company/{company_id}", response_model=CompanyAPIModel)
def get_company(
    company_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company = db.exec(
        select(Company).where(
            Company.original_id == company_id, Company.user_id == user.id
        )
    ).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return get_company_api_model(company)


@company_router.get("/companies", response_model=List[CompanyAPIModel])
def get_companies(
    user: User = Depends(get_current_user),
):
    return [get_company_api_model(c) for c in user.companies]


@company_router.delete("/company/{company_id}", status_code=204)
def delete_company(
    company_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_company = db.exec(
        select(Company).where(
            Company.original_id == company_id, Company.user_id == user.id
        )
    ).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(db_company)
    db.commit()


class CompanyUpdateModel(BaseModel):
    name: str
    siren: str


@company_router.put("/company/{company_id}", response_model=CompanyAPIModel)
def update_company(
    company_id: str,
    company: CompanyUpdateModel,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_company = (
        db.query(Company)
        .filter(Company.original_id == company_id, Company.user_id == user.id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    db_company.name = company.name
    db_company.siren = company.siren
    db.commit()
    db.refresh(db_company)
    return get_company_api_model(db_company).model_dump(exclude={"id"})
