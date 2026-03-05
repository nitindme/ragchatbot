import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const startSession = async () => {
  const response = await api.post('/chat/start');
  return response.data.session_id;
};

export const sendMessage = async (sessionId: string, message: string) => {
  const response = await api.post(`/chat/${sessionId}/message`, { message });
  return response.data;
};

export const getChatHistory = async (sessionId: string) => {
  const response = await api.get(`/chat/${sessionId}/history`);
  return response.data;
};

export const submitFeedback = async (feedbackData: {
  session_id: string;
  message_id: number;
  question: string;
  response: string;
  rating: number;
  comment?: string;
  retrieved_chunks?: any[];
  sources?: string[];
}) => {
  const response = await api.post('/feedback', feedbackData);
  return response.data;
};
