
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";

export const PublicHeader = () => {
  const location = useLocation();

  return (
    <header className="py-4 px-6">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="flex items-center space-x-2">
          <span className="text-3xl font-bold text-blue-400">Tantar</span>
        </Link>
        
        <div className="flex items-center space-x-4">
          {location.pathname !== "/login" && (
            <Link to="/login">
              <Button variant="ghost" className="text-white hover:text-white hover:bg-blue-800">
                Connexion
              </Button>
            </Link>
          )}
          
          {location.pathname !== "/register" && (
            <Link to="/register">
              <Button className="bg-blue-600 hover:bg-blue-700">
                {location.pathname === "/login" ? "Créer un compte" : "S'inscrire"}
              </Button>
            </Link>
          )}
          
          {!["/login", "/register"].includes(location.pathname) && (
            <Link to="/contact">
              <Button variant="outline" className="border-blue-400 text-blue-400 hover:bg-blue-900">
                Demander une démo
              </Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
