import pytest
from schemas.relational import File, User, Company
from tantar.database import get_db
from tantar.settings import SETTINGS
import uuid


@pytest.fixture
def db():
    return next(get_db())


@pytest.fixture
def user(db):
    user = User(email="enzo.the@gmail.com", hashed_password="password", account_name="")
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.delete(user)
    db.commit()


@pytest.fixture
def company(db, user):
    company = Company(name="test_company", siren="123456789", user=user)
    db.add(company)
    db.commit()
    db.refresh(company)
    yield company
    db.delete(company)
    db.commit()


@pytest.fixture
def pv_ag(db, user, company):
    name = "datasets/CLARTE AUTOMOBILES/CLARTE AUTOMOBILES - Actes du 03-11-2016.pdf"
    s3 = SETTINGS.s3.client
    s3_key = f"{user.original_id}/{uuid.uuid4()}.pdf"
    with open(name, "rb") as f:
        s3.put_object(
            Bucket=SETTINGS.s3.bucket,
            Key=s3_key,
            Body=f.read(),
        )
    file = File(
        name="CLARTE AUTOMOBILES - Actes du 03-11-2016.pdf",
        user=user,
        s3_path=s3_key,
        company=company,
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    yield file
    db.delete(file)
    db.commit()
    s3.delete_object(Bucket=SETTINGS.s3.bucket, Key=s3_key)


@pytest.fixture
def contract(db, user, company):
    name = "datasets/CLARTE AUTOMOBILES/FAUX CONTRAT DE BAIL COMMERCIAL 2016.pdf"
    s3 = SETTINGS.s3.client
    s3_key = f"{user.original_id}/{uuid.uuid4()}.pdf"
    with open(name, "rb") as f:
        s3.put_object(
            Bucket=SETTINGS.s3.bucket,
            Key=s3_key,
            Body=f.read(),
        )
    file = File(
        name="FAUX CONTRAT DE BAIL COMMERCIAL 2016.pdf",
        user=user,
        s3_path=s3_key,
        company=company,
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    yield file
    db.delete(file)
    db.commit()
    s3.delete_object(Bucket=SETTINGS.s3.bucket, Key=s3_key)
