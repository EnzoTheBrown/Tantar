
import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent } from './ui/dialog';
import { Button } from './ui/button';
import { Download, Loader2 } from 'lucide-react';
import * as api from '../api';
import { toast } from 'sonner';

interface FileViewDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fileId: string;
  pageIndex?: number;
}

export const FileViewDialog: React.FC<FileViewDialogProps> = ({ 
  open, 
  onOpenChange, 
  fileId,
  pageIndex = 0 
}) => {
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && fileId) {
      loadFile();
    }
    
    return () => {
      // Clean up the URL when component unmounts or dialog closes
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl);
        setFileUrl(null);
      }
    };
  }, [open, fileId]);

  const loadFile = async () => {
    if (!fileId) return;
    
    try {
      setLoading(true);
      setError(null);
      console.log('Loading file with ID:', fileId);
      const response = await api.downloadFile(fileId);
      
      // Create a blob from the response data
      const blob = new Blob([response], { type: 'application/pdf' });
      
      // Create an object URL for the blob
      const url = URL.createObjectURL(blob);
      
      // Add page parameter if specified
      const fullUrl = `${url}#page=${pageIndex + 1}`;
      setFileUrl(fullUrl);
      setLoading(false);
    } catch (error) {
      console.error('Error loading file:', error);
      setError('Impossible de charger le fichier. Veuillez réessayer.');
      toast.error('Erreur lors du chargement du fichier');
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!fileId) return;
    
    try {
      setLoading(true);
      toast.promise(
        (async () => {
          const response = await api.downloadFile(fileId);
          const blob = new Blob([response], { type: 'application/pdf' });
          const url = URL.createObjectURL(blob);
          
          // Create an anchor element and trigger download
          const a = document.createElement('a');
          a.href = url;
          a.download = `document-${fileId}.pdf`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          
          // Clean up
          setTimeout(() => URL.revokeObjectURL(url), 100);
          return 'Téléchargement terminé';
        })(),
        {
          loading: 'Téléchargement en cours...',
          success: 'Fichier téléchargé avec succès',
          error: 'Erreur lors du téléchargement'
        }
      );
    } catch (error) {
      console.error('Error downloading file:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl min-h-[85vh] p-6">
        <div className="flex flex-col h-full">
          <div className="flex justify-end mb-4">
            <Button variant="outline" size="sm" onClick={handleDownload} disabled={loading || !fileUrl}>
              <Download className="h-4 w-4 mr-2" />
              Télécharger
            </Button>
          </div>
          <div className="flex-grow bg-white rounded-lg overflow-hidden border border-gray-200">
            {loading ? (
              <div className="w-full h-full min-h-[70vh] flex items-center justify-center">
                <div className="flex flex-col items-center">
                  <Loader2 className="h-8 w-8 animate-spin text-blue-500 mb-2" />
                  <p className="text-gray-500">Chargement du document...</p>
                </div>
              </div>
            ) : error ? (
              <div className="w-full h-full min-h-[70vh] flex items-center justify-center">
                <div className="text-center text-red-500 max-w-md px-4">
                  <p>{error}</p>
                  <Button variant="outline" className="mt-4" onClick={loadFile}>
                    Réessayer
                  </Button>
                </div>
              </div>
            ) : fileUrl ? (
              <iframe 
                src={fileUrl}
                className="w-full h-full min-h-[70vh] border-none" 
                title="Document viewer"
              />
            ) : (
              <div className="w-full h-full min-h-[70vh] flex items-center justify-center">
                <p className="text-gray-500">Aucun document à afficher</p>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
