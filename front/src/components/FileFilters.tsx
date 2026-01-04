
import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Company } from '@/types/api';

interface FileFiltersProps {
  fileTypes: string[];
  companies: Company[];
  onFilterChange: (filterType: string, value: string) => void;
  selectedFilters: {
    type: string;
    companyId: string;
  };
}

export const FileFilters: React.FC<FileFiltersProps> = ({ 
  fileTypes, 
  companies, 
  onFilterChange, 
  selectedFilters 
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label htmlFor="type-filter" className="block text-sm font-medium text-gray-700 mb-1">
          Type de document
        </label>
        <Select 
          value={selectedFilters.type} 
          onValueChange={(value) => onFilterChange('type', value)}
        >
          <SelectTrigger id="type-filter" className="w-full bg-white border-gray-200">
            <SelectValue placeholder="Tous les types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all_types">Tous les types</SelectItem>
            {fileTypes.map((type) => (
              <SelectItem key={type} value={type}>{type}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      <div>
        <label htmlFor="company-filter" className="block text-sm font-medium text-gray-700 mb-1">
          Société
        </label>
        <Select 
          value={selectedFilters.companyId} 
          onValueChange={(value) => onFilterChange('companyId', value)}
        >
          <SelectTrigger id="company-filter" className="w-full bg-white border-gray-200">
            <SelectValue placeholder="Toutes les sociétés" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all_companies">Toutes les sociétés</SelectItem>
            {companies.map((company) => (
              <SelectItem key={company.original_id} value={company.original_id}>
                {company.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
