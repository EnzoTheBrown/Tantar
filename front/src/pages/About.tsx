
import { PublicLayout } from "@/components/PublicLayout";

const About = () => {
  return (
    <PublicLayout>
      <div className="container mx-auto px-6">
        <h1 className="text-4xl font-bold mb-8 text-center">À propos de <span className="text-blue-400">Tantar</span></h1>
        
        <div className="max-w-4xl mx-auto mb-16">
          <p className="text-lg mb-8 text-center">
            <span className="text-blue-400">Tantar</span> a été conçu pour révolutionner la manière dont les professionnels 
            juridiques accèdent à l'historique complet des sociétés. Notre technologie 
            innovante simplifie la recherche d'informations complexes et facilite la prise de décision.
          </p>
          
          <h2 className="text-3xl font-bold mb-8 text-center mt-20">Notre Mission</h2>
          <p className="text-lg mb-16 max-w-3xl mx-auto">
            Nous nous engageons à fournir une solution complète et intuitive pour optimiser le temps et les 
            ressources des cabinets d'avocats, des experts-comptables et des directions juridiques. Notre 
            mission est de transformer la gestion des informations critiques en un processus simple, rapide et sécurisé.
          </p>
          
        </div>
        
        <h2 className="text-3xl font-bold mb-16 text-center mt-20">Notre Équipe</h2>
        <div className="flex justify-center max-w-4xl mx-auto mb-16">
          <div className="text-center">
            <div className="mb-6 mx-auto">
              <img 
                src="/lovable-uploads/39dcee91-7864-4ce5-b23f-cfc9d0138153.png" 
                alt="Enzo Lebrun" 
                className="rounded-full h-48 w-48 object-cover object-center border-4 border-blue-900 mx-auto"
              />
            </div>
            <h3 className="text-xl font-bold mb-1">Enzo Lebrun</h3>
            <p className="text-gray-300">CEO & Founder</p>
          </div>
        </div>
        
        <div className="max-w-4xl mx-auto mt-20">
          <h2 className="text-3xl font-bold mb-8 text-center">Pourquoi Nous Choisir ?</h2>
          <p className="text-lg text-center mb-16">
            Avec <span className="text-blue-400">Tantar</span>, bénéficiez d'une solution complète qui combine sécurité, efficacité et innovation. 
            Nos fonctionnalités avancées et notre engagement envers la confidentialité vous permettent d'accéder rapidement à 
            l'historique de vos sociétés pour une prise de décision éclairée.
          </p>
        </div>
      </div>
    </PublicLayout>
  );
};

export default About;
