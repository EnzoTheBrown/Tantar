
import React from 'react';
import { Button } from '../ui/button';
import { Search } from 'lucide-react';

interface FilterActionsProps {
  onApply: () => void;
  onClear: () => void;
}

export const FilterActions: React.FC<FilterActionsProps> = ({
  onApply,
  onClear,
}) => {
  return (
    <div className="flex justify-end space-x-2 pt-2">
      <Button variant="outline" onClick={onClear}>
        Réinitialiser
      </Button>
      <Button onClick={onApply}>
        <Search className="mr-2 h-4 w-4" />
        Appliquer
      </Button>
    </div>
  );
};
