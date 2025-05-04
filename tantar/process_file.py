from tantar.model.tokenizer import tokenize_paragraphs
from tantar.settings import SETTINGS
from tantar.pdf_to_image import pdf2images
from tantar.model.ocr import get_blocks, get_page_plane_text
from typing import List
from tantar.model.classifier import (
    classify_file,
    classify_contract,
    classify_person_exists,
    person_exists_agent,
)
from tantar.model.parser import (
    extract_events,
    extract_shares,
    extract_document_metadata,
    extract_persons,
    extract_contract_parties,
    extract_roles,
)
from schemas.file_model import (
    FileType,
    ContractType,
    JuridicCategory,
)
from schemas.relational import (
    Account,
    User,
    Company,
    File,
    Person,
    PhysicalPerson,
    MoralPerson,
    Event,
    Contract,
    Shares,
    Role,
    PVAG,
    CompanyDetails,
    Statuts,
    OrdreDeMouvement,
    RegistreDeMouvementDeTitres,
    AuthorizedContract,
    Offeror,
    Offeree,
)
from schemas.vector import (
    MoralPersonInput,
    PhysicalPersonInput,
    MoralPersonVector,
    PhysicalPersonVector,
    EventInput,
    EventVector,
    ContractChunkInput,
    ContractChunk,
)
from schemas.objects import FileMetadata, ContractParties
from tantar.database import engine
from tantar.vector_database import post_event, post_contract_chunk
from tantar.rules.event_to_contract_rules import find_matching_contract_chunks
from sqlmodel import select, Session
from uuid import uuid4
from tantar.controller import get_or_create_company
from tantar.pappers import create_company_details

s3 = SETTINGS.s3.client


async def pdf_to_images(pdf_path: str) -> List[bytes]:
    images = pdf2images(pdf_path, company_id="images")
    images_bytes = [
        s3.get_object(Bucket="tantar", Key=image["image_name"])["Body"].read()
        for image in images
    ]

    return images_bytes


async def ocr(file_bytes: list[bytes]):
    return [get_blocks(image_byte) for image_byte in file_bytes]


async def get_pages(text_blocks):
    return [get_page_plane_text(blocks) for blocks in text_blocks]


async def chunkify_contract(
    contract: Contract, text_blocks, file_metadata: FileMetadata
):
    paragraphs = tokenize_paragraphs(text_blocks)
    for paragraph in paragraphs:
        contract_chunk = ContractChunkInput(
            original_id=str(uuid4()),
            account_id=contract.file.account.original_id,
            company_id=contract.file.company.original_id,
            file_id=contract.file.original_id,
            date=file_metadata.date.strftime("%Y-%m-%d")
            if file_metadata.date
            else None,
            text=paragraph.text,
            title=file_metadata.title,
            page_index=paragraph.page_index,
            file_name=contract.file.name,
            siren=contract.file.company.siren,
            type=contract.type,
        )
        post_contract_chunk(contract_chunk)


async def handle_contract(
    db, file: File, file_metadata: FileMetadata, text_blocks, pages: List[str]
):
    contract_type = await classify_contract(pages)
    contract = Contract(
        file=file,
        type=contract_type,
        title=file.name,
    )
    db.add(contract)
    db.commit()
    await chunkify_contract(
        contract=contract,
        text_blocks=text_blocks,
        file_metadata=file_metadata,
    )
    events = db.exec(
        select(Event).join(PVAG).join(File).where(File.company_id == file.company_id)
    ).all()
    for event in events:
        await contract_event_fit(
            db=db,
            event=event,
            company=file.company,
        )
    parties = await extract_contract_parties(pages)

    offeror = parties.offeror
    person = Person(
        account_id=file.account_id,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    if offeror.__class__.__name__ == "MoralPerson":
        person_type = MoralPerson(
            name=offeror.name,
            account_id=file.account_id,
            person=person,
        )
    else:
        person_type = PhysicalPerson(
            firstname=offeror.firstname,
            lastname=offeror.lastname,
            account_id=file.account_id,
            person=person,
        )
    db.add(person_type)
    db.commit()
    offeror = Offeror(
        contract=contract,
        person=person,
    )
    db.add(offeror)
    db.commit()

    offeree = parties.offeree
    person = Person(
        account_id=file.account_id,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    if offeree.__class__.__name__ == "MoralPerson":
        person_type = MoralPerson(
            name=offeree.name,
            account_id=file.account_id,
            person=person,
        )
    else:
        person_type = PhysicalPerson(
            firstname=offeree.firstname,
            lastname=offeree.lastname,
            account_id=file.account_id,
            person=person,
        )
    db.add(person_type)
    db.commit()
    db.refresh(person_type)
    offeree = Offeree(
        contract=contract,
        person=person,
    )
    db.add(offeree)
    db.commit()


async def contract_event_fit(
    db,
    event: Event,
    company: Company,
):
    chunks = await find_matching_contract_chunks(
        account_id=company.account.original_id,
        siren=company.siren,
        event=event,
    )
    if chunks:
        contract = db.exec(
            select(Contract).where(Contract.id == chunks[0].original_id)
        ).first()
        if contract:
            AuthorizedContract(
                contract=contract,
                event=event,
            )
            db.add(AuthorizedContract)
            db.commit()


async def handle_pvag(db, file: File, pages: List[str], file_metadata: FileMetadata):
    pvag = PVAG(
        file=file,
    )
    db.add(pvag)
    db.commit()
    events = await extract_events(pages)
    db_events = []
    for event in events:
        event_db = Event(
            pvag=pvag,
            type=event.type,
            label=event.label,
            title=event.title,
            page_index=event.page_index,
            text=event.text,
        )
        db.add(event_db)
        db.commit()
        db.refresh(event_db)
        db_events.append(event_db)
        event_input = EventInput(
            original_id=event_db.original_id,
            account_id=file.account.original_id,
            company_id=file.company.original_id,
            file_id=file.original_id,
            date=file_metadata.date.strftime("%Y-%m-%d"),
            text=event.text,
            title=event.title,
            label=event.label,
            type=event.type,
            page_index=event.page_index,
            file_name=file.name,
            siren=file.company.siren,
        )
        post_event(event_input)
        await contract_event_fit(
            db=db,
            event=event_db,
            company=file.company,
        )


async def handle_statuts(db, file: File):
    statuts = Statuts(
        file=file,
    )
    db.add(statuts)
    db.commit()


async def handle_registre_de_mouvement_de_titre(db, file: File, pages: List[str]):
    registre = RegistreDeMouvementDeTitres(
        file=file,
    )
    db.add(registre)
    db.commit()
    shares_list = await extract_shares(pages)
    for shares in shares_list:
        person = Person(
            account_id=file.account_id,
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        if shares.person.__class__.__name__ == "MoralPerson":
            person_type = MoralPerson(
                name=shares.person.name,
                account_id=file.account_id,
                person=person,
            )
        else:
            person_type = PhysicalPerson(
                firstname=shares.person.firstname,
                lastname=shares.person.lastname,
                account_id=file.account_id,
                person=person,
            )
        db.add(person_type)
        db.commit()
        shares = Shares(
            person=person,
            shares=shares.shares,
            percentage=shares.percentage,
            company=file.company,
        )
        db.add(shares)
        db.commit()
        db.refresh(shares)

    roles = await extract_roles(pages)
    for role in roles:
        person = role.person
        role = role.role
        _person = Person(
            account_id=file.account_id,
        )
        db.add(_person)
        db.commit()
        db.refresh(_person)
        if person.__class__.__name__ == "MoralPerson":
            person_type = MoralPerson(
                name=person.name,
                account_id=file.account_id,
                person=_person,
            )
        else:
            person_type = PhysicalPerson(
                firstname=person.firstname,
                lastname=person.lastname,
                account_id=file.account_id,
                person=_person,
            )
        db.add(person_type)
        db.commit()
        db.refresh(person_type)
        role = Role(
            name=role,
            person=_person,
            company=file.company,
        )
        db.add(role)
        db.commit()
        db.refresh(role)


async def handle_ordre_mvt(db, file: File):
    ordre_mvt = OrdreDeMouvement(
        file=file,
    )
    db.add(ordre_mvt)
    db.commit()


async def route_on_filetype(
    db,
    file_type: FileType,
    file: File,
    pages: List[str],
    text_blocks,
    file_metadata: FileMetadata,
):
    match file_type:
        case FileType.CONTRAT:
            await handle_contract(db, file, file_metadata, text_blocks, pages)
        case FileType.PROCES_VERBAL_D_ASSEMBLEE_GENERALE:
            await handle_pvag(db, file, pages, file_metadata)
        case FileType.REGISTRE_DE_MOUVEMENT_DE_TITRES:
            await handle_registre_de_mouvement_de_titre(db, file, pages)
        case FileType.ORDRE_DE_MOUVEMENT_DE_TITRES:
            await handle_ordre_mvt(db, file)
        case FileType.STATUTS:
            await handle_statuts(db, file)
        case _:
            pass


async def process_file(
    db: Session,
    file: File,
) -> File:
    file_bytes = await pdf_to_images(file.s3_path)
    text_blocks = await ocr(file_bytes)
    pages = await get_pages(text_blocks)
    file_type = await classify_file(pages)
    file.type = file_type
    db.add(file)
    db.commit()
    db.refresh(file)

    file_metadata = await extract_document_metadata(pages)
    create, company = await get_or_create_company(
        db=db,
        name=file_metadata.name,
        siren=file_metadata.siren,
        account_id=file.account_id,
    )
    if create:
        company_details = create_company_details(company)
        db.add(company_details)
        db.commit()
        db.refresh(company_details)
        company.company_details = company_details
        db.add(company)
        db.commit()
        db.refresh(company)
    file.company = company
    db.add(file)
    db.commit()
    db.refresh(file)

    await route_on_filetype(
        db=db,
        file_type=file.type,
        file=file,
        pages=pages,
        text_blocks=text_blocks,
        file_metadata=file_metadata,
    )
    return file

