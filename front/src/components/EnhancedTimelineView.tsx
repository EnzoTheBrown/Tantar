import React, { useState, useEffect } from 'react';
import { Event, DocumentEdge, Contract } from '@/types/api';
import { format } from 'date-fns';
import { FileViewDialog } from './FileViewDialog';
import { TimelineGroup } from './timeline/TimelineGroup';
import { EmptyTimeline } from './timeline/EmptyTimeline';
import { TimelineIconLegend } from './TimelineIconLegend';
import { ScrollArea } from './ui/scroll-area';
import { getAuthorizedContracts } from '@/api/events';
import { useToast } from '@/hooks/use-toast';

interface EnhancedTimelineViewProps {
  events: Event[];
  onEventClick: (event: Event) => void;
}

export const EnhancedTimelineView: React.FC<EnhancedTimelineViewProps> = ({ events, onEventClick }) => {
  const [hoveredEventLabel, setHoveredEventLabel] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<DocumentEdge | null>(null);
  const [eventContracts, setEventContracts] = useState<Record<string, Contract[]>>({});
  const { toast } = useToast();
  
  // Group events by month and year
  const groupedEvents = events.reduce((groups, event) => {
    const date = event.date ? new Date(event.date) : new Date();
    const key = format(date, 'MMMM yyyy');
    
    if (!groups[key]) {
      groups[key] = [];
    }
    
    groups[key].push(event);
    return groups;
  }, {} as Record<string, Event[]>);

  // Sort groups by date (newest first)
  const sortedGroups = Object.entries(groupedEvents).sort((a, b) => {
    const dateA = a[1][0].date ? new Date(a[1][0].date) : new Date();
    const dateB = b[1][0].date ? new Date(b[1][0].date) : new Date();
    return dateB.getTime() - dateA.getTime();
  });

  // Handle related document click
  const handleRelatedDocumentClick = (doc: DocumentEdge) => {
    setSelectedDocument(doc);
    // Additional logic for handling document click can be added here
    console.log('Related document clicked:', doc);
  };

  // Handle contract click and fetch contracts for an event
  const handleContractsClick = async (event: Event) => {
    try {
      // Only fetch if we haven't fetched for this event before
      if (!eventContracts[event.original_id]) {
        console.log('Fetching contracts for event:', event.original_id);
        const contracts = await getAuthorizedContracts(event.original_id);
        console.log('Fetched contracts:', contracts);
        setEventContracts(prev => ({
          ...prev,
          [event.original_id]: contracts
        }));
      }
    } catch (error) {
      console.error('Error fetching contracts:', error);
      toast({
        title: "Erreur",
        description: "Impossible de récupérer les contrats associés.",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="flex flex-col lg:flex-row w-full gap-4">
      {/* Main timeline content - takes up most of the width */}
      <div className="flex-1">
        {sortedGroups.length > 0 ? (
          sortedGroups.map(([dateGroup, groupEvents], groupIndex) => (
            <TimelineGroup
              key={dateGroup}
              dateGroup={dateGroup}
              events={groupEvents}
              groupIndex={groupIndex}
              onEventClick={onEventClick}
              onRelatedDocumentClick={handleRelatedDocumentClick}
              onEventHover={setHoveredEventLabel}
              hoveredEventLabel={hoveredEventLabel}
              onContractsClick={handleContractsClick}
              eventContracts={eventContracts}
            />
          ))
        ) : (
          <EmptyTimeline />
        )}
      </div>
      
      {/* Legend now visible on all screen sizes, with a fixed width using scroll area for overflow */}
      <div className="w-full lg:w-72 shrink-0">
        <ScrollArea className="h-[calc(100vh-220px)] sticky top-4 pr-4">
          <TimelineIconLegend 
            hoveredEventLabel={hoveredEventLabel} 
          />
        </ScrollArea>
      </div>

      {/* File viewer dialog */}
      {selectedDocument && (
        <FileViewDialog
          open={!!selectedDocument}
          onOpenChange={(open) => {
            if (!open) setSelectedDocument(null);
          }}
          fileId={selectedDocument.original_id || ''}
          pageIndex={0}
        />
      )}
    </div>
  );
};
