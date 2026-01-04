
import { useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Eye, FileText, Download } from "lucide-react";
import { Button } from "./ui/button";
import { FileViewDialog } from "./FileViewDialog";
import { toast } from "sonner";
import * as api from "@/api";
import type { File } from '@/types/api';

interface FilesListProps {
  files: File[];
  title: string;
  compact?: boolean;
}

export const FilesList = ({ files, title, compact = false }: FilesListProps) => {
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null);

  const handleDownload = async (fileId: string, fileName: string) => {
    try {
      toast.promise(api.downloadFile(fileId), {
        loading: 'Téléchargement du fichier...',
        success: 'Fichier téléchargé avec succès',
        error: 'Erreur lors du téléchargement'
      });
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  if (compact) {
    return (
      <>
        <div className="overflow-hidden">
          {files && files.length > 0 ? (
            <ul className="space-y-1">
              {files.map((file) => (
                <li key={file.original_id} className="flex items-center justify-between py-1 text-sm border-b border-gray-100 last:border-0">
                  <div className="flex items-center gap-2 truncate">
                    <FileText className="h-3.5 w-3.5 text-gray-400 flex-shrink-0" />
                    <span className="truncate font-medium">{file.name}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 w-6 p-0 hover:bg-blue-50 hover:text-blue-600"
                      onClick={() => setSelectedFileId(file.original_id)}
                    >
                      <Eye className="h-3.5 w-3.5" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 w-6 p-0 hover:bg-green-50 hover:text-green-600"
                      onClick={() => handleDownload(file.original_id, file.name)}
                    >
                      <Download className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="py-3 text-center text-sm text-gray-500">
              Aucun document disponible
            </div>
          )}
        </div>
        {selectedFileId && (
          <FileViewDialog 
            open={!!selectedFileId} 
            onOpenChange={() => setSelectedFileId(null)} 
            fileId={selectedFileId} 
          />
        )}
      </>
    );
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 transition-all duration-200 hover:shadow-md">
        <div className="p-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold flex items-center gap-2 text-gray-800">
            <FileText className="h-5 w-5 text-blue-500" />
            {title}
          </h2>
        </div>
        <div className="overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-gray-50">
                <TableHead className="font-medium text-gray-700">Document</TableHead>
                <TableHead className="font-medium text-gray-700">Société</TableHead>
                <TableHead className="font-medium text-gray-700">Type</TableHead>
                <TableHead className="w-[100px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {files && files.length > 0 ? files.map((file) => (
                <TableRow key={file.original_id} className="hover:bg-gray-50">
                  <TableCell className="font-medium">{file.name}</TableCell>
                  <TableCell className="text-gray-600">{file.company?.name || 'N/A'}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                      {file.type}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-8 w-8 p-0 hover:bg-blue-50 hover:text-blue-600"
                        onClick={() => setSelectedFileId(file.original_id)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="h-8 w-8 p-0 hover:bg-green-50 hover:text-green-600"
                        onClick={() => handleDownload(file.original_id, file.name)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8 text-gray-500">
                    Aucun document disponible
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
      {selectedFileId && (
        <FileViewDialog 
          open={!!selectedFileId} 
          onOpenChange={() => setSelectedFileId(null)} 
          fileId={selectedFileId} 
        />
      )}
    </>
  );
};
