
export interface Company {
  original_id: string;
  name: string;
  siren: string;
  account?: {
    original_id: string;
    name: string;
  } | null;
  details?: {
    siren: string;
    name: string;
    naf_code: string;
    activity: string;
    capital: number | null;
    juridic_form: string | null;
  } | null;
  roles?: {
    name: string;
    person: {
      name: string;
      is_moral: boolean;
    }
  }[];
  shares?: {
    person: {
      name: string;
      is_moral: boolean;
    },
    percentage?: number;
    shares?: number;
  }[];
  files?: {
    name: string;
    id: string;
    file_type: string;
    offeror?: {
      name: string;
      is_moral: boolean;
    };
    offeree?: {
      name: string;
      is_moral: boolean;
    };
  }[];
}

export interface File {
  original_id: string;
  name: string;
  type?: FileType | null;
  s3_path: string;
  status: number;
  company: {
    original_id: string;
    name: string;
    siren: string;
  } | null;
  watched_at?: string | null;
  created_at: string;
}

export enum FileType {
  CONTRAT = "CONTRAT",
  PROCES_VERBAL = "Proces verbal d'assemblee generale",
  REGISTRE_TITRES = "Registre de mouvement de titres",
  ORDRE_TITRES = "Ordre de mouvement de titres",
  STATUTS = "Statuts"
}

export enum EventType {
  TRANSFERT_SIEGE = "Transfert de siège social",
  AUTORISATION_PRET = "Autorisation de souscription à un prêt bancaire",
  AUTORISATION_ACQUISITION_IMMEUBLE = "Autorisation d'acquisition d'un immeuble",
  AUTORISATION_CESSION_IMMEUBLE = "Autorisation de cession d'un immeuble",
  AUTORISATION_CESSION_FONDS = "Autorisation de cession d'un fonds de commerce",
  AUTORISATION_PRISE_PARTICIPATION = "Autorisation de prise de participation",
  AUTORISATION_CESSION_ACTIONS = "Autorisation de cession d'actions",
  EMISSION_OBLIGATIONS = "Décision d'émission d'obligations",
  ATTRIBUTION_ACTIONS = "Décision d'attribution d'action gratuite",
  AUTORISATION_NANTISSEMENT = "Autorisation de nantissement d'actions ou de parts",
  AUTORISATION_CESSION_MARQUE = "Autorisation de cession de marque",
  AUTORISATION_ACQUISITION_MARQUE = "Autorisation d'acquisition de marque",
  APPROBATION_CONVENTIONS = "Décision d'approbation des conventions réglementées",
  APPROBATION_COMPTES = "Décision d'approbation des comptes annuels",
  DISTRIBUTION_DIVIDENDES = "Décision de distribution de dividendes",
  AUGMENTATION_CAPITAL = "Augmentation de capital",
  REDUCTION_CAPITAL = "Réduction de capital",
  MODIFICATION_STATUTS = "Modification des statuts",
  NOMINATION_DIRIGEANTS = "Nomination des dirigeants",
  NOMINATION_CAC = "Nomination des commissaires aux comptes",
  FUSION = "Décision de fusion",
  SCISSION = "Décision de scission",
  DISSOLUTION = "Décision de dissolution et liquidation",
  TRANSFORMATION = "Transformation de la société",
  CHANGEMENT_OBJET = "Changement d'objet social",
  AUTRE = "Autre"
}

export enum JuridicCategory {
  CARACTERISTIQUES = "Caractéristiques de la société",
  MODIFICATIONS = "Modifications statutaires",
  CAPITAL = "Capital",
  CAPITAUX_PROPRES = "Capitaux propres",
  COMPTES_ANNUELS = "Comptes annuels",
  FONDS_COMMERCE = "Fonds de commerce",
  ASSOCIES = "Associés",
  AUTORISATIONS = "Autorisations diverses",
  DIRIGEANTS = "Dirigeants",
  CONTROLE = "Contrôle de la société",
  TITRES = "Titres",
  DISTRIBUTIONS = "Distributions",
  RESTRUCTURATION = "Restructuration",
  DISSOLUTION = "Dissolution",
  AUTRE = "Autre"
}

export interface PVAGModel {
  original_id: string;
  file: File;
}

// Contract interface for authorized contracts
export interface Contract {
  original_id: string;
  title?: string;
  name?: string;
  file_id?: string;
  contract_type?: string;
  description?: string;
  date?: string;
  status?: string;
}

// Adding DocumentEdge interface that was missing
export interface DocumentEdge {
  id: string;
  original_id?: string;
  target_id?: string;
  name?: string;
  label: string;
}

export interface Event {
  original_id: string;
  title: string;
  text: string;
  date: string | null;
  label: JuridicCategory;
  type: EventType;
  page_index: number;
  pvag: PVAGModel;
  file?: {
    original_id: string;
    company: {
      name: string;
      original_id: string;
    };
  };
  // Add the relatedDocuments property that was missing
  relatedDocuments?: DocumentEdge[];
}

export interface User {
  original_id: string;
  email: string;
  account: {
    original_id: string;
    name: string;
  };
}

export interface AccessLevel {
  user_original_id: string;
  company_original_id: string;
  access_level: string;
}

export interface FileInformation {
  title?: string | null;
  company_name?: string | null;
  siren?: string | null;
}

// API response types
export interface EventsResponse {
  events: Event[];
  categories: string[];
}

export interface Account {
  original_id: string;
  name: string;
}

export interface AccountInput {
  name: string;
}

export interface CompanyInput {
  name: string;
  siren: string;
}

export interface CompanyUpdate {
  name: string;
  siren: string;
}

export interface UserInput {
  email: string;
  password: string;
  invitation_token?: string | null;
}
