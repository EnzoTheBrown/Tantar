
import { api, handleError } from './config';
import type { Company, CompanyInput, CompanyUpdate } from '../types/api';

export const getCompanies = async (): Promise<Company[]> => {
  try {
    const response = await api.get('/companies');
    
    // Enhance companies with mock roles and shares data
    const enhancedCompanies = response.data.map((company: Company) => {
      if (!company.roles) {
        // Add mock roles data with more realistic names
        company.roles = [
          {
            name: "PRÉSIDENT",
            person: {
              name: "Adrien Lefèvre",
              is_moral: false
            }
          },
          {
            name: "UNKNOWN",
            person: {
              name: "Clara Dubois",
              is_moral: false
            }
          },
          {
            name: "UNKNOWN",
            person: {
              name: company.name,
              is_moral: true
            }
          }
        ];
      }
      
      if (!company.shares) {
        // Add mock shares data with more realistic names and shares count
        company.shares = [
          {
            person: {
              name: "Clara Dubois",
              is_moral: false
            },
            percentage: 50,
            shares: 500
          },
          {
            person: {
              name: "Adrien Lefèvre",
              is_moral: false
            },
            percentage: 50,
            shares: 500
          }
        ];
      }
      
      return company;
    });
    
    return enhancedCompanies;
  } catch (error) {
    handleError(error);
    return []; // Return empty array on error
  }
};

export const getCompany = async (companyId: string): Promise<Company | null> => {
  try {
    const response = await api.get(`/company/${companyId}`);
    return response.data;
  } catch (error) {
    handleError(error);
    return null;
  }
};

export const createCompany = async (company: CompanyInput): Promise<Company> => {
  try {
    const response = await api.post('/company', company);
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

export const updateCompany = async (companyId: string, data: CompanyUpdate): Promise<Company> => {
  try {
    const response = await api.put(`/company/${companyId}`, data);
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

export const deleteCompany = async (companyId: string): Promise<boolean> => {
  try {
    await api.delete(`/company/${companyId}`);
    return true;
  } catch (error) {
    handleError(error);
    return false;
  }
};
