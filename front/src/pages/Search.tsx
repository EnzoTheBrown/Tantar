
import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { useQuery } from '@tanstack/react-query';
import { Search as SearchIcon, AlertCircle, Home } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import * as api from '../api';
import type { Event } from '@/types/api';
import { FileViewDialog } from '../components/FileViewDialog';
import { EventList } from '../components/EventList';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  Breadcrumb, 
  BreadcrumbList, 
  BreadcrumbItem, 
  BreadcrumbLink, 
  BreadcrumbSeparator, 
  BreadcrumbPage 
} from '@/components/ui/breadcrumb';
import { Link } from 'react-router-dom';
import { FileSpreadsheet } from 'lucide-react';
import { exportEventsToExcel } from '@/utils/excelExport';

export const Search = () => {
  const [query, setQuery] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState<{ id: string; pageIndex: number } | null>(null);

  const { data: eventsData, isLoading: eventsLoading, isError: eventsError, refetch } = useQuery({
    queryKey: ['events', searchQuery],
    queryFn: () => api.getEvents({ question: searchQuery }),
    enabled: !!searchQuery.trim(),
  });

  // Initial load with default search
  useEffect(() => {
    const initialSearch = async () => {
      const defaultQuery = 'Tous les événements';
      setQuery(defaultQuery);
      setSearchQuery(defaultQuery);
    };
    initialSearch();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setSearchQuery(query);
    }
  };

  const handleEventClick = (event: Event) => {
    if (event.pvag && event.pvag.file && event.pvag.file.original_id) {
      setSelectedFile({
        id: event.pvag.file.original_id,
        pageIndex: event.page_index
      });
    }
  };

  const handleDialogClose = (open: boolean) => {
    if (!open) {
      setSelectedFile(null);
    }
  };

  const handleExport = () => {
    if (eventsData?.events) {
      exportEventsToExcel(eventsData.events, 'recherche-evenements');
    }
  };

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
              <BreadcrumbPage>Recherche</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="flex items-center justify-between gap-2 mb-6">
          <div className="flex items-center gap-2">
            <SearchIcon className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-semibold">Recherche d'événements</h1>
          </div>
          {eventsData?.events && eventsData.events.length > 0 && (
            <Button onClick={handleExport} variant="outline">
              <FileSpreadsheet className="h-4 w-4 mr-2" />
              Exporter en Excel
            </Button>
          )}
        </div>

        <form onSubmit={handleSearch} className="max-w-3xl mx-auto mb-8">
          <div className="flex gap-2">
            <Input
              placeholder="Recherchez des événements..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1"
            />
            <Button type="submit">
              <SearchIcon className="h-4 w-4 mr-2" />
              Rechercher
            </Button>
          </div>
        </form>

        {eventsLoading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-gray-500">Chargement des résultats...</p>
          </div>
        )}

        {eventsError && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erreur</AlertTitle>
            <AlertDescription>
              Une erreur est survenue lors de la recherche. Veuillez réessayer plus tard.
            </AlertDescription>
          </Alert>
        )}

        {eventsData?.events && eventsData.events.length > 0 && (
          <div className="max-w-3xl mx-auto">
            <EventList 
              events={eventsData.events} 
              onEventClick={handleEventClick} 
            />
          </div>
        )}

        {eventsData?.events && eventsData.events.length === 0 && (
          <div className="flex flex-col items-center justify-center h-60 bg-gray-50 rounded-lg border border-dashed border-gray-300 p-6">
            <p className="text-gray-500 mb-2">Aucun résultat trouvé</p>
            <p className="text-sm text-gray-400">Essayez avec d'autres termes de recherche</p>
          </div>
        )}

        {selectedFile && (
          <FileViewDialog 
            open={Boolean(selectedFile)} 
            onOpenChange={handleDialogClose} 
            fileId={selectedFile.id}
            pageIndex={selectedFile.pageIndex}
          />
        )}
      </main>
    </div>
  );
};

export default Search;
