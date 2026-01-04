
import React from 'react';

export const EmptyTimeline: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-60 bg-gray-50 rounded-lg border border-dashed border-gray-300 p-6">
      <p className="text-gray-500 mb-2">Aucun événement trouvé</p>
      <p className="text-sm text-gray-400">Ajustez vos filtres ou ajoutez de nouveaux documents</p>
    </div>
  );
};
