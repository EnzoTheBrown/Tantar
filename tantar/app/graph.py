from fastapi import Depends, APIRouter
from tantar.database import get_db
from schemas.relational import (
    Company,
    File,
    Event,
    Person,
    MoralPerson,
    PhysicalPerson,
    Shares,
    Role,
    Contract,
    PVAG,
    OrdreDeMouvement,
    RegistreDeMouvementDeTitres,
    AuthorizedContract,
)
from sqlmodel import select

graph_router = APIRouter()
