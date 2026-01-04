
import React, { useState } from 'react';
import { Button } from './ui/button';
import { Filter, X } from 'lucide-react';
import { format } from 'date-fns';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { DateFilterTabs } from './filters/DateFilterTabs';
import { CategorySelector } from './filters/CategorySelector';
import { QuestionSearch } from './filters/QuestionSearch';
import { FilterActions } from './filters/FilterActions';

interface TimelineFiltersProps {
  categories: string[];
  onFilterChange: (filters: TimelineFilters) => void;
}

export interface TimelineFilters {
  startDate?: string;
  endDate?: string;
  label?: string;
  question?: string;
  k?: number;
}

export const TimelineFilters: React.FC<TimelineFiltersProps> = ({ categories, onFilterChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [startDate, setStartDate] = useState<Date | undefined>(undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(undefined);
  const [label, setLabel] = useState<string>('');
  const [question, setQuestion] = useState('');
  const [k, setK] = useState(10);

  const handleApplyFilters = () => {
    const filters: TimelineFilters = {
      startDate: startDate ? format(startDate, 'yyyy-MM-dd') : undefined,
      endDate: endDate ? format(endDate, 'yyyy-MM-dd') : undefined,
      label: label || undefined,
      question: question || undefined,
      k: k
    };
    onFilterChange(filters);
  };

  const handleClearFilters = () => {
    setStartDate(undefined);
    setEndDate(undefined);
    setLabel('');
    setQuestion('');
    setK(10);
    onFilterChange({});
  };

  return (
    <div className="mb-6 bg-white rounded-lg shadow-sm p-4">
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">Filtres avancés</h3>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm">
              {isOpen ? <X className="h-4 w-4" /> : <Filter className="h-4 w-4" />}
            </Button>
          </CollapsibleTrigger>
        </div>
        
        <CollapsibleContent className="mt-4 space-y-4">
          <DateFilterTabs 
            startDate={startDate}
            endDate={endDate}
            setStartDate={setStartDate}
            setEndDate={setEndDate}
          />
          
          <CategorySelector 
            categories={categories}
            label={label}
            setLabel={setLabel}
          />
          
          <QuestionSearch 
            question={question}
            k={k}
            setQuestion={setQuestion}
            setK={setK}
          />
          
          <FilterActions 
            onApply={handleApplyFilters}
            onClear={handleClearFilters}
          />
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
};
