import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Header } from '../components/Header';
import { Clock, AlertCircle, Home } from 'lucide-react';
import * as api from '../api';
import type { Event } from '@/types/api';
import { FileViewDialog } from '../components/FileViewDialog';
import { TimelineFilters, TimelineFilters as TimelineFiltersType } from '../components/TimelineFilters';
import { EnhancedTimelineView } from '../components/EnhancedTimelineView';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  Breadcrumb, 
  BreadcrumbList, 
  BreadcrumbItem, 
  BreadcrumbLink, 
  BreadcrumbSeparator, 
  BreadcrumbPage 
} from '@/components/ui/breadcrumb';
import { Button } from '@/components/ui/button';
import { FileSpreadsheet } from 'lucide-react';
import { exportEventsToExcel } from '@/utils/excelExport';
import { useToast } from '@/hooks/use-toast';

export const Timeline: React.FC = () => {
  const { companyId } = useParams<{ companyId: string }>();
  const [selectedFile, setSelectedFile] = useState<{ id: string; pageIndex: number } | null>(null);
  const [filters, setFilters] = useState<TimelineFiltersType>({});
  const { toast } = useToast();
  
  const { data: eventsData, isLoading, isError } = useQuery({
    queryKey: ['events', companyId, filters],
    queryFn: () => api.getEvents({
      company_id: companyId,
      start_date: filters.startDate,
      end_date: filters.endDate,
      label: filters.label === 'all' ? undefined : filters.label,
      question: filters.question,
      k: filters.k
    }),
  });

  const handleFilterChange = (newFilters: TimelineFiltersType) => {
    setFilters(newFilters);
  };

  const handleEventClick = (event: Event) => {
    // Updated to use the correct property path: pvag.file.original_id
    if (event.pvag && event.pvag.file && event.pvag.file.original_id) {
      setSelectedFile({
        id: event.pvag.file.original_id,
        pageIndex: event.page_index
      });
    } else {
      toast({
        title: "Information",
        description: "Aucun document associé à cet événement.",
        variant: "default"
      });
    }
  };

  const handleDialogClose = (open: boolean) => {
    if (!open) {
      setSelectedFile(null);
    }
  };

  const handleExport = () => {
    if (events) {
      exportEventsToExcel(events, 'timeline-evenements');
      toast({
        title: "Succès",
        description: "Les événements ont été exportés avec succès.",
        variant: "default"
      });
    }
  };

  const events = eventsData?.events || [];
  const categories = eventsData?.categories || [];

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
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
              <BreadcrumbPage>Timeline</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="flex items-center justify-between gap-2 mb-6">
          <div className="flex items-center gap-2">
            <Clock className="h-6 w-6 text-blue-600" />
            <h1 className="text-2xl font-semibold">Timeline des événements</h1>
          </div>
          {events.length > 0 && (
            <Button onClick={handleExport} variant="outline">
              <FileSpreadsheet className="h-4 w-4 mr-2" />
              Exporter en Excel
            </Button>
          )}
        </div>

        <TimelineFilters 
          categories={categories}
          onFilterChange={handleFilterChange}
        />

        {isLoading && (
          <div className="flex justify-center items-center py-20">
            <div className="flex flex-col items-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
              <p className="text-gray-500">Chargement des événements...</p>
            </div>
          </div>
        )}

        {isError && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erreur</AlertTitle>
            <AlertDescription>
              Une erreur est survenue lors du chargement des événements. Veuillez réessayer plus tard.
            </AlertDescription>
          </Alert>
        )}
        
        {filters.question && !isLoading && !isError && (
          <Alert className="mb-6 bg-blue-50 border-blue-200">
            <AlertTitle className="text-blue-800">Recherche par question</AlertTitle>
            <AlertDescription className="text-blue-700">
              Affichage des résultats pour la question: "{filters.question}"
            </AlertDescription>
          </Alert>
        )}
        
        {!isLoading && !isError && (
          <EnhancedTimelineView events={events} onEventClick={handleEventClick} />
        )}
      </main>

      {selectedFile && (
        <FileViewDialog 
          open={Boolean(selectedFile)} 
          onOpenChange={handleDialogClose} 
          fileId={selectedFile.id}
          pageIndex={selectedFile.pageIndex}
        />
      )}
    </div>
  );
};

export default Timeline;
