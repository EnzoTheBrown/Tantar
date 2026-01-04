
import { 
  Info, Pencil, Wallet, Calendar, Briefcase, 
  Users, CheckCircle, User, Settings, Tag,
  Share, RefreshCw, X, HelpCircle, CircleDollarSign
} from "lucide-react";

export const timelineIconMapping = {
  "Caractéristiques de la société": Info,
  "Modifications statutaires": Pencil,
  "Capital": CircleDollarSign,
  "Capitaux propres": Wallet,
  "Comptes annuels": Calendar,
  "Fonds de commerce": Briefcase,
  "Associés": Users,
  "Autorisations diverses": CheckCircle,
  "Dirigeants": User,
  "Contrôle de la société": Settings,
  "Titres": Tag,
  "Distributions": Share,
  "Restructuration": RefreshCw,
  "Dissolution": X,
  "Autre": HelpCircle,
};
