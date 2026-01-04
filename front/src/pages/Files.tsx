import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FilesList } from '@/components/FilesList';
import { FileFilters } from '@/components/FileFilters';
import { FileViewDialog } from '@/components/FileViewDialog';
import { Loader2, FileText, Eye } from 'lucide-react';
import { toast } from 'sonner';
import * as api from '@/api';
import type { File, Company } from '@/types/api';
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
import { Card, CardContent } from "@/components/ui/card";

const Files = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    type: 'all_types',
    companyId: 'all_companies'
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [filesRes, companiesRes] = await Promise.all([
          api.getFiles(),
          api.getCompanies()
        ]);
        
        setFiles(filesRes);
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

  const handleFilterChange = (filterType: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const filteredFiles = files.filter(file => {
    const typeMatch = filters.type === 'all_types' || file.type === filters.type;
    const companyMatch = filters.companyId === 'all_companies' || (file.company && file.company.original_id === filters.companyId);
    
    return typeMatch && companyMatch;
  });

  // Get unique file types for filter options
  const fileTypes = Array.from(new Set(files.map(file => file.type).filter(Boolean)));

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        <p className="mt-4 text-gray-600">Chargement des fichiers...</p>
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
              <BreadcrumbPage>Tous les fichiers</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="flex items-center justify-between gap-2 mb-6">
          <div className="flex items-center gap-2">
            <FileText className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-semibold">Tous les fichiers</h1>
          </div>
        </div>

        <Card className="mb-6 shadow-sm">
          <CardContent className="p-4">
            <FileFilters 
              fileTypes={fileTypes}
              companies={companies}
              onFilterChange={handleFilterChange}
              selectedFilters={filters}
            />
          </CardContent>
        </Card>

        <div className="mt-4">
          {filteredFiles.length > 0 ? (
            <Card className="shadow-sm">
              <Table>
                <TableHeader>
                  <TableRow className="bg-gray-50">
                    <TableHead className="font-medium text-gray-700">Document</TableHead>
                    <TableHead className="font-medium text-gray-700">Société</TableHead>
                    <TableHead className="font-medium text-gray-700">Type</TableHead>
                    <TableHead className="w-[100px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredFiles.map((file) => (
                    <FileRow key={file.original_id} file={file} />
                  ))}
                </TableBody>
              </Table>
            </Card>
          ) : (
            <Card className="py-12 text-center">
              <p className="text-gray-500">Aucun fichier trouvé avec les filtres sélectionnés</p>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
};

// File row component with actions
const FileRow = ({ file }: { file: File }) => {
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);

  return (
    <>
      <TableRow key={file.original_id} className="hover:bg-gray-50">
        <TableCell className="font-medium">{file.name}</TableCell>
        <TableCell className="text-gray-600">{file.company?.name || 'N/A'}</TableCell>
        <TableCell>
          <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
            {file.type || 'N/A'}
          </span>
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-1">
            <button 
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-full"
              onClick={() => setSelectedFileId(file.original_id)}
              title="Voir le document"
            >
              <Eye className="h-4 w-4" />
            </button>
          </div>
        </TableCell>
      </TableRow>
      
      {selectedFileId && (
        <FileViewDialog 
          open={!!selectedFileId} 
          onOpenChange={() => setSelectedFileId(null)} 
          fileId={selectedFileId} 
        />
      )}
    </>
  );
};

export default Files;
