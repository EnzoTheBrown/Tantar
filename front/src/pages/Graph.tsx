
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

export const Graph = () => {
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
              <BreadcrumbPage>Graphe de relations</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="flex items-center gap-2 mb-6">
          <Network className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-semibold">Graphe de relations</h1>
        </div>

        <div className="grid place-items-center py-12">
          <div className="w-full max-w-3xl">
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-100">
              <h2 className="text-xl font-medium mb-4">Visualisation des relations</h2>
              <p className="text-gray-600 mb-4">
                Ce module vous permettra de visualiser les relations entre différentes entités.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Graph;
