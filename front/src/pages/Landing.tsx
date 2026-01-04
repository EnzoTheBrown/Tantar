
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight, Check, Clock, ShieldCheck, Users, Search, Calendar, Network, FileText, Filter } from "lucide-react";
import { PublicLayout } from "@/components/PublicLayout";

const Landing = () => {
  const features = [
    {
      title: "Recherche intradocumentaire en temps réel",
      icon: <Search className="w-6 h-6 text-white" />
    },
    {
      title: "Identification automatique des bénéficiaires effectifs",
      icon: <Users className="w-6 h-6 text-white" />
    },
    {
      title: "Datavisualisation via une frise chronologique interactive",
      icon: <Calendar className="w-6 h-6 text-white" />
    },
    {
      title: "Lien entre les parties prenantes et les décisions",
      icon: <Network className="w-6 h-6 text-white" />
    },
    {
      title: "Traçabilité et accès rapide à la source",
      icon: <FileText className="w-6 h-6 text-white" />
    },
    {
      title: "Export des résultats",
      icon: <FileText className="w-6 h-6 text-white" />
    },
    {
      title: "Filtres intelligents",
      icon: <Filter className="w-6 h-6 text-white" />
    },
    {
      title: "Sécurité et confidentialité",
      icon: <ShieldCheck className="w-6 h-6 text-white" />
    }
  ];

  const advantages = [
    {
      title: "Gain de temps et d'efficacité",
      description: "Suppression des recherches manuelles fastidieuses, structuration et filtrage par thématique."
    },
    {
      title: "Collaboration simplifiée",
      description: "Centralisation des données, continuité assurée même en cas d'absence."
    },
    {
      title: "Gestion proactive",
      description: "Alertes automatiques, suivi des échéances et mandats."
    }
  ];

  const visionPoints = [
    "Sécuriser vos opérations juridiques et fiscales",
    "Gagner du temps dans les vérifications",
    "Comprendre la logique et la stratégie de la société"
  ];

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-[#000033] to-[#0000cc] text-white">
      {/* Custom header for the landing page */}
      <header className="py-4 px-6">
        <div className="container mx-auto flex justify-between items-center">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-3xl font-bold text-blue-400">Tantar</span>
          </Link>
          
          <div className="flex items-center space-x-4">
            <Link to="/login">
              <Button variant="ghost" className="text-white hover:text-white hover:bg-blue-800">
                Connexion
              </Button>
            </Link>
            <Link to="/contact">
              <Button className="bg-blue-600 hover:bg-blue-700">
                Demander une démo
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 md:py-28 relative">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-8">
              L'historique complet de votre société en un seul clic.
            </h1>
            <p className="text-lg md:text-xl mb-8 text-gray-200">
              Avec Tantar, les cabinets d'avocats, d'expertise-comptable et les directions juridiques 
              optimisent leur temps et réduisent les coûts liés à la recherche d'informations sur les sociétés de 
              leur portefeuille.
            </p>
            <Link to="/features">
              <Button size="lg" className="bg-blue-500 hover:bg-blue-600">
                Découvrir
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Vision Section */}
      <section className="py-16">
        <div className="container mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-6">
              Une vision globale et complète de votre portefeuille de sociétés.
            </h2>
            <p className="text-lg mb-12 text-gray-200">
              Ne perdez plus de temps à fouiller dans des procès verbaux...
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold mb-16 text-center">Fonctionnalités</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {features.map((feature, index) => (
              <div key={index} className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  {feature.icon}
                </div>
                <p className="text-lg">{feature.title}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Import Documents */}
      <section className="py-16">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-2xl font-bold">Vous importez vos documents, Tantar se charge du reste.</h2>
        </div>
      </section>

      {/* Advantages */}
      <section className="py-16">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold mb-12 text-center">Les avantages pour vous</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {advantages.map((advantage, index) => (
              <div key={index} className="text-center p-6">
                <h3 className="text-xl font-bold mb-3">{advantage.title}</h3>
                <p>{advantage.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Vision */}
      <section className="py-16">
        <div className="container mx-auto px-6 max-w-4xl text-center">
          <h2 className="text-3xl font-bold mb-8">Nous allons plus loin, avoir une vision globale des décisions sociales c'est :</h2>
          <ul className="text-lg space-y-4">
            {visionPoints.map((point, index) => (
              <li key={index} className="flex items-center justify-center">
                <Check className="text-blue-400 mr-2" />
                <span>{point}</span>
              </li>
            ))}
          </ul>
          <p className="mt-12 text-lg">
            Et bien entendu, la confidentialité et la sécurité sont au cœur de notre engagement.
          </p>
          
          <div className="mt-12">
            <Link to="/contact">
              <Button size="lg" className="bg-blue-500 hover:bg-blue-600">
                Contactez-nous
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer from shared component */}
      <footer className="py-12 border-t border-blue-900">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4 text-blue-400">Tantar</h3>
              <p className="mb-4">© 2025 Tantar - Tous droits réservés.</p>
              <p>Votre partenaire pour accéder à l'historique complet des sociétés.</p>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-4">Liens utiles</h3>
              <ul className="space-y-2">
                <li><Link to="/features" className="hover:text-blue-400">Fonctionnalités</Link></li>
                <li><Link to="/about" className="hover:text-blue-400">À propos</Link></li>
                <li><Link to="/contact" className="hover:text-blue-400">Contact</Link></li>
                <li><Link to="/legal" className="hover:text-blue-400">Mentions légales</Link></li>
                <li><Link to="/faq" className="hover:text-blue-400">FAQ</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-4">Réseaux sociaux</h3>
              <ul className="space-y-2">
                <li>
                  <a href="https://www.linkedin.com/in/tantar-ai-4a349930a/" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 flex items-center">
                    <span className="mr-2">LinkedIn</span>
                  </a>
                </li>
                <li>
                  <a href="https://www.instagram.com/tantar.ai/" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 flex items-center">
                    <span className="mr-2">Instagram</span>
                  </a>
                </li>
                <li>
                  <a href="https://twitter.com/tantar_ai" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 flex items-center">
                    <span className="mr-2">Twitter</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
