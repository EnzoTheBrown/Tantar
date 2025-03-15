from enum import Enum
from pydantic import BaseModel, Field


class FileType(str, Enum):
    CONTRAT = 'CONTRAT'
    PROCES_VERBAL_D_ASSEMBLEE_GENERALE = "Proces verbal d'assemblee generale"
    REGISTRE_DE_MOUVEMENT_DE_TITRES = 'Registre de mouvement de titres'


class FileTypeModel(BaseModel):
    file_type: FileType = Field(..., title="Type de fichier")


class JuridicCategory(str, Enum):
    CARACTERISTIQUES_DE_LA_SOCIETE = "Caractéristiques de la société"
    MODIFICATIONS_STATUTAIRES = "Modifications statutaires"
    CAPITAL = "Capital"
    CAPITAUX_PROPRES = "Capitaux propres"
    COMPTES_ANNUELS = "Comptes annuels"
    FONDS_DE_COMMERCE = "Fonds de commerce"
    ASSOCIES = "Associés"
    AUTORISATIONS_DIVERSES = "Autorisations diverses"
    DIRIGEANTS = "Dirigeants"
    CONTROLE_DE_LA_SOCIETE = "Contrôle de la société"
    TITRES = "Titres"
    DISTRIBUTIONS = "Distributions"
    RESTRUCTURATION = "Restructuration"
    DISSOLUTION = "Dissolution"
    AUTRE = "Autre"


class EventType(str, Enum):
    TRANSFERT_DE_SIEGE_SOCIAL = "Transfert de siège social"
    AUTORISATION_DE_SOUSCRIPTION_A_UN_PRET_BANCAIRE = "Autorisation de souscription à un prêt bancaire"
    AUTORISATION_D_ACQUISITION_D_UN_IMMEUBLE = "Autorisation d'acquisition d'un immeuble"
    AUTORISATION_DE_CESSION_D_UN_IMMEUBLE = "Autorisation de cession d'un immeuble"
    AUTORISATION_DE_CESSION_D_UN_FONDS_DE_COMMERCE = "Autorisation de cession d'un fonds de commerce"
    AUTOSISATION_DE_PRISE_DE_PARTICIPATION = "Autorisation de prise de participation"
    AUTORISATION_DE_CESSION_D_ACTIONS = "Autorisation de cession d'actions"
    DECISION_D_EMISSION_D_OBLIGATIONS = "Décision d'émission d'obligations"
    DECISION_D_ATTRIBUTION_D_ACTION_GRATUITE = "Décision d'attribution d'action gratuite"
    AUTORISATION_DE_NANTISSEMENT_D_ACTIONS_OU_DE_PARTS = "Autorisation de nantissement d'actions ou de parts"
    AUTOSISATION_DE_CESSION_DE_MARQUE = "Autorisation de cession de marque"
    AUTORISATION_D_ACQUISITION_DE_MARQUE = "Autorisation d'acquisition de marque"
    DECISION_D_APPROBATION_DES_CONVENTIONS_REGLEMENTEES = "Décision d'approbation des conventions réglementées"
    AUTRE = "Autre"


class EventTypeModel(BaseModel):
    event_type: EventType = Field(..., title="Type d'événement")
    juridic_category: JuridicCategory = Field(..., title="Catégorie juridique")


class ContractType(str, Enum):
    """ Transfert de siège social """
    BAIL = "Bail"
    MISE_A_DISPOSITION_DE_LOCAL = "Mise à disposition de local"
    DOMICILIATION = "Domiciliation"
    ACTE_DE_CESSION_D_UN_IMMEUBLE = "Acte de cession d'un immeuble"
    ACTE_DE_CESSION_D_UN_LOCAL = "Acte de cession d'un local"
    CONTRAT_DE_SOUS_LOCATION = "Contrat de sous-location"

    """ Acquisition d'un immeuble """
    COMPROMIS_DE_VENTE = "Compromis de vente"

    """ Demande de prêt bancaire """
    PRET_BANCAIRE = "Prêt bancaire"

    """ Emission de titres """
    BON_DE_SOUSCRIPTION = "Bon de souscription"
    BON_DE_SOUSCRIPTION_D_ACTION = "Bon de souscription d'action"
    ACTE_DE_CESSION_D_ACTION = "Acte de cessation d'action"
    BULLETIN_DE_SOUSCRIPTION = "Bulletin de souscription"
    PV_DE_CONSTATATION_D_AUGMENTATION_DE_CAPITAL = "PV de constatation d'augmentation de capital"
    PROTOCOL_DE_CESSION = "Protocole de cession"
    FORMULAIRE_2759 = "Formulaire 2759"
    ORDRE_DE_MOUVEMENT_DE_TITRES = "Ordre de mouvement de titres"
    CONTRAT_D_EMISSION_D_OBLIGATIONS = "Contrat d'émission d'obligations"
    PLAN_D_ATTRIBUTION_D_ACTION_GRATUITE = "Plan d'attribution d'action gratuite"
    ETAT_DES_INSCRIPTIONS_DES_PRIVILEGES_ET_NANTISSEMENTS = "Etat des inscriptions des privilèges et nantissements"

    """ Cession de marque """
    ACTE_DE_CESSION_DE_MARQUE = "Acte de cession de marque"

    """ Conventions réglementées """
    RAPPORT_SPECIAL_DU_COMMISSAIRE_AU_COMPTES = "Rapport spécial du commissaire aux comptes"

    """ Autre """
    AUTRE = "Autre"


class ContractTypeModel(BaseModel):
    contract_type: ContractType = Field(..., title="Type de contrat")

