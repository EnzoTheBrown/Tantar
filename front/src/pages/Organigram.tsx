
import React from 'react';
import { Header } from '../components/Header';
import { Network, Home } from 'lucide-react';
import { 
  Breadcrumb, 
  BreadcrumbList, 
  BreadcrumbItem, 
  BreadcrumbLink, 
  BreadcrumbSeparator, 
  BreadcrumbPage 
} from '@/components/ui/breadcrumb';
import { Link } from 'react-router-dom';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export const Organigram = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Breadcrumb className="mb-6">
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink asChild>
                <Link to="/" className="flex items-center">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Organigramme</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="flex items-center gap-2 mb-6">
          <Network className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-semibold">Organigramme de l'entreprise</h1>
        </div>

        <Alert className="my-8">
          <AlertTitle>En cours de développement</AlertTitle>
          <AlertDescription>
            La fonctionnalité d'organigramme est en cours de développement.
          </AlertDescription>
        </Alert>
      </main>
    </div>
  );
};

export default Organigram;
