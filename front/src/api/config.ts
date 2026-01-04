
import axios, { AxiosError } from 'axios';

// Create API instance with base configuration
const baseURL =
  import.meta.env.VITE_API_URL?.toString().trim() || 'https://app.tantar.ai';

export const api = axios.create({
  baseURL,
});

// Add a request interceptor to add the token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Error handler helper
export const handleError = (error: unknown) => {
  if (error instanceof AxiosError) {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
  throw error;
};
