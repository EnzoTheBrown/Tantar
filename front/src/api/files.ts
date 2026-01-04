
import { api, handleError } from './config';
import type { File, FileInformation } from '../types/api';

export const getFiles = async (companyId?: string, orderedBy?: string): Promise<File[]> => {
  try {
    const params: { company_id?: string; ordered_by?: string } = {};
    if (companyId) {
      params.company_id = companyId;
    }
    if (orderedBy) {
      params.ordered_by = orderedBy;
    }
    
    const response = await api.get('/files', { params });
    return response.data;
  } catch (error) {
    handleError(error);
    return []; // Return empty array on error
  }
};

export const getFileById = async (fileId: string): Promise<File | null> => {
  try {
    const response = await api.get(`/file/${fileId}`);
    return response.data;
  } catch (error) {
    handleError(error);
    return null;
  }
};

// Note: This uses the browser's File type, not our custom File type
export const uploadFile = async (file: Blob, companyId?: string) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: companyId ? { company_id: companyId } : {}
    });
    return response.data;
  } catch (error) {
    handleError(error);
  }
};

export const downloadFile = async (fileId: string): Promise<ArrayBuffer> => {
  try {
    const response = await api.get(`/file/${fileId}/download`, {
      responseType: 'arraybuffer'
    });
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

export const invalidateFile = async (
  companyId: string, 
  fileId: string, 
  fileInfo: FileInformation
): Promise<boolean> => {
  try {
    await api.patch(`/company/${companyId}/file/${fileId}`, fileInfo);
    return true;
  } catch (error) {
    handleError(error);
    return false;
  }
};
