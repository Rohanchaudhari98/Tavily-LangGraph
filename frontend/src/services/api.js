// API service module using Axios
// Provides methods to interact with the backend for queries

import axios from 'axios';

// Base URL for the API, falling back to localhost if not set in environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create an Axios instance with default headers
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Create a new query
 * @param {Object} queryData - Data for the new query
 * @returns {Promise<Object>} - Newly created query data
 */
export const createQuery = async (queryData) => {
  const response = await api.post('/api/queries', queryData);
  return response.data;
};

/**
 * Fetch a query by its ID
 * @param {string} queryId - ID of the query to fetch
 * @returns {Promise<Object>} - Query data
 */
export const getQuery = async (queryId) => {
  const response = await api.get(`/api/queries/${queryId}`);
  return response.data;
};

/**
 * List queries with optional pagination
 * @param {number} skip - Number of queries to skip
 * @param {number} limit - Maximum number of queries to return
 * @returns {Promise<Array>} - List of queries
 */
export const listQueries = async (skip = 0, limit = 20) => {
  const response = await api.get('/api/queries', {
    params: { skip, limit },
  });
  return response.data;
};

/**
 * Delete a query by ID
 * @param {string} queryId - ID of the query to delete
 * @returns {Promise<Object>} - Response from the delete request
 */
export const deleteQuery = async (queryId) => {
  const response = await api.delete(`/api/queries/${queryId}`);
  return response.data;
};

// Export the Axios instance for custom requests if needed
export default api;
