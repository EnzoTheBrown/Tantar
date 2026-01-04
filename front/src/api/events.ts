import { api, handleError } from './config';
import type { Event, EventsResponse, Contract } from '../types/api';

export const getEvents = async (params: {
  start_date?: string;
  end_date?: string;
  label?: string;
  question?: string;
  k?: number;
  company_id?: string;
}): Promise<EventsResponse> => {
  try {
    const response = await api.get('/events', { params });
    
    // Ensure each event has relatedDocuments initialized as an empty array if it's not present
    const events = response.data.events || [];
    events.forEach(event => {
      if (!event.relatedDocuments) {
        event.relatedDocuments = [];
      }
    });
    
    return {
      events,
      categories: response.data.categories || []
    };
  } catch (error) {
    handleError(error);
    return { events: [], categories: [] }; // Return empty response on error
  }
};

export const getCategories = async (): Promise<string[]> => {
  try {
    const response = await api.get('/categories');
    return response.data;
  } catch (error) {
    handleError(error);
    return []; // Return empty array on error
  }
};

export const getCompanyEventsByQuestion = async (
  companyId: string,
  question: string,
  k: number = 10
): Promise<Event[]> => {
  try {
    const response = await api.get('/events', {
      params: { company_id: companyId, question, k }
    });
    
    // Ensure each event has relatedDocuments initialized
    const events = response.data.events || [];
    events.forEach(event => {
      if (!event.relatedDocuments) {
        event.relatedDocuments = [];
      }
    });
    
    return events;
  } catch (error) {
    handleError(error);
    return []; // Return empty array on error
  }
};

// Fixed function to get authorized contracts for an event (fixed event ID parameter)
export const getAuthorizedContracts = async (eventId: string): Promise<Contract[]> => {
  try {
    const response = await api.get(`/events/${eventId}/authorized_contracts`);
    return response.data || [];
  } catch (error) {
    handleError(error);
    return []; // Return empty array on error
  }
};
