import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth
export const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login', null, {
    auth: { username, password },
  });
  return response.data;
};

// Documents
export const uploadDocument = async (file: File, token: string) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/admin/documents/upload', formData, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const listDocuments = async (token: string) => {
  const response = await api.get('/admin/documents', {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return response.data;
};

export const deleteDocument = async (documentId: string, token: string) => {
  const response = await api.delete(`/admin/documents/${documentId}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return response.data;
};

// Chat Sessions
export const listSessions = async () => {
  const response = await api.get('/chat/sessions?limit=50');
  return response.data;
};

export const getSessionHistory = async (sessionId: string) => {
  const response = await api.get(`/chat/${sessionId}/history`);
  return response.data;
};

// Feedback
export const getFeedbackStats = async () => {
  const response = await api.get('/feedback/stats');
  return response.data;
};

export const getAllFeedback = async () => {
  const response = await api.get('/feedback/all?limit=100');
  return response.data;
};

export const markFeedbackReviewed = async (feedbackId: number, token: string) => {
  const response = await api.patch(`/feedback/${feedbackId}/review`, null, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return response.data;
};
