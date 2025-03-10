from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from schemas.model import Account, User, Company, File, CompanyDetails

engine = create_engine("sqlite:///db/tantar.db")
SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

__all__ = ['Account', 'User', 'Company', 'File', 'CompanyDetails']
