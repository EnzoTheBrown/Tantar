from fastapi import Depends, HTTPException, APIRouter, Query
from schemas.relational import (
    Company,
    File,
    JuridicCategory,
    User,
    EventCategoriesAPIModel,
    Account,
    Event,
)
from schemas.vector import EventInput
from tantar.database import get_db, Session
from sqlmodel import select
from typing import Optional
from tantar.utils.logger import get_logger
from tantar.vector_database import get_events, post_event
from .authenticate import get_current_user
import uuid

logger = get_logger(__name__)

event_router = APIRouter()


@event_router.post("/company/{original_id}/event", status_code=201)
async def create_event(
    original_id: str,
    event: EventInput,
    db: Session = Depends(get_db),
):
    db_company = db.exec(
        select(Company).where(Company.original_id == original_id)
    ).first()
    file = db.exec(select(File).where(File.original_id == event.file_id)).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    new_event = EventInput(
        original_id=str(uuid.uuid4()),
        account_id=file.account_id,
        company_id=db_company.id,
        file_id=event.file_id,
        date=event.date,
        label=JuridicCategory.AUTORISATIONS_DIVERSES,
        text=event.text,
        title=event.title,
        page_index=event.page_index,
        file_name=file.name,
        siren=db_company.siren,
    )
    post_event(new_event)
    event_model = Event.model_validate(new_event)
    return event_model


@event_router.get(
    "/events",
    response_model=EventCategoriesAPIModel,
)
async def get_events_(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    question: Optional[str] = Query(None),
    k: int = Query(10),
    company_id: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_account = db.exec(select(Account).where(Account.id == user.account_id)).first()
    events = get_events(
        account_id=db_account.original_id,
        question=question,
        company_id=company_id,
        label=JuridicCategory._value2member_map_[label] if label is not None else None,
        k=k,
        start_date=start_date,
        end_date=end_date,
        siren=None,
    )
    categories = list(set([event.label for event in events]))
    events_db = []
    for event in events:
        event_db = db.exec(
            select(Event).where(Event.original_id == event.original_id)
        ).first()
        events_db.append(event_db)
    return EventCategoriesAPIModel(
        categories=categories,
        events=events_db,
    )


@event_router.get(
    "/categories",
)
def get_categories():
    return {category.name: category.value for category in JuridicCategory}
