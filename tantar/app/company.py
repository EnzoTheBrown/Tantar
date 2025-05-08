from typing import Union, List
from schemas.relational import (
    Company,
    User,
    CompanyInputModel,
    Shares,
    Role,
    MoralPerson,
    PhysicalPerson,
    Person,
    File,
)
from schemas.model_api import (
    CompanyAPIModel,
    CompanyDetailsAPIModel,
    RoleAPIModel,
    PersonAPIModel,
    SharesAPIModel,
    PVAGAPIModel,
    StatusAPIModel,
    ContratAPIModel,
    OrdreDeMouvementAPIModel,
    FileAPIModel,
    RegistreDeMouvementAPIModel,
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


def get_person_api_model(person: Person) -> PersonAPIModel:
    moral_persons = person.moral_persons
    physical_persons = person.physical_persons
    is_moral = bool(moral_persons)
    if is_moral:
        person = moral_persons[0]
    else:
        person = physical_persons[0]
    return PersonAPIModel(
        name=person.name,
        is_moral=is_moral,
    )


def get_role_api_model(role: Role) -> RoleAPIModel:
    person = get_person_api_model(role.person)
    role_api_model = RoleAPIModel(
        name=role.name,
        person=person,
    )
    return role_api_model


def get_shares_api_model(shares: Shares) -> SharesAPIModel:
    person = get_person_api_model(shares.person)
    shares_api_model = SharesAPIModel(
        person=person,
        percentage=shares.percentage,
        shares=shares.shares,
    )
    return shares_api_model


def get_file_api_model(file: File) -> FileAPIModel:
    match file.type:
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
            contract = file.contracts[0]
            return ContratAPIModel(
                name=file.name,
                id=file.original_id,
                file_type=file.type,
                offeror=get_person_api_model(contract.offerors[0].person)
                if contract.offerors
                else None,
                offeree=get_person_api_model(contract.offerees[0].person)
                if contract.offerees
                else None,
            )
        case FileType.ORDRE_DE_MOUVEMENT_DE_TITRES:
            return OrdreDeMouvementAPIModel(
                name=file.name,
                id=file.original_id,
                file_type=file.type,
            )


def get_company_api_model(company: Company) -> CompanyAPIModel:
    return CompanyAPIModel(
        name=company.name,
        siren=company.siren,
        original_id=company.original_id,
        roles=[get_role_api_model(role) for role in company.roles],
        shares=[get_shares_api_model(shares) for shares in company.shares],
        files=[get_file_api_model(file) for file in company.files],
        details=company.details,
    )


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
    company = db.exec(select(Company).where(Company.original_id == company_id)).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return get_company_api_model(company)


@company_router.get("/companies", response_model=List[CompanyAPIModel])
def get_companies(
    user: User = Depends(get_current_user),
):
    return [get_company_api_model(c) for c in user.account.companies]


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


@company_router.put("/company/{company_id}", response_model=CompanyAPIModel)
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
    return get_company_api_model(db_company).model_dump(exclude={"id"})
