
import { PublicLayout } from "@/components/PublicLayout";
import { Link } from "react-router-dom";

const Legal = () => {
  return (
    <PublicLayout>
      <div className="container mx-auto px-4 md:px-6">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-10 text-center">Mentions légales</h1>
          
          <div className="space-y-6">
            <p className="leading-relaxed">
              Ce site est édité par Tantar, société par actions simplifiée au capital de 2 000 euros, ayant son siège social 11 rue des Frères Lumière 92500 Rueil-Malmaison, immatriculée au Registre du Commerce et des Sociétés de Nanterre sous le numéro 940 018 740.
            </p>
            
            <p className="leading-relaxed">N° TVA Intracommunautaire : FR64940018740</p>
            
            <p className="leading-relaxed">
              Le directeur de la publication est Enzo Lebrun, Président de la société Tantar.
            </p>
            
            <p className="leading-relaxed">
              Email : <a href="mailto:enzo@tantar.ai" className="text-blue-300 hover:underline">enzo@tantar.ai</a>
            </p>
            
            <p className="leading-relaxed">
              Ce site est hébergé par AWS, le serveur est géographiquement localisé à Paris (France).
            </p>
            
            <p className="leading-relaxed">
              L'ensemble de ce site relève de la législation française et internationale sur le droit d'auteur et la propriété intellectuelle. Tous les droits de reproduction sont réservés, y compris pour les documents téléchargeables et les représentations iconographiques et photographiques. Les visuels d'illustration de ce site sont propriété de l'Éditeur. Les droits d'utilisation, de reproduction et de diffusion sont strictement réservés à la communication de l'Éditeur. La reproduction de tout ou partie de ce site sur un support électronique ou papier quel qu'il soit est formellement interdite sauf autorisation expresse du responsable du site. Pour d'autres utilisations, veuillez contacter le responsable du site. Les marques citées sur ce site sont déposées par les sociétés qui en sont propriétaires.
            </p>
          </div>
        </div>
      </div>
    </PublicLayout>
  );
};

export default Legal;
