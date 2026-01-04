
import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { EventSearchDialog } from './EventSearchDialog';

export const SearchBar = () => {
  const [isEventSearchOpen, setIsEventSearchOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Open the search dialog with the current search term
    setIsEventSearchOpen(true);
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="flex items-center space-x-2 max-w-3xl mx-auto my-6 group">
        <div className="relative flex-1 transition-all duration-200 group-hover:shadow-lg">
          <Input
            placeholder="Recherchez des événements..."
            className="pl-4 pr-10 py-2 w-full transition-all duration-200 group-hover:border-blue-300"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
            <Search className="h-5 w-5" />
          </div>
        </div>
        <Button 
          type="submit"
          variant="outline" 
          className="px-3 transition-all duration-200 group-hover:border-blue-300"
        >
          <Search className="h-5 w-5 mr-2" />
          Rechercher
        </Button>
        <Button 
          type="button"
          variant="outline" 
          className="px-3 transition-all duration-200 group-hover:border-blue-300"
          onClick={() => setIsEventSearchOpen(true)}
        >
          <Filter className="h-5 w-5" />
        </Button>
      </form>
      <EventSearchDialog 
        open={isEventSearchOpen} 
        onOpenChange={setIsEventSearchOpen} 
        initialQuery={searchTerm}
      />
    </>
  );
};
