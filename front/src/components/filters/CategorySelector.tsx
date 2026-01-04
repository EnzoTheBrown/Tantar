
import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

interface CategorySelectorProps {
  categories: string[];
  label: string;
  setLabel: (value: string) => void;
}

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  categories,
  label,
  setLabel,
}) => {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">Catégorie</label>
      <Select value={label} onValueChange={setLabel}>
        <SelectTrigger>
          <SelectValue placeholder="Toutes les catégories" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Toutes les catégories</SelectItem>
          {categories.map((category) => (
            <SelectItem key={category} value={category}>
              {category}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};
