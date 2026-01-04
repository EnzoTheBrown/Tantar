
import React from 'react';
import { timelineIconMapping } from '@/utils/timelineIcons';
import { cn } from '@/lib/utils';

interface TimelineIconLegendProps {
  className?: string;
  hoveredEventLabel?: string | null;
}

export const TimelineIconLegend: React.FC<TimelineIconLegendProps> = ({
  className,
  hoveredEventLabel = null,
}) => {
  // Convert the timelineIconMapping object to an array of entries
  const iconEntries = Object.entries(timelineIconMapping);

  return (
    <div className={cn('bg-white rounded-lg border border-gray-200 p-4 shadow-sm w-full', className)}>
      <h3 className="text-sm font-semibold mb-3 text-gray-700">Légende des icônes</h3>
      <div className="space-y-2">
        {iconEntries.map(([label, Icon]) => {
          const isHighlighted = hoveredEventLabel === label;
          return (
            <div 
              key={label} 
              className={cn(
                "flex items-center gap-2 text-xs p-2 rounded-md transition-colors duration-200",
                isHighlighted ? "bg-blue-50" : ""
              )}
            >
              <div className={cn(
                "h-6 w-6 rounded-full flex items-center justify-center shrink-0 transition-all duration-200",
                isHighlighted 
                  ? "bg-blue-600 ring-2 ring-blue-200 scale-110" 
                  : "bg-blue-500"
              )}>
                <Icon className="h-3 w-3 text-white" />
              </div>
              <span className={cn(
                "text-gray-700",
                isHighlighted ? "font-medium" : ""
              )}>
                {label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
