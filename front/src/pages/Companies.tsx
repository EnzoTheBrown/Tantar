
import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { CompaniesTable } from '@/components/CompaniesTable';
import { Loader2, Building2 } from 'lucide-react';
import { toast } from 'sonner';
import * as api from '@/api';
import type { Company } from '@/types/api';
import { 
  Breadcrumb, 
  BreadcrumbList, 
  BreadcrumbItem, 
  BreadcrumbLink, 
  BreadcrumbSeparator, 
  BreadcrumbPage 
} from '@/components/ui/breadcrumb';
import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';
import { Card } from "@/components/ui/card";
import { useNavigate } from 'react-router-dom';

const Companies = () => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const companiesRes = await api.getCompanies();
        setCompanies(companiesRes);
      } catch (error) {
        console.error('Error fetching data:', error);
        toast.error("Erreur lors du chargement des données");
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleCompanyClick = (companyId: string) => {
    navigate(`/timeline/${companyId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        <p className="mt-4 text-gray-600">Chargement des sociétés...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Header />
      <main className="container mx-auto px-4 py-6">
        <Breadcrumb className="mb-6">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink asChild>
                <Link to="/dashboard" className="flex items-center">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Toutes les sociétés</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="flex items-center justify-between gap-2 mb-6">
          <div className="flex items-center gap-2">
            <Building2 className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-semibold">Toutes les sociétés</h1>
          </div>
        </div>

        <div className="mt-4">
          {companies.length > 0 ? (
            <Card className="shadow-sm">
              <CompaniesTable 
                companies={companies} 
                onCompanyClick={handleCompanyClick}
              />
            </Card>
          ) : (
            <Card className="py-12 text-center">
              <p className="text-gray-500">Aucune société trouvée</p>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

export default Companies;
