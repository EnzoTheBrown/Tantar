
import React from 'react';
import { Event, DocumentEdge, Contract } from '@/types/api';
import { motion } from 'framer-motion';
import { TimelineEvent } from './TimelineEvent';

interface TimelineGroupProps {
  dateGroup: string;
  events: Event[];
  groupIndex: number;
  onEventClick: (event: Event) => void;
  onRelatedDocumentClick: (doc: DocumentEdge) => void;
  onEventHover: (label: string | null) => void;
  hoveredEventLabel: string | null;
  onContractsClick: (event: Event) => void;
  eventContracts: Record<string, Contract[]>;
}

export const TimelineGroup: React.FC<TimelineGroupProps> = ({
  dateGroup,
  events,
  groupIndex,
  onEventClick,
  onRelatedDocumentClick,
  onEventHover,
  hoveredEventLabel,
  onContractsClick,
  eventContracts
}) => {
  return (
    <div className="mb-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: groupIndex * 0.1 }}
        className="sticky top-0 z-10 mb-4 bg-blue-50 py-2 px-4 rounded-lg shadow-sm"
      >
        <h3 className="text-xl font-bold text-blue-700">{dateGroup}</h3>
      </motion.div>
      
      <div className="relative pl-8 before:content-[''] before:absolute before:left-4 before:top-0 before:h-full before:w-0.5 before:bg-blue-200">
        {events.map((event, eventIndex) => (
          <TimelineEvent
            key={event.original_id}
            event={event}
            groupIndex={groupIndex}
            eventIndex={eventIndex}
            onEventClick={onEventClick}
            onRelatedDocumentClick={onRelatedDocumentClick}
            onEventHover={onEventHover}
            isHighlighted={event.label === hoveredEventLabel}
            onContractsClick={onContractsClick}
            contracts={eventContracts[event.original_id] || []}
          />
        ))}
      </div>
    </div>
  );
};
