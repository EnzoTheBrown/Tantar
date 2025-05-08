from datetime import datetime
import uuid
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlmodel import Field, Relationship, SQLModel

# ----- External/shared enums -------------------------------------------------
from schemas.file_model import (
    ContractType,
    EventType,
    FileType,
    JuridicCategory,
)


# ============================================================================
# Base helpers
# ============================================================================


class BaseSQLModel(SQLModel):
    """Common fields for every persisted model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    original_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


# ============================================================================
# Account & User
# ============================================================================


class Account(BaseSQLModel, table=True):
    name: str

    users: List["User"] = Relationship(back_populates="account")
    companies: List["Company"] = Relationship(back_populates="account")
    files: List["File"] = Relationship(back_populates="account")
    persons: List["Person"] = Relationship(back_populates="account")


class AccountInputModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class AccountAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    name: str


class User(BaseSQLModel, table=True):
    email: str
    hashed_password: str

    account_id: int = Field(foreign_key="account.id")
    account: Account = Relationship(back_populates="users")


class UserInputModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    password: str
    invitation_token: Optional[str] = None


class UserAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr
    original_id: str
    account: AccountAPIModel


# ============================================================================
# Company & details
# ============================================================================


class Company(BaseSQLModel, table=True):
    name: str
    siren: str

    account_id: int = Field(foreign_key="account.id")
    account: Account = Relationship(back_populates="companies")

    files: List["File"] = Relationship(back_populates="company")  # noqa: F821
    details: Optional["CompanyDetails"] = Relationship(back_populates="company")  # noqa: F821
    shares: List["Shares"] = Relationship(back_populates="company")  # noqa: F821
    roles: List["Role"] = Relationship(back_populates="company")  # noqa: F821


class CompanyInputModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    siren: str


class CompanyDetails(BaseSQLModel, table=True):
    siren: str
    name: str
    naf_code: str
    activity: str
    capital: Optional[float] = None
    juridic_form: Optional[str] = None

    company_id: int = Field(foreign_key="company.id")
    company: Company = Relationship(back_populates="details")


class CompanyDetailsAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    siren: str
    name: str
    naf_code: str
    activity: str
    capital: Optional[float]
    juridic_form: Optional[str]


class CompanyAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    name: str
    siren: str
    account: Optional[AccountAPIModel] = None
    details: Optional[CompanyDetailsAPIModel] = None


# ============================================================================
# Files, PVAG & Events
# ============================================================================


class File(BaseSQLModel, table=True):
    name: str
    s3_path: str
    status: int = Field(default=0)

    account_id: Optional[int] = Field(default=None, foreign_key="account.id")
    account: Optional[Account] = Relationship(back_populates="files")

    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    company: Optional[Company] = Relationship(back_populates="files")

    created_at: datetime = Field(default_factory=datetime.now)
    watched_at: Optional[datetime] = None
    type: Optional[FileType] = None

    contracts: List["Contract"] = Relationship(  # noqa: F821
        back_populates="file", sa_relationship_kwargs={"cascade": "all, delete"}
    )

    pvags: List["PVAG"] = Relationship(  # noqa: F821
        back_populates="file", sa_relationship_kwargs={"cascade": "all, delete"}
    )

    statuts: List["Statuts"] = Relationship(
        back_populates="file", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    ordres_de_mouvement: List["OrdreDeMouvement"] = Relationship(
        back_populates="file", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    registre_de_mouvement_de_titres: List["RegistreDeMouvementDeTitres"] = Relationship(
        back_populates="file", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class FileInputModel(BaseModel):
    name: str
    s3_path: str


class FileAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    name: str
    s3_path: str
    status: int
    company: Optional[CompanyAPIModel] = None
    created_at: datetime
    watched_at: Optional[datetime] = None
    type: Optional[FileType] = None


class SerFileAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    name: str
    s3_path: str
    status: int
    company: Optional[CompanyAPIModel] = None
    type: Optional[FileType] = None


class PVAG(BaseSQLModel, table=True):
    file_id: int = Field(foreign_key="file.id")
    file: File = Relationship(back_populates="pvags")

    events: List["Event"] = Relationship(  # noqa: F821
        back_populates="pvag", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class PVAGAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    file: FileAPIModel


class Statuts(BaseSQLModel, table=True):
    file_id: int = Field(foreign_key="file.id")
    file: File = Relationship(back_populates="statuts")


class StatutsAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    file: FileAPIModel


class OrdreDeMouvement(BaseSQLModel, table=True):
    file_id: int = Field(foreign_key="file.id")
    file: File = Relationship(back_populates="ordres_de_mouvement")


class OrdreDeMouvementAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    file: FileAPIModel


class RegistreDeMouvementDeTitres(BaseSQLModel, table=True):
    file_id: int = Field(foreign_key="file.id")
    file: File = Relationship(back_populates="registre_de_mouvement_de_titres")


class RegistreDeMouvementDeTitresAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    file: FileAPIModel


# ============================================================================
# Person hierarchy
# ============================================================================


class Person(BaseSQLModel, table=True):
    account_id: int = Field(foreign_key="account.id")
    account: "Account" = Relationship(back_populates="persons")
    physical_persons: List["PhysicalPerson"] = Relationship(
        back_populates="person", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    moral_persons: List["MoralPerson"] = Relationship(
        back_populates="person", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    shares: List["Shares"] = Relationship(
        back_populates="person", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    roles: List["Role"] = Relationship(
        back_populates="person", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    offerees: List["Offeree"] = Relationship(
        back_populates="person", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    offerors: List["Offeror"] = Relationship(
        back_populates="person", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class PhysicalPerson(BaseSQLModel, table=True):
    firstname: str
    lastname: str

    person_id: int = Field(foreign_key="person.id")
    person: Person = Relationship(back_populates="physical_persons")

    @property
    def name(self) -> str:  # pragma: no cover ‑ simple helper
        return f"{self.firstname} {self.lastname}"


class PhysicalPersonAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    firstname: str
    lastname: str

    @property
    def name(self) -> str:  # pragma: no cover ‑ simple helper
        return f"{self.firstname} {self.lastname}"


class MoralPerson(BaseSQLModel, table=True):
    name: str

    person_id: int = Field(foreign_key="person.id")
    person: Person = Relationship(back_populates="moral_persons")


class MoralPersonAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None

    @property
    def name(self) -> str:  # pragma: no cover ‑ simple helper
        return f"{self.firstname} {self.lastname}"


# ============================================================================
# Events & related schemas
# ============================================================================


class Event(BaseSQLModel, table=True):
    text: str
    title: str
    page_index: int
    type: EventType
    label: JuridicCategory

    pvag_id: int = Field(foreign_key="pvag.id")
    pvag: PVAG = Relationship(back_populates="events")

    date: Optional[datetime] = None

    authorized_contracts: List["AuthorizedContract"] = Relationship(  # noqa: F821
        back_populates="event", sa_relationship_kwargs={"cascade": "all, delete"}
    )

    @property
    def name(self) -> str:  # pragma: no cover
        return self.title


class EventAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    text: str
    title: str
    page_index: int
    type: EventType
    label: JuridicCategory
    pvag: PVAGAPIModel
    date: Optional[datetime] = None

    @property
    def name(self) -> str:  # pragma: no cover
        return self.title


class EventInput(BaseModel):
    original_id: str
    account_id: str
    company_id: str
    file_id: str
    date: str
    label: JuridicCategory
    type: EventType
    text: str
    title: str
    page_index: int
    file_name: str
    siren: str

    @property
    def name(self) -> str:  # pragma: no cover
        return self.title


class EventCategoriesAPIModel(BaseModel):
    events: List[EventAPIModel]
    categories: List[str]


# ============================================================================
# Contracts, shares & roles
# ============================================================================


class Contract(BaseSQLModel, table=True):
    type: Optional[ContractType]
    title: str

    file_id: int = Field(foreign_key="file.id")
    file: File = Relationship(back_populates="contracts")

    offerees: List["Offeree"] = Relationship(  # noqa: F821
        back_populates="contract", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    offerors: List["Offeror"] = Relationship(  # noqa: F821
        back_populates="contract", sa_relationship_kwargs={"cascade": "all, delete"}
    )
    authorized_contracts: List["AuthorizedContract"] = Relationship(  # noqa: F821
        back_populates="contract", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class Offeror(BaseSQLModel, table=True):
    person_id: int = Field(foreign_key="person.id")
    person: Person = Relationship(back_populates="offerors")

    contract_id: int = Field(foreign_key="contract.id")
    contract: Contract = Relationship(back_populates="offerors")


class Offeree(BaseSQLModel, table=True):
    person_id: int = Field(foreign_key="person.id")
    person: Person = Relationship(back_populates="offerees")

    contract_id: int = Field(foreign_key="contract.id")
    contract: Contract = Relationship(back_populates="offerees")


class Shares(BaseSQLModel, table=True):
    person_id: int = Field(foreign_key="person.id")
    person: "Person" = Relationship(back_populates="shares")

    company_id: int = Field(foreign_key="company.id")
    company: "Company" = Relationship(back_populates="shares")

    shares: int = Field(description="Number of shares owned by the person")
    percentage: Optional[float] = Field(
        default=None, description="Percentage of company capital owned"
    )


class SharesAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    shares: int
    percentage: Optional[float] = None
    person: Union[PhysicalPersonAPIModel, MoralPersonAPIModel]
    company: CompanyAPIModel


class RoleName(str, Enum):
    PRESIDENT = "PRESIDENT"
    DIRECTOR = "DIRECTOR"
    FOUNDER = "FOUNDER"
    ASSOCIATE = "ASSOCIATE"
    UNKNOWN = "UNKNOWN"


class Role(BaseSQLModel, table=True):
    name: RoleName = Field(description="Role name inside the company")
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    person_id: int = Field(foreign_key="person.id")
    person: Person = Relationship(back_populates="roles")

    company_id: int = Field(foreign_key="company.id")
    company: Company = Relationship(back_populates="roles")


class RoleAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    name: RoleName
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    person: PhysicalPersonAPIModel
    company: CompanyAPIModel


class AuthorizedContract(BaseSQLModel, table=True):
    contract_id: int = Field(foreign_key="contract.id")
    contract: Contract = Relationship(back_populates="authorized_contracts")

    event_id: int = Field(foreign_key="event.id")
    event: Event = Relationship(back_populates="authorized_contracts")


# ============================================================================
# Re‑export public symbols
# ============================================================================

__all__ = [
    # tables
    "Account",
    "User",
    "Company",
    "File",
    "Person",
    "PhysicalPerson",
    "MoralPerson",
    "Event",
    "Contract",
    "Shares",
    "Role",
    "PVAG",
    "CompanyDetails",
    "Statuts",
    "OrdreDeMouvement",
    "RegistreDeMouvementDeTitres",
    "AuthorizedContract",
    # pydantic schemas
    "AccountInputModel",
    "AccountAPIModel",
    "UserInputModel",
    "UserAPIModel",
    "CompanyInputModel",
    "CompanyAPIModel",
    "CompanyDetailsAPIModel",
    "FileInputModel",
    "FileAPIModel",
    "SerFileAPIModel",
    "PVAGAPIModel",
    "EventAPIModel",
    "EventInput",
    "EventCategoriesAPIModel",
]
