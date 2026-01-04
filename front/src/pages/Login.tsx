
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import * as api from '@/api';
import { PublicLayout } from '@/components/PublicLayout';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast({
        title: "Erreur",
        description: "Veuillez remplir tous les champs",
        variant: "destructive",
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      const response = await api.login(email, password);
      
      // The API returns the response directly, not nested in a 'data' property
      if (response && response.access_token) {
        login(response.access_token);
        toast({
          title: "Succès",
          description: "Vous êtes connecté",
        });
        navigate('/dashboard');
      } else {
        throw new Error("Token not found in response");
      }
    } catch (error) {
      console.error("Login error:", error);
      toast({
        title: "Erreur",
        description: "Email ou mot de passe incorrect",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PublicLayout>
      <div className="w-full max-w-md p-6 mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-center">Connexion</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full"
              disabled={isLoading}
            />
          </div>
          
          <div>
            <Input
              type="password"
              placeholder="Mot de passe"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full"
              disabled={isLoading}
            />
          </div>
          
          <Button 
            type="submit" 
            className="w-full bg-blue-500 hover:bg-blue-600"
            disabled={isLoading}
          >
            {isLoading ? "Connexion en cours..." : "Connexion"}
          </Button>
        </form>
        
        <div className="mt-4 text-center">
          <span className="text-gray-300">Vous n'avez pas de compte ?</span>{" "}
          <Link to="/register" className="text-blue-400 hover:text-blue-300">
            Créer un compte
          </Link>
        </div>
      </div>
    </PublicLayout>
  );
};

export default Login;
