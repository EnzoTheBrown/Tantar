
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PublicLayout } from "@/components/PublicLayout";
import { Search, Calendar, Shield, Users, FileText, Network, Filter } from "lucide-react";
import { Link } from "react-router-dom";

const Features = () => {
  const features = [
    {
      title: "Recherche intradocumentaire en temps réel",
      description: "Trouvez instantanément l'information dont vous avez besoin dans l'ensemble de vos documents.",
      icon: <Search className="h-12 w-12 text-blue-400" />
    },
    {
      title: "Identification automatique des bénéficiaires effectifs",
      description: "Notre technologie identifie automatiquement les bénéficiaires effectifs de vos sociétés.",
      icon: <Users className="h-12 w-12 text-blue-400" />
    },
    {
      title: "Datavisualisation via une frise chronologique interactive",
      description: "Visualisez l'évolution de vos sociétés à travers une frise chronologique intuitive et interactive.",
      icon: <Calendar className="h-12 w-12 text-blue-400" />
    },
    {
      title: "Lien entre les parties prenantes et les décisions",
      description: "Comprenez les liens entre les différentes parties prenantes et les décisions prises au sein de la société.",
      icon: <Network className="h-12 w-12 text-blue-400" />
    },
    {
      title: "Traçabilité et accès rapide à la source",
      description: "Accédez rapidement aux documents sources pour vérifier l'information à tout moment.",
      icon: <FileText className="h-12 w-12 text-blue-400" />
    },
    {
      title: "Export des résultats",
      description: "Exportez facilement vos recherches et résultats dans différents formats pour les partager avec vos équipes.",
      icon: <FileText className="h-12 w-12 text-blue-400" />
    },
    {
      title: "Filtres intelligents",
      description: "Utilisez nos filtres intelligents pour affiner vos recherches et trouver exactement ce que vous cherchez.",
      icon: <Filter className="h-12 w-12 text-blue-400" />
    },
    {
      title: "Sécurité et confidentialité",
      description: "Vos données sont protégées par les plus hauts standards de sécurité et de confidentialité.",
      icon: <Shield className="h-12 w-12 text-blue-400" />
    }
  ];

  return (
    <PublicLayout>
      <div className="container mx-auto px-6">
        <h1 className="text-4xl font-bold mb-8 text-center">Fonctionnalités</h1>
        <p className="text-lg text-center mb-12 max-w-3xl mx-auto">
          Découvrez les fonctionnalités avancées de Tantar qui transforment la recherche d'informations sur vos sociétés en une expérience simple et efficace.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="bg-blue-900/30 border border-blue-800 hover:bg-blue-900/50 transition-all">
              <CardContent className="p-6">
                <div className="flex justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-2 text-center">{feature.title}</h3>
                <p className="text-gray-300 text-center">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <div className="mt-16 text-center p-10 bg-blue-900/30 border border-blue-800 rounded-lg">
          <h2 className="text-2xl font-bold mb-6">Vous importez vos documents, Tantar se charge du reste.</h2>
          <p className="text-lg mb-8 max-w-3xl mx-auto">
            Notre plateforme est conçue pour s'adapter à vos besoins et vous permettre de gagner un temps précieux dans la gestion de vos informations.
          </p>
          <Link to="/contact">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700">Contactez-nous pour une démonstration</Button>
          </Link>
        </div>
      </div>
    </PublicLayout>
  );
};

export default Features;
