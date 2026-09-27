import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
});

export const getHealth = async () => {
  const response = await axios.get(`${API_BASE_URL}/health`);
  return response.data;
};

export const getSources = async () => {
  const response = await client.get('/sources');
  return response.data;
};

export const getSourceDetail = async (sourceId) => {
  const response = await client.get(`/sources/${sourceId}`);
  return response.data;
};

export const uploadSource = async (sourceName, sourceType, file) => {
  const formData = new FormData();
  formData.append('source_name', sourceName);
  formData.append('source_type', sourceType);
  formData.append('file', file);

  const response = await client.post('/sources', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteSource = async (sourceId) => {
  const response = await client.delete(`/sources/${sourceId}`);
  return response.data;
};
