from datetime import datetime
import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, ConfigDict
from sqlmodel import Field, Relationship, SQLModel

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
# User, Company, File (minimal relational state)
# ============================================================================


class User(BaseSQLModel, table=True):
    email: str
    hashed_password: str
    account_name: Optional[str] = None

    companies: List["Company"] = Relationship(back_populates="user")
    files: List["File"] = Relationship(back_populates="user")


class Company(BaseSQLModel, table=True):
    name: str
    siren: str

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="companies")

    details_naf_code: Optional[str] = None
    details_activity: Optional[str] = None
    details_capital: Optional[float] = None
    details_juridic_form: Optional[str] = None

    files: List["File"] = Relationship(back_populates="company")


class File(BaseSQLModel, table=True):
    name: str
    s3_path: str
    status: int = Field(default=0)

    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="files")

    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    company: Optional[Company] = Relationship(back_populates="files")

    created_at: datetime = Field(default_factory=datetime.now)
    watched_at: Optional[datetime] = None
    type: Optional[FileType] = None


# ============================================================================
# API schemas (kept for compatibility)
# ============================================================================


class AccountInputModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class AccountAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    name: str


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


class CompanyInputModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    siren: str


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


class PVAGAPIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: str
    file: FileAPIModel


class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: Optional[str] = None
    text: str
    title: str
    page_index: int
    type: EventType
    label: JuridicCategory
    pvag: Optional[PVAGAPIModel] = None
    date: Optional[datetime] = None

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


class RoleName(str, Enum):
    PRESIDENT = "PRESIDENT"
    DIRECTOR = "DIRECTOR"
    FOUNDER = "FOUNDER"
    ASSOCIATE = "ASSOCIATE"
    UNKNOWN = "UNKNOWN"


class Contract(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    original_id: Optional[str] = None
    type: Optional[ContractType] = None
    title: Optional[str] = None
    file_id: Optional[str] = None


__all__ = [
    # tables
    "BaseSQLModel",
    "User",
    "Company",
    "File",
    # api schemas
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
    "Event",
    "EventAPIModel",
    "EventInput",
    "EventCategoriesAPIModel",
    "RoleName",
    "Contract",
]
