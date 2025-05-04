from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from schemas.relational import (
    Account,
    User,
    Company,
    File,
    CompanyDetails,
    Event,
    Person,
    PhysicalPerson,
    MoralPerson,
    Contract,
    PVAG,
    Shares,
    Role,
)

engine = create_engine("sqlite:///db/tantar.db")
SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session


__all__ = [
    "get_db",
    "engine",
    "Account",
    "User",
    "Company",
    "File",
    "CompanyDetails",
    "Event",
    "Person",
    "PhysicalPerson",
    "MoralPerson",
    "Contract",
    "PVAG",
    "Shares",
    "Role",
]
