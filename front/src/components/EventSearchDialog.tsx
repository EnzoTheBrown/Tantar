
import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Search, Info, Pencil, DollarSign, Wallet, Calendar, Briefcase, Users, CheckCircle, User, Cog, Tag, Share2, RefreshCw, X, HelpCircle } from 'lucide-react';
import * as api from '../api';
import { Input } from './ui/input';
import { Button } from './ui/button';
import type { Event } from '@/types/api';

// Map the old icon names to Lucide React icons
const iconMapping = {
  "Caractéristiques de la société": Info,
  "Modifications statutaires": Pencil,
  "Capital": DollarSign,
  "Capitaux propres": Wallet,
  "Comptes annuels": Calendar,
  "Fonds de commerce": Briefcase,
  "Associés": Users,
  "Autorisations diverses": CheckCircle,
  "Dirigeants": User,
  "Contrôle de la société": Cog,
  "Titres": Tag,
  "Distributions": Share2,
  "Restructuration": RefreshCw,
  "Dissolution": X,
  "Autre": HelpCircle,
};

interface EventSearchDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialQuery?: string;
}

export const EventSearchDialog: React.FC<EventSearchDialogProps> = ({ 
  open, 
  onOpenChange, 
  initialQuery = '' 
}) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [query, setQuery] = useState(initialQuery);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (open) {
      setQuery(initialQuery);
      // Don't auto-search when opening
    }
  }, [open, initialQuery]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await api.getEvents({
        question: query
      });
      setEvents(response.events);
      setCategories(response.categories);
    } catch (error) {
      console.error('Error searching events:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Recherche d'événements</DialogTitle>
          <DialogDescription>
            Entrez votre requête et cliquez sur Rechercher pour trouver des événements.
          </DialogDescription>
        </DialogHeader>
        <div className="flex items-center space-x-2 mb-4">
          <Input
            placeholder="Recherchez des événements..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-grow"
          />
          <Button 
            onClick={handleSearch}
            disabled={isLoading} 
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Search className="h-5 w-5 mr-2" />
            )}
            Rechercher
          </Button>
        </div>
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="flex justify-center items-center py-10">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : events.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Dénomination sociale</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Catégories</TableHead>
                  <TableHead>Titre</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Texte</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {events.map((event, index) => {
                  const IconComponent = iconMapping[event.label as keyof typeof iconMapping] || iconMapping["Autre"];
                  const companyName = event.pvag?.file?.company?.name || 'N/A';
                  
                  return (
                    <TableRow key={index}>
                      <TableCell>{companyName}</TableCell>
                      <TableCell>{event.date ? new Date(event.date).toLocaleDateString() : 'N/A'}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <IconComponent className="h-4 w-4 text-blue-500" />
                          {event.label}
                        </div>
                      </TableCell>
                      <TableCell>{event.title}</TableCell>
                      <TableCell>{event.type}</TableCell>
                      <TableCell>{event.text}</TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-10 text-gray-500">
              {query.trim() ? "Aucun résultat trouvé" : "Veuillez effectuer une recherche"}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};
