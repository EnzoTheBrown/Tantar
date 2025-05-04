from sqlmodel import select
from schemas.relational import (
    Company,
)
from typing import Tuple


async def get_or_create_company(
    db, name: str, siren: str, account_id: str
) -> Tuple[bool, Company]:
    company = db.exec(
        select(Company).where(Company.account_id == account_id, Company.siren == siren)
    ).first()
    if not company:
        company = Company(name=name, siren=siren, account_id=account_id)
        db.add(company)
        db.commit()
        db.refresh(company)
        return True, company
    return False, company
