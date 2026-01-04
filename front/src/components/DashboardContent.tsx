
import React from 'react';
import { Link } from 'react-router-dom';
import { CompaniesTable } from './CompaniesTable';
import { FilesList } from './FilesList';
import { SearchBar } from './SearchBar';
import { FileUploader } from './FileUploader';
import { Building2, FileText, PlusCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import type { Company, File } from '@/types/api';

interface DashboardContentProps {
  companies: Company[];
  recentFiles: File[];
  addedFiles: File[];
  onCompanyClick: (companyId: string) => void;
  onFilesUpdated: (files: File[]) => void;
}

export const DashboardContent = ({
  companies,
  recentFiles,
  addedFiles,
  onCompanyClick,
  onFilesUpdated
}: DashboardContentProps) => {
  // Only display the first 4 companies for a more condensed view
  const displayedCompanies = companies.slice(0, 4);
  
  return (
    <main className="container mx-auto px-4 py-4">
      <div className="max-w-3xl mx-auto mb-4">
        <Link to="/search">
          <SearchBar />
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2 space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-blue-600" />
                  <CardTitle className="text-lg">Mon portefeuille</CardTitle>
                </div>
                <Link to="/companies">
                  <Button variant="ghost" size="sm" className="text-xs h-8">
                    Voir tout
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent className="pt-0 pb-2">
              <CompaniesTable 
                companies={displayedCompanies} 
                onCompanyClick={onCompanyClick}
              />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <PlusCircle className="h-5 w-5 text-green-600" />
                  <CardTitle className="text-lg">Ajouter des fichiers</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0 pb-2">
              <FileUploader onFilesUpdated={onFilesUpdated} />
            </CardContent>
          </Card>
        </div>
        
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  <CardTitle className="text-lg">Documents récents</CardTitle>
                </div>
                <Link to="/files">
                  <Button variant="ghost" size="sm" className="text-xs h-8">
                    Voir tout
                  </Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent className="pt-0 pb-2">
              <FilesList 
                files={recentFiles}
                title="Documents consultés"
                compact={true}
              />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-green-600" />
                  <CardTitle className="text-lg">Ajouts récents</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0 pb-2">
              <FilesList 
                title="Documents ajoutés"
                files={addedFiles}
                compact={true}
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
};
