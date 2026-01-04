
import { PublicLayout } from "@/components/PublicLayout";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const FAQ = () => {
  const faqs = [
    {
      question: "Qu'est-ce que Tantar ?",
      answer: "Tantar est une plateforme innovante qui permet aux cabinets d'avocats, aux experts-comptables et aux directions juridiques d'accéder à l'historique complet de leurs sociétés en un seul clic, afin d'optimiser leur temps et réduire les coûts."
    },
    {
      question: "Comment fonctionne Tantar ?",
      answer: "Tantar importe vos documents et exploite des fonctionnalités telles que la recherche intradocumentaire en temps réel, l'identification automatique des bénéficiaires effectifs, ainsi qu'une datavisualisation interactive pour offrir une vue globale des décisions sociales."
    },
    {
      question: "Quelles sont les fonctionnalités clés ?",
      answer: "La plateforme inclut la recherche en temps réel, l'identification des bénéficiaires, la frise chronologique interactive, le traçage des informations, des filtres intelligents et l'exportation des résultats dans un environnement hautement sécurisé."
    },
    {
      question: "Comment la confidentialité et la sécurité sont-elles assurées ?",
      answer: "La sécurité et la confidentialité sont au cœur de notre engagement. Tantar utilise des protocoles de sécurité avancés pour protéger vos données et garantir un traitement confidentiel de vos informations."
    },
    {
      question: "À qui s'adresse Tantar ?",
      answer: "La solution s'adresse aux cabinets d'avocats, aux experts-comptables ainsi qu'aux directions juridiques qui souhaitent optimiser leurs recherches d'informations et la gestion de leurs portefeuilles de sociétés."
    },
    {
      question: "Comment puis-je contacter Tantar pour plus d'informations ?",
      answer: "Pour toute question ou demande d'information complémentaire, vous pouvez nous contacter via notre page Contact ou envoyer un email à notre service support."
    }
  ];

  return (
    <PublicLayout>
      <div className="container mx-auto px-6">
        <h1 className="text-4xl font-bold mb-8 text-center">FAQ</h1>
        <p className="text-lg text-center mb-12 max-w-3xl mx-auto">
          Vous trouverez ci-dessous les réponses aux questions les plus fréquentes concernant Tantar.
        </p>
        
        <div className="max-w-3xl mx-auto">
          <Accordion type="single" collapsible className="w-full">
            {faqs.map((faq, index) => (
              <AccordionItem key={index} value={`item-${index}`} className="border-b border-blue-800">
                <AccordionTrigger className="text-lg font-medium text-white py-4">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-gray-300 pb-4">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
        
        <div className="text-center mt-16">
          <p className="text-lg mb-4">Vous avez d'autres questions ?</p>
          <Link to="/contact">
            <Button className="bg-blue-600 hover:bg-blue-700">Contactez-nous</Button>
          </Link>
        </div>
      </div>
    </PublicLayout>
  );
};

export default FAQ;
