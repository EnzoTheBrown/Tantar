import React from 'react';
import { Event, DocumentEdge, Contract } from '@/types/api';
import { timelineIconMapping } from '@/utils/timelineIcons';
import { format } from 'date-fns';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { motion } from 'framer-motion';
import { FileText, Link2, FileCheck } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface TimelineEventProps {
  event: Event;
  groupIndex: number;
  eventIndex: number;
  onEventClick: (event: Event) => void;
  onRelatedDocumentClick: (doc: DocumentEdge) => void;
  onEventHover: (label: string | null) => void;
  isHighlighted: boolean;
  onContractsClick: (event: Event) => void;
  contracts: Contract[];
}

export const TimelineEvent: React.FC<TimelineEventProps> = ({
  event,
  groupIndex,
  eventIndex,
  onEventClick,
  onRelatedDocumentClick,
  onEventHover,
  isHighlighted,
  onContractsClick,
  contracts
}) => {
  const IconComponent = timelineIconMapping[event.label] || timelineIconMapping["Autre"];
  const date = event.date ? new Date(event.date) : new Date();
  const hasDate = date && !isNaN(date.getTime());

  // Trigger contract loading when component mounts
  React.useEffect(() => {
    onContractsClick(event);
  }, [event, onContractsClick]);

  // Prevent event propagation for document clicks
  const handleDocumentClick = (e: React.MouseEvent, doc: DocumentEdge) => {
    e.stopPropagation();
    onRelatedDocumentClick(doc);
  };

  // Handle contract click
  const handleContractClick = (e: React.MouseEvent, contract: Contract) => {
    e.stopPropagation();
    if (contract.original_id) {
      // Pass the contract as a document edge to use the same viewer
      const contractAsDoc: DocumentEdge = {
        id: contract.file_id,
        original_id: contract.original_id,
        label: contract.contract_type || 'Contrat'
      };
      onRelatedDocumentClick(contractAsDoc);
    }
  };

  return (
    <TooltipProvider>
      <Tooltip>
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: (groupIndex * 0.1) + (eventIndex * 0.05) }}
          className="relative mb-8"
          onMouseEnter={() => onEventHover(event.label)}
          onMouseLeave={() => onEventHover(null)}
        >
          <div className={`absolute -left-8 top-0 mt-1.5 flex h-8 w-8 items-center justify-center rounded-full ${isHighlighted ? 'bg-blue-600 ring-4 ring-blue-200' : 'bg-blue-500'} shadow-md transition-all duration-200`}>
            <IconComponent className="h-4 w-4 text-white" />
          </div>
          
          <div className="flex items-start">
            <TooltipTrigger asChild>
              <div 
                className={`ml-4 cursor-pointer rounded-lg bg-white p-4 shadow-lg transition-all hover:shadow-xl hover:translate-y-[-2px] ${isHighlighted ? 'ring-2 ring-blue-300' : ''} flex-1 mr-4`}
                onClick={() => onEventClick(event)}
              >
                <div className="mb-2 flex items-center justify-between">
                  <h4 className="text-lg font-semibold text-gray-800">{event.title}</h4>
                  <span className="text-sm text-gray-500">{hasDate ? format(date, 'dd MMMM yyyy') : 'Date inconnue'}</span>
                </div>
                
                <div className="flex items-center text-sm text-gray-600 space-x-2">
                  <span className="inline-block rounded-full px-3 py-1 text-xs bg-blue-100 text-blue-800">
                    {event.label}
                  </span>
                  <span>•</span>
                  <span>{event.type}</span>
                </div>
              </div>
            </TooltipTrigger>
            
            <div className="w-64 bg-gray-50 rounded-lg p-3 border border-gray-200 shrink-0">
              {/* Related Documents Section */}
              {event.relatedDocuments && event.relatedDocuments.length > 0 && (
                <div>
                  <div className="flex items-center mb-2">
                    <Link2 className="h-4 w-4 text-blue-600 mr-2" />
                    <h5 className="text-sm font-medium text-gray-700">Documents liés</h5>
                  </div>
                  <div className="space-y-2">
                    {event.relatedDocuments.map((doc) => (
                      <div 
                        key={doc.id || doc.original_id}
                        className="flex items-center p-2 bg-white rounded border border-gray-200 text-sm hover:bg-blue-50 cursor-pointer"
                        onClick={(e) => handleDocumentClick(e, doc)}
                      >
                        <FileText className="h-4 w-4 text-blue-500 mr-2" />
                        <div className="text-xs">
                          {doc.name ? (
                            <div className="font-medium truncate max-w-[180px]" title={doc.name}>
                              {doc.name}
                            </div>
                          ) : (
                            <div className="font-medium">Document #{doc.original_id || doc.target_id}</div>
                          )}
                          <Badge variant="outline" className="text-[10px] mt-1">
                            {doc.label}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Authorized Contracts Section */}
              {contracts.length > 0 && (
                <div className={`${event.relatedDocuments && event.relatedDocuments.length > 0 ? 'mt-4 pt-4 border-t border-gray-200' : ''}`}>
                  <div className="flex items-center mb-2">
                    <FileCheck className="h-4 w-4 text-blue-600 mr-2" />
                    <h5 className="text-sm font-medium text-gray-700">Contrats autorisés</h5>
                  </div>
                  <div className="space-y-2">
                    {contracts.map((contract) => (
                      <div 
                        key={contract.original_id}
                        className="flex items-center p-2 bg-white rounded border border-gray-200 text-sm hover:bg-blue-50 cursor-pointer"
                        onClick={(e) => handleContractClick(e, contract)}
                      >
                        <FileCheck className="h-4 w-4 text-blue-500 mr-2" />
                        <div className="text-xs">
                          <div className="font-medium truncate max-w-[180px]" title={contract.title || contract.name || 'Contrat'}>
                            {contract.title || contract.name || `Contrat #${contract.original_id}`}
                          </div>
                          {contract.contract_type && (
                            <Badge variant="outline" className="text-[10px] mt-1">
                              {contract.contract_type}
                            </Badge>
                          )}
                          {contract.date && (
                            <div className="text-[10px] text-gray-500 mt-1">
                              {new Date(contract.date).toLocaleDateString()}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Show empty state if no documents or contracts */}
              {(!event.relatedDocuments || event.relatedDocuments.length === 0) && contracts.length === 0 && (
                <div className="flex flex-col items-center justify-center py-4 text-gray-400">
                  <FileText className="h-8 w-8 mb-2 opacity-30" />
                  <p className="text-xs text-center">Aucun document lié</p>
                </div>
              )}
            </div>
          </div>
          
          <TooltipContent side="right" className="max-w-md p-4 bg-white shadow-lg rounded-lg border border-gray-200">
            <p className="text-sm whitespace-pre-wrap">{event.text}</p>
          </TooltipContent>
        </motion.div>
      </Tooltip>
    </TooltipProvider>
  );
};
