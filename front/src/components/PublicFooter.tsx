
import { Link } from "react-router-dom";
import { Linkedin, Instagram, Twitter } from "lucide-react";

export const PublicFooter = () => {
  return (
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
  );
};
