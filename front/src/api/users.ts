
import { api, handleError } from './config';
import type { User, AccessLevel, UserInput, Account, AccountInput } from '../types/api';

export const getUsers = async (): Promise<User[]> => {
  try {
    const response = await api.get('/users');
    return response.data;
  } catch (error) {
    handleError(error);
    return []; // Return empty array on error
  }
};

export const createUser = async (userData: UserInput): Promise<User> => {
  try {
    const response = await api.post('/user', userData);
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

export const deleteUser = async (userId: string): Promise<boolean> => {
  try {
    await api.delete(`/user/${userId}`);
    return true;
  } catch (error) {
    handleError(error);
    return false;
  }
};

// Account functions
export const createAccount = async (accountData: AccountInput): Promise<Account> => {
  try {
    const response = await api.post('/account', accountData);
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

export const getAccount = async (accountId: string): Promise<Account> => {
  try {
    const response = await api.get(`/account/${accountId}`);
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

// Access Management
export const getUserCompanyAccesses = async (): Promise<AccessLevel[]> => {
  try {
    const response = await api.get('/accesses');
    return response.data;
  } catch (error) {
    handleError(error);
    return []; // Return empty array on error
  }
};

export const createUserCompanyAccess = async (access: AccessLevel): Promise<AccessLevel> => {
  try {
    const response = await api.post('/access', access);
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

export const updateUserCompanyAccess = async (
  userOriginalId: string,
  companyOriginalId: string,
  accessLevel: string
): Promise<AccessLevel> => {
  try {
    const response = await api.put(
      `/access/${userOriginalId}/${companyOriginalId}`,
      { access_level: accessLevel }
    );
    return response.data;
  } catch (error) {
    handleError(error);
    throw error;
  }
};

export const deleteUserCompanyAccess = async (
  userOriginalId: string,
  companyOriginalId: string
): Promise<boolean> => {
  try {
    await api.delete(`/access/${userOriginalId}/${companyOriginalId}`);
    return true;
  } catch (error) {
    handleError(error);
    throw error;
  }
};
