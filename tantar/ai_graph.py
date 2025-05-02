from sqlmodel import Session
from tantar.database import engine

from tantar.model.tokenizer import tokenize_paragraphs
from pydantic_graph import BaseNode, End, Graph, GraphRunContext
from dataclasses import dataclass
from typing import List, Optional, Tuple, Any
from tantar.model.classifier import classify_file, classify_contract
from tantar.model.parser import (
    extract_events,
    extract_shares_agent,
    Share,
    extract_relationships,
    RelationShip,
    extract_document_metadata,
    extract_persons,
    extract_contract_parties,
)
from schemas.file_model import FileType, ContractType
from schemas.model import (
    FileMetadata,
    Person,
    ContractChunkInput,
    EventInput,
    EdgeLabel,
    NodeType,
    PhysicalPerson,
    MoralPerson,
)
from tantar.pdf_to_image import pdf2images
from tantar.model.ocr import get_blocks, get_page_plane_text
from tantar.rules.event_to_contract_rules import find_matching_contract_chunks
from tantar.settings import SETTINGS
from uuid import uuid4
from tantar.vector_database import (
    post_event,
    post_contract_chunk,
)
from tantar.controller import (
    get_or_create_company,
    save_company_details,
    save_event,
    get_events,
    get_event,
    get_file,
    get_file_by_original_id,
    get_file_by_original_id,
    get_company,
    add_company_to_file,
    save_person,
)
from tantar.pappers import create_company_details
from tantar.graph import create_node, create_edge

s3 = SETTINGS.s3.client


@dataclass
class DocumentState:
    file_id: Optional[str] = None
    company_id: Optional[str] = None
    file_bytes: Optional[List[bytes]] = None
    pages: Optional[List[str]] = None
    metadata: Optional[FileMetadata] = None
    type: Optional[FileType] = None
    contract_type: Optional[ContractType] = None
    event_ids: Optional[List[str]] = None
    shares: Optional[List[Share]] = None
    relationships: Optional[List[RelationShip]] = None
    persons: Optional[List[Person]] = None
    contract_event_fit: Optional[Tuple[str, str]] = None
    text_blocks: Optional[List[str]] = None
    account_id: Optional[str] = None
    session: Optional[Any] = None


@dataclass
class GraphDB(BaseNode[DocumentState]):
    state_name: str = "graph_db"
    description: str = "Store relationships in the database"

    async def run(self, context: GraphRunContext) -> End:
        pass


class ContractEventFit(BaseNode[DocumentState]):
    state_name: str = "contract_event_fit"
    description: str = "Recherche d'un événement juridique correspondant au contrat"

    async def run(self, context: GraphRunContext) -> End:
        contract_event_fit = []
        with Session(engine) as db:
            for event_id in context.state.event_ids:
                event = get_event(db, event_id)
                file = get_file(db, event.file_id)
                chunks = await find_matching_contract_chunks(
                    account_id=file.account.original_id,
                    siren=context.state.metadata.siren,
                    event=event,
                )
                if chunks:
                    contract_event_fit.append((event, chunks[0].original_id))
                    with Session(engine) as db:
                        contract_file = get_file_by_original_id(db, chunks[0].file_id)
                        create_edge(db, event, contract_file, EdgeLabel.AUTHORIZED)

            context.state.contract_event_fit = contract_event_fit
        return End(data=context.state.contract_event_fit)


@dataclass
class ExtractPersonsOnEvents(BaseNode[DocumentState]):
    state_name: str = "extract_persons_on_events"
    description: str = "Extraction des personnes sur les événements juridiques"

    async def run(self, context: GraphRunContext) -> ContractEventFit:
        event_ids = context.state.event_ids
        if event_ids is None:
            raise ValueError("Events not found in context state.")
        persons = []
        for event_id in event_ids:
            with Session(engine) as db:
                event = get_event(db, event_id)
                persons += await extract_persons(event)
                for person in persons:
                    if isinstance(person, PhysicalPerson):
                        create_node(db, person, NodeType.PHYSICAL_PERSON)
                        create_edge(db, event, person, EdgeLabel.IS_MENTIONED)
                    elif isinstance(person, MoralPerson):
                        create_node(db, person, NodeType.MORAL_PERSON)
                        create_edge(db, event, person, EdgeLabel.IS_MENTIONED)
        context.state.persons = persons
        return ContractEventFit()


@dataclass
class ExtractEvents(BaseNode[DocumentState]):
    state_name: str = "extract_events"
    description: str = "Extraction des événements juridiques dans le document"

    async def run(self, context: GraphRunContext) -> ExtractPersonsOnEvents:
        events = await extract_events(context.state.pages)
        file_metadata = context.state.metadata
        db_events = []
        with Session(engine) as db:
            file = get_file(db, context.state.file_id)
            company = get_company(db, context.state.company_id)
            for event in events:
                event_db = save_event(db, event, file_metadata.date, file.id)
                create_edge(db, file, event_db, EdgeLabel.DECIDES)
                event_input = EventInput(
                    original_id=event_db.original_id,
                    account_id=file.account.original_id,
                    company_id=company.original_id,
                    file_id=file.original_id,
                    date=file_metadata.date.strftime("%Y-%m-%d"),
                    text=event.text,
                    title=event.title,
                    label=event.label,
                    type=event.type,
                    page_index=event.page_index,
                    file_name=file.name,
                    siren=company.siren,
                )
                post_event(event_input)
                db_events.append(event_db)
            context.state.event_ids = [event.id for event in db_events]
        return ExtractPersonsOnEvents()


@dataclass
class NormalizePersonsNames(BaseNode[DocumentState]):
    state_name: str = "normalize_persons_names"
    description: str = "Normalisation des noms des personnes"

    async def run(self, context: GraphRunContext) -> End:
        return End(data=None)


@dataclass
class ExtractRelationships(BaseNode[DocumentState]):
    state_name: str = "extract_relationships"
    description: str = "Extraction des relations entre les parties prenantes"

    async def run(self, context: GraphRunContext) -> End:
        if context.state.pages is None:
            raise ValueError("Pages not found in context state.")
        relationships = await extract_relationships(context.state.pages)
        context.state.relationships = relationships
        return End(data=relationships)


@dataclass
class ExtractShares(BaseNode[DocumentState]):
    state_name: str = "extract_shares"
    description: str = "Extraction des mouvements de titres dans le document"

    async def run(self, context: GraphRunContext) -> ExtractRelationships:
        if context.state.pages is None:
            raise ValueError("Pages not found in context state.")
        shares = await extract_shares_agent.run(context.state.pages)
        context.state.shares = shares
        return ExtractRelationships()


@dataclass
class GetEvents(BaseNode[DocumentState]):
    state_name: str = "get_events"
    description: str = "Récupération des événements juridiques"

    async def run(self, context: GraphRunContext) -> ContractEventFit:
        with Session(engine) as db:
            file = get_file(db, context.state.file_id)
            events = get_events(
                db,
                account_id=file.account_id,
                siren=context.state.metadata.siren,
            )
            context.state.event_ids = [event.id for event in events]
        return ContractEventFit()


@dataclass
class ContractChunk(BaseNode[DocumentState]):
    state_name: str = "contract_chunk"
    description: str = "Extraction des morceaux de contrat"

    async def run(self, context: GraphRunContext) -> GetEvents:
        with Session(engine) as db:
            text_blocks = context.state.text_blocks
            file = get_file(db, context.state.file_id)
            company = get_company(db, context.state.company_id)
            file_metadata = context.state.metadata
            contract_type = context.state.contract_type
            paragraphs = tokenize_paragraphs(text_blocks)
            for paragraph in paragraphs:
                contract_chunk = ContractChunkInput(
                    original_id=str(uuid4()),
                    account_id=file.account.original_id,
                    company_id=company.original_id,
                    file_id=file.original_id,
                    date=file_metadata.date.strftime("%Y-%m-%d")
                    if file_metadata.date
                    else None,
                    text=paragraph.text,
                    title=file_metadata.title,
                    page_index=paragraph.page_index,
                    file_name=file.name,
                    siren=company.siren,
                    type=contract_type,
                )
                post_contract_chunk(contract_chunk)
            return GetEvents()


@dataclass
class ContractPartiesParser(BaseNode[DocumentState]):
    state_name: str = "contract_offeror_parser"
    description: str = "Extraction de l'offreur de contrat"

    async def run(self, context: GraphRunContext) -> ContractChunk:
        if context.state.pages is None:
            raise ValueError("Pages not found in context state.")
        parties = await extract_contract_parties(context.state.pages)
        with Session(engine) as db:
            file = get_file(db, context.state.file_id)
            offeror = parties.offeror
            if offeror:
                person = save_person(db, offeror, account_id=context.state.account_id)
                create_edge(db, file, person, EdgeLabel.SIGNS)
            offeree = parties.offeree
            if offeree:
                person = save_person(db, offeree, account_id=context.state.account_id)
                create_edge(db, file, person, EdgeLabel.SIGNS)
        return ContractChunk()


@dataclass
class ContractClassifier(BaseNode[DocumentState]):
    state_name: str = "contract_classifier"
    description: str = "Classification du contrat"

    async def run(self, context: GraphRunContext) -> ContractPartiesParser:
        if context.state.pages is None:
            raise ValueError("Pages not found in context state.")
        contract_type = await classify_contract(context.state.pages)
        context.state.contract_type = contract_type
        return ContractPartiesParser()


@dataclass
class ExtractDocumentMetadata(BaseNode[DocumentState]):
    state_name: str = "extract_document_metadata"
    description: str = "Extraction des métadonnées du document"

    async def run(
        self, context: GraphRunContext
    ) -> ExtractEvents | ExtractShares | ContractClassifier | End:
        if context.state.pages is None:
            raise ValueError("Pages not found in context state.")
        metadata = await extract_document_metadata(context.state.pages)
        context.state.metadata = metadata
        if metadata.siren is None:
            return End(data=None)
        with Session(engine) as db:
            file = get_file(db, context.state.file_id)
            created, company = get_or_create_company(
                db,
                name=metadata.name or "",
                siren=metadata.siren,
                account_id=context.state.account_id,
            )
            add_company_to_file(db, file, company)
            if created:
                # company_details = create_company_details(company)
                save_company_details(db, company_details)
            db.refresh(company)
            context.state.company_id = company.id
            match context.state.type:
                case FileType.CONTRAT:
                    create_node(db, file, NodeType.CONTRACT)
                    create_edge(db, file, company, EdgeLabel.SIGNS)
                    next_state = ContractClassifier()
                case FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE:
                    create_node(db, file, NodeType.PV_AG)
                    create_edge(db, file, company, EdgeLabel.ORGANIZED)
                    next_state = ExtractEvents()
                case FileType.REGISTRE_DE_MOUVEMENT_DE_TITRES:
                    create_node(db, file, NodeType.MVT)
                    create_edge(db, file, company, EdgeLabel.BELONGS_TO)
                    next_state = ExtractShares()
                case _:
                    next_state = End(data=None)
        return next_state


@dataclass
class DocumentClassifier(BaseNode[DocumentState]):
    state_name: str = "document_classifier"
    description: str = "Classification du document"

    async def run(self, context: GraphRunContext) -> ExtractDocumentMetadata:
        if context.state.pages is None:
            raise ValueError("Pages not found in context state.")
        file_type = await classify_file(context.state.pages)
        context.state.type = file_type
        return ExtractDocumentMetadata()


@dataclass
class OCR(BaseNode[DocumentState]):
    state_name: str = "ocr"
    description: str = "OCR sur le document"

    async def run(self, context: GraphRunContext) -> DocumentClassifier:
        if context.state.file_bytes is None:
            raise ValueError("File bytes not found in context state.")
        text_blocks = [
            get_blocks(image_byte) for image_byte in context.state.file_bytes
        ]
        context.state.text_blocks = text_blocks
        pages = [get_page_plane_text(blocks) for blocks in text_blocks]
        context.state.pages = pages
        return DocumentClassifier()


@dataclass
class PDFToImage(BaseNode[DocumentState]):
    state_name: str = "pdf_to_image"
    description: str = "Conversion du PDF en images"

    async def run(self, context: GraphRunContext) -> OCR:
        if context.state.file_id is None:
            raise ValueError("File not found in context state.")
        with Session(engine) as db:
            file = get_file(db, context.state.file_id)
            s3_path = file.s3_path
            images = pdf2images(s3_path, company_id="images")
            image_bytes = [
                s3.get_object(Bucket="tantar", Key=image["image_name"])["Body"].read()
                for image in images
            ]
            context.state.file_bytes = image_bytes
        return OCR()


graph = Graph(
    nodes=[
        DocumentClassifier,
        ExtractDocumentMetadata,
        ExtractEvents,
        ExtractShares,
        ExtractRelationships,
        ExtractPersonsOnEvents,
        NormalizePersonsNames,
        PDFToImage,
        OCR,
        ContractClassifier,
        ContractChunk,
        ContractEventFit,
        GetEvents,
        ContractPartiesParser,
    ]
)
