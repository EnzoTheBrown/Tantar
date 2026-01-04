
import React, { useRef, useState } from 'react';
import { Button } from './ui/button';
import { Plus, Loader2 } from 'lucide-react';
import { Progress } from './ui/progress';
import { toast } from 'sonner';
import * as api from '../api';
import type { File } from '@/types/api';

interface FileUploaderProps {
  onFilesUpdated: (files: File[]) => void;
}

export const FileUploader = ({ onFilesUpdated }: FileUploaderProps) => {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files?.length) return;

    try {
      setUploading(true);
      
      const uploadPromises = Array.from(files).map(async (file) => {
        try {
          await api.uploadFile(file);
          toast.success(`${file.name} uploaded successfully`, {
            description: "File has been uploaded and processed",
          });
        } catch (error) {
          toast.error(`Failed to upload ${file.name}`, {
            description: "Please try again or contact support if the issue persists",
          });
          console.error('Error uploading file:', error);
        }
      });

      await Promise.all(uploadPromises);

      const filesRes = await api.getFiles();
      const sortedFiles = filesRes.sort((a: File, b: File) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      onFilesUpdated(sortedFiles.slice(0, 5));
      
    } catch (error) {
      console.error('Error handling files:', error);
      toast.error('An error occurred while uploading files');
    } finally {
      setUploading(false);
      if (event.target) event.target.value = '';
    }
  };

  const handleDropAreaClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="mb-6 max-w-3xl mx-auto">
      <div 
        onClick={handleDropAreaClick}
        className={`w-full h-24 border-2 border-dashed rounded-lg transition-all duration-200 cursor-pointer ${
          uploading 
            ? 'border-blue-300 bg-blue-50 text-blue-600' 
            : 'border-gray-300 bg-white text-gray-600 hover:bg-gray-50 hover:border-gray-400'
        }`}
      >
        <Button 
          className="w-full h-full"
          disabled={uploading}
        >
          <div className="flex flex-col items-center gap-2">
            {uploading ? (
              <>
                <div className="flex items-center gap-2">
                  <Loader2 className="h-6 w-6 animate-spin" />
                  <span>Analyse du document en cours...</span>
                </div>
                <Progress value={33} className="w-1/2" />
              </>
            ) : (
              <>
                <Plus className="h-6 w-6" />
                <span>Déposez les fichiers ici ou cliquez pour télécharger</span>
                <span className="text-sm text-gray-400">
                  Formats acceptés : PDF, DOC, DOCX
                </span>
              </>
            )}
          </div>
        </Button>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        onChange={handleFileUpload}
        accept=".pdf,.doc,.docx"
        multiple
      />
    </div>
  );
};
