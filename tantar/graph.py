from schemas.model import (
    GraphNode,
    GraphEdge,
    File,
    EventInput,
    Company,
    MoralPerson,
    PhysicalPerson,
    NodeType,
)
from typing import Union, Optional, List
from sqlmodel import select, Session
from tantar.database import engine

Node = Union[Company, File, EventInput, MoralPerson, PhysicalPerson]


def create_node(db, entity: Node, type: NodeType) -> GraphNode:
    node = GraphNode(
        type=type,
        original_id=entity.original_id,
        name=entity.name,
    )

    db.add(node)
    db.commit()

    return node


def get_node(db, original_id: str) -> Optional[GraphNode]:
    node = db.exec(
        select(GraphNode).where(GraphNode.original_id == original_id)
    ).first()
    if node is None:
        raise ValueError("Node not found")
    return node


def create_edge(db, source: Node, target: Node, label: str) -> GraphEdge:
    source_node = get_node(db, source.original_id)
    target_node = get_node(db, target.original_id)
    if source_node is None:
        raise ValueError("Source node not found")
    if target_node is None:
        raise ValueError("Target node not found")
    edge = GraphEdge(source=source_node, target=target_node, label=label)
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return edge


def get_nodes(db) -> list[GraphNode]:
    nodes = db.exec(select(GraphNode)).all()
    return nodes


def get_neighbors(
    db, source_id: Optional[str], label: Optional[str] = None
) -> Optional[List[GraphEdge]]:
    node = db.exec(select(GraphNode).where(GraphNode.original_id == source_id)).first()
    if node is None:
        raise ValueError("Node not found")
    clauses = (GraphEdge.source_id == node.id) if source_id else True
    if label:
        clauses &= GraphEdge.label == label
    return db.exec(select(GraphEdge).where(clauses)).all()
