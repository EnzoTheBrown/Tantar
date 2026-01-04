
import { api, handleError } from './config';
import type { User } from '../types/api';

export const login = async (username: string, password: string) => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/login', formData);
    return response.data;
  } catch (error) {
    handleError(error);
  }
};

export const getCurrentUser = async (): Promise<User> => {
  try {
    const response = await api.get('/user');
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};
