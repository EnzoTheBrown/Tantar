import pytest
from schemas.model import File, Account, User, Company, NodeType
from sqlmodel import select
from tantar.graph import create_node, create_edge
from tantar.database import get_db
from tantar.settings import SETTINGS
import uuid


@pytest.fixture
def db():
    return next(get_db())


@pytest.fixture
def account(db):
    account = Account(name="test_account")
    db.add(account)
    db.commit()
    db.refresh(account)
    yield account
    db.delete(account)
    db.commit()


@pytest.fixture
def user(db, account):
    user = User(email="enzo.the@gmail.com", hashed_password="password", account=account)
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture
def company(db, account):
    company = Company(name="test_company", siren="123456789", account=account)
    create_node(db, company, type=NodeType.COMPANY)
    db.add(company)
    db.commit()
    db.refresh(company)
    yield company
    db.delete(company)
    db.commit()


@pytest.fixture
def pv_ag(db, account, company):
    name = "datasets/CLARTE AUTOMOBILES/CLARTE AUTOMOBILES - Actes du 03-11-2016.pdf"
    s3 = SETTINGS.s3.client
    s3_key = f"{account.original_id}/{uuid.uuid4()}.pdf"
    with open(name, "rb") as f:
        s3.put_object(
            Bucket=SETTINGS.s3.bucket,
            Key=s3_key,
            Body=f.read(),
        )
    file = File(
        name="CLARTE AUTOMOBILES - Actes du 03-11-2016.pdf",
        account=account,
        s3_path=s3_key,
        company=company,
    )
    create_node(db, file, NodeType.PV_AG)
    db.add(file)
    db.commit()
    db.refresh(file)
    yield file
    db.delete(file)
    db.commit()
    s3.delete_object(Bucket=SETTINGS.s3.bucket, Key=s3_key)


@pytest.fixture
def contract(db, account, company):
    name = "datasets/CLARTE AUTOMOBILES/FAUX CONTRAT DE BAIL COMMERCIAL 2016.pdf"
    s3 = SETTINGS.s3.client
    s3_key = f"{account.original_id}/{uuid.uuid4()}.pdf"
    with open(name, "rb") as f:
        s3.put_object(
            Bucket=SETTINGS.s3.bucket,
            Key=s3_key,
            Body=f.read(),
        )
    file = File(
        name="FAUX CONTRAT DE BAIL COMMERCIAL 2016.pdf",
        account=account,
        s3_path=s3_key,
        company=company,
    )
    create_node(db, file, NodeType.CONTRACT)
    db.add(file)
    db.commit()
    db.refresh(file)
    yield file
    db.delete(file)
    db.commit()
    s3.delete_object(Bucket=SETTINGS.s3.bucket, Key=s3_key)
