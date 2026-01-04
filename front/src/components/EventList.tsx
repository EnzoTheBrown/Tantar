
import React from 'react';
import { Event } from '@/types/api';
import { timelineIconMapping } from '@/utils/timelineIcons';
import { format } from 'date-fns';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Building2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { fr } from 'date-fns/locale';

interface EventListProps {
  events: Event[];
  onEventClick: (event: Event) => void;
}

export const EventList: React.FC<EventListProps> = ({ events, onEventClick }) => {
  return (
    <div className="space-y-4">
      {events.map((event, index) => {
        const IconComponent = timelineIconMapping[event.label] || timelineIconMapping["Autre"];
        const date = event.date ? new Date(event.date) : new Date();
        const companyName = event.pvag?.file?.company?.name || 'N/A';
        
        return (
          <motion.div
            key={event.original_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card 
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => onEventClick(event)}
            >
              <CardHeader className="flex flex-row items-center gap-4 pb-2">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <IconComponent className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-lg">{event.title}</h3>
                    <span className="text-sm text-gray-500">
                      {format(date, 'dd MMMM yyyy', { locale: fr })}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Building2 className="h-4 w-4" />
                    <span>{companyName}</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-3 line-clamp-2">{event.text}</p>
                <div className="flex gap-2">
                  <Badge variant="secondary">{event.label}</Badge>
                  <Badge variant="outline">{event.type}</Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        );
      })}

      {events.length === 0 && (
        <div className="flex flex-col items-center justify-center h-60 bg-gray-50 rounded-lg border border-dashed border-gray-300 p-6">
          <p className="text-gray-500 mb-2">Aucun résultat trouvé</p>
          <p className="text-sm text-gray-400">Essayez avec d'autres termes de recherche</p>
        </div>
      )}
    </div>
  );
};
