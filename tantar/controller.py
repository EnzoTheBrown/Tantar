from sqlmodel import select
from schemas.model import (
    Company,
    File,
    CompanyDetails,
    Event,
    EventDBModel,
    MoralPerson,
    PhysicalPerson,
    MoralPersonModel,
    PhysicalPersonModel,
    Person,
)
from typing import Tuple
from tantar.graph import create_node, NodeType


def get_or_create_company(
    db, name: str, siren: str, account_id: str
) -> Tuple[bool, Company]:
    company = db.exec(
        select(Company).where(Company.account_id == account_id, Company.siren == siren)
    ).first()
    if not company:
        company = Company(name=name, siren=siren, account_id=account_id)
        create_node(db, company, NodeType.COMPANY)
        db.add(company)
        db.commit()
        db.refresh(company)
        return True, company
    return False, company


def save_company_details(db, company_details: CompanyDetails) -> CompanyDetails:
    db.add(company_details)
    db.commit()
    db.refresh(company_details)
    return company_details


def save_event(db, event: Event, date, file_id) -> EventDBModel:
    event_db = EventDBModel(
        type=event.type,
        label=event.label,
        title=event.title,
        page_index=event.page_index,
        text=event.text,
        date=date,
        file_id=file_id,
    )
    db.add(event_db)
    db.commit()
    db.refresh(event_db)
    create_node(db, event_db, NodeType.EVENT)
    return event_db


def get_events(db, account_id: str, siren: str) -> list[EventDBModel]:
    events = db.exec(
        select(EventDBModel)
        .join(File)
        .join(Company)
        .where(File.account_id == account_id, Company.siren == siren)
    ).all()
    return events


def get_event(db, event_id: str) -> EventDBModel:
    event = db.exec(select(EventDBModel).where(EventDBModel.id == event_id)).first()
    if event is None:
        raise ValueError("Event not found")
    return event


def get_file(db, file_id: str) -> File:
    file = db.exec(select(File).where(File.id == file_id)).first()
    if file is None:
        raise ValueError("File not found")
    return file


def get_file_by_original_id(db, original_id: str) -> File:
    file = db.exec(select(File).where(File.original_id == original_id)).first()
    if file is None:
        raise ValueError("File not found")
    return file


def get_company(db, company_id: str) -> Company:
    company = db.exec(select(Company).where(Company.id == company_id)).first()
    if company is None:
        raise ValueError("Company not found")
    return company


def save_moral_person(db, person: MoralPersonModel, account_id: int) -> MoralPerson:
    person = MoralPerson(
        name=person.name,
        account_id=account_id,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    create_node(db, person, NodeType.MORAL_PERSON)
    return person


def save_physical_person(
    db, person: PhysicalPersonModel, account_id: int
) -> PhysicalPerson:
    person = PhysicalPerson(
        first_name=person.first_name,
        last_name=person.last_name,
        account_id=account_id,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    create_node(db, person, NodeType.PHYSICAL_PERSON)
    return person


def save_person(db, person: Person, account_id: int) -> Person:
    if isinstance(person, PhysicalPersonModel):
        person = save_physical_person(db, person, account_id)
    elif isinstance(person, MoralPersonModel):
        person = save_moral_person(db, person, account_id)
    else:
        raise ValueError("Unknown person type")
    return person


def add_company_to_file(db, file: File, company: Company) -> None:
    file.company = company
    db.add(file)
    db.commit()
    db.refresh(file)
