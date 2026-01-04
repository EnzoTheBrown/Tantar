
import * as XLSX from 'xlsx';
import { Event } from '@/types/api';

export const exportEventsToExcel = (events: Event[], fileName: string = 'events') => {
  const data = events.map(event => ({
    'Date': new Date(event.date).toLocaleDateString(),
    'Société': event.file.company.name,
    'Catégorie': event.label,
    'Type': event.type,
    'Titre': event.title,
    'Description': event.text,
  }));

  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Events');
  XLSX.writeFile(wb, `${fileName}.xlsx`);
};
