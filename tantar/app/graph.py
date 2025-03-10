from tantar.settings import SETTINGS
from fastapi import Depends, HTTPException, APIRouter, Query
from schemas.model import (
    GraphNode,
    GraphEdge,
)
from tantar.database import get_db, Session
from sqlmodel import select

graph_router = APIRouter()


@graph_router.get("/graph")
def get_graph(
    db: Session = Depends(get_db),
):
    nodes = db.exec(select(GraphNode)).all()
    edges = db.exec(select(GraphEdge)).all()
    return {"nodes": nodes, "edges": edges}
