import axios from 'axios';

// Base API URL - adjust this based on your backend URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload image for prediction
 * @param {File} file - Image file
 * @param {string} user - Optional user name
 * @param {string} description - Optional description
 * @returns {Promise} API response with detection results
 */
export const predictImage = async (file, user = '', description = '') => {
  const formData = new FormData();
  formData.append('file', file);
  if (user) formData.append('user', user);
  if (description) formData.append('description', description);

  const response = await api.post('/predict', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Get all records
 * @returns {Promise} List of all detection records
 */
export const getRecords = async () => {
  const response = await api.get('/records');
  return response.data;
};

/**
 * Get single record by ID
 * @param {number} id - Record ID
 * @returns {Promise} Single record
 */
export const getRecord = async (id) => {
  const response = await api.get(`/records/${id}`);
  return response.data;
};

/**
 * Update record description
 * @param {number} id - Record ID
 * @param {string} description - New description
 * @returns {Promise} Updated record
 */
export const updateRecordDescription = async (id, description) => {
  const response = await api.patch(`/records/${id}`, { description });
  return response.data;
};

/**
 * Delete record
 * @param {number} id - Record ID
 * @returns {Promise} Success message
 */
export const deleteRecord = async (id) => {
  const response = await api.delete(`/records/${id}`);
  return response.data;
};

/**
 * Get image URL for display
 * @param {string} filename - Image filename
 * @returns {string} Full image URL
 */
export const getImageUrl = (filename) => {
  return `${API_BASE_URL}/uploads/${filename}`;
};

export default api;
