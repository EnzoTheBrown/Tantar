from schemas.model import (
    GraphNode,
    GraphEdge,
    File,
    EventInput,
    Company,
    MoralPerson,
    PhysicalPerson,
)
from typing import Union
from sqlmodel import select

Node = Union[Company, File, EventInput, MoralPerson, PhysicalPerson]


def create_node(db, entity: Node) -> GraphNode:
    node = GraphNode(
        label=entity.__class__.__name__,
        original_id=entity.original_id,
        name=entity.name,
    )

    db.add(node)
    db.commit()

    return node


def get_node(db, original_id: str) -> GraphNode:
    return db.exec(
        select(GraphNode).where(GraphNode.original_id == original_id)
    ).first()


def create_edge(db, source: Node, target: Node, label: str) -> GraphEdge:
    source_node = get_node(db, source.original_id)
    target_node = get_node(db, target.original_id)

    if source_node is None or target_node is None:
        raise ValueError("Source or target node not found")

    edge = GraphEdge(source=source_node, target=target_node, label=label)

    db.add(edge)
    db.commit()

    return edge
