from fastapi import Depends, APIRouter, Query
from schemas.model import GraphNode, GraphEdge
from tantar.graph import get_nodes, get_neighbors
from tantar.database import get_db, Session
from sqlmodel import select
from typing import List, Optional

graph_router = APIRouter()


@graph_router.get("/graph")
def get_graph(
    db: Session = Depends(get_db),
):
    nodes = get_nodes(db)
    edges = db.exec(select(GraphEdge)).all()
    return {"nodes": nodes, "edges": edges}


@graph_router.get("/graph/edges")
def get_neighbors_(
    source_id: Optional[str] = Query(None),
    label: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    neighbors = get_neighbors(db, source_id, label)
    return neighbors
