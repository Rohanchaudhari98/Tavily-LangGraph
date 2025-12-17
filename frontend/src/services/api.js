import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a new query
export const createQuery = async (queryData) => {
  const response = await api.post('/api/queries', queryData);
  return response.data;
};

// Get query by ID
export const getQuery = async (queryId) => {
  const response = await api.get(`/api/queries/${queryId}`);
  return response.data;
};

// List all queries
export const listQueries = async (skip = 0, limit = 20) => {
  const response = await api.get('/api/queries', {
    params: { skip, limit }
  });
  return response.data;
};

// Delete query
export const deleteQuery = async (queryId) => {
  const response = await api.delete(`/api/queries/${queryId}`);
  return response.data;
};

export default api;