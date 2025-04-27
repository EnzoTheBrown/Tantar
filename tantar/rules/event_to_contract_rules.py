from schemas.file_model import ContractType
from schemas.model import EventDBModel, EventType, ContractChunk, Event
from tantar.vector_database import get_contract_chunks_in_vector_db
from typing import List, Optional
from datetime import timedelta


def within_6_months(event: EventDBModel) -> str:
    """Days in lanceDB are in format 'YYYY-MM-DD'"""
    if event.date is None:
        return "1 = 1"
    _3_months_before = event.date - timedelta(days=90)
    _3_months_after = event.date + timedelta(days=90)
    return f"date>='{_3_months_before}' AND date<='{_3_months_after}'"


async def find_matching_contract_chunks(
    account_id: str,
    siren: str,
    event: Event,
) -> Optional[List[ContractChunk]]:
    match event.type:
        case EventType.TRANSFERT_DE_SIEGE_SOCIAL:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND (
                           type='{ContractType.BAIL.value.replace("'", "''")}'
                        OR type='{ContractType.MISE_A_DISPOSITION_DE_LOCAL.value.replace("'", "''")}'
                        OR type='{ContractType.DOMICILIATION.value.replace("'", "''")}'
                        OR type='{ContractType.ACTE_DE_CESSION_D_UN_IMMEUBLE.value.replace("'", "''")}'
                        OR type='{ContractType.ACTE_DE_CESSION_D_UN_LOCAL.value.replace("'", "''")}'
                        OR type='{ContractType.CONTRAT_DE_SOUS_LOCATION.value.replace("'", "''")}'
                        )
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTORISATION_DE_SOUSCRIPTION_A_UN_PRET_BANCAIRE:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND type='{ContractType.PRET_BANCAIRE.value.replace("'", "''")}'
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTORISATION_D_ACQUISITION_D_UN_IMMEUBLE:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND type='{ContractType.ACTE_DE_CESSION_D_UN_IMMEUBLE.value.replace("'", "''")}'
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTORISATION_DE_CESSION_D_UN_IMMEUBLE:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND type='{ContractType.ACTE_DE_CESSION_D_UN_IMMEUBLE.value.replace("'", "''")}'
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTORISATION_DE_CESSION_D_UN_FONDS_DE_COMMERCE:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND type='{ContractType.ACTE_DE_CESSION_D_UN_LOCAL.value.replace("'", "''")}'
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTOSISATION_DE_PRISE_DE_PARTICIPATION:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND (
                           type='{ContractType.BON_DE_SOUSCRIPTION.value.replace("'", "''")}'
                        OR type='{ContractType.BON_DE_SOUSCRIPTION_D_ACTION.value.replace("'", "''")}'
                        OR type='{ContractType.ACTE_DE_CESSION_D_ACTION.value.replace("'", "''")}'
                        OR type='{ContractType.BULLETIN_DE_SOUSCRIPTION.value.replace("'", "''")}'
                        OR type='{ContractType.PV_DE_CONSTATATION_D_AUGMENTATION_DE_CAPITAL.value.replace("'", "''")}'
                    )
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTORISATION_DE_CESSION_D_ACTIONS:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND (
                           type='{ContractType.PROTOCOL_DE_CESSION.value.replace("'", "''")}'
                        OR type='{ContractType.FORMULAIRE_2759.value.replace("'", "''")}'
                        OR type='{ContractType.ORDRE_DE_MOUVEMENT_DE_TITRES.value.replace("'", "''")}'
                        OR type='{ContractType.ACTE_DE_CESSION_D_ACTION.value.replace("'", "''")}'
                    )
                    AND {within_6_months(event)}
                """,
            )
        case EventType.DECISION_D_EMISSION_D_OBLIGATIONS:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND type='{ContractType.CONTRAT_D_EMISSION_D_OBLIGATIONS.value.replace("'", "''")}'
                    AND {within_6_months(event)}
                """,
            )
        case EventType.DECISION_D_ATTRIBUTION_D_ACTION_GRATUITE:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND type='{ContractType.PLAN_D_ATTRIBUTION_D_ACTION_GRATUITE.value.replace("'", "''")}'
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTORISATION_DE_NANTISSEMENT_D_ACTIONS_OU_DE_PARTS:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND type='{ContractType.ETAT_DES_INSCRIPTIONS_DES_PRIVILEGES_ET_NANTISSEMENTS.value.replace("'", "''")}'
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTOSISATION_DE_CESSION_DE_MARQUE:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND (type='{ContractType.ACTE_DE_CESSION_DE_MARQUE.value.replace("'", "''")}')
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTORISATION_D_ACQUISITION_DE_MARQUE:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{siren}'
                    AND (type='{ContractType.ACTE_DE_CESSION_DE_MARQUE.value.replace("'", "''")}')
                    AND {within_6_months(event)}
                """,
            )
        case EventType.DECISION_D_APPROBATION_DES_CONVENTIONS_REGLEMENTEES:
            return get_contract_chunks_in_vector_db(
                question=event.text,
                metadata=f"""
                        account_id='{account_id}'
                    AND siren='{event.siren}'
                    AND (type='{ContractType.RAPPORT_SPECIAL_DU_COMMISSAIRE_AU_COMPTES.value.replace("'", "''")}')
                    AND {within_6_months(event)}
                """,
            )
        case EventType.AUTRE:
            return None
