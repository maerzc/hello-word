/**
 * API Service für SmartInbox Backend-Kommunikation
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Sendet eine E-Mail zur Verarbeitung an das Backend
 */
export const processEmail = async (emailData) => {
  try {
    const response = await api.post('/process-email', emailData);
    return response.data;
  } catch (error) {
    console.error('Fehler beim Verarbeiten der E-Mail:', error);
    throw error;
  }
};

/**
 * Sendet eine Chat-Nachricht
 */
export const sendChatMessage = async (message) => {
  try {
    const response = await api.post('/chat', { message });
    return response.data;
  } catch (error) {
    console.error('Fehler beim Senden der Chat-Nachricht:', error);
    throw error;
  }
};

/**
 * Health Check
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Fehler beim Health Check:', error);
    throw error;
  }
};

/**
 * Holt den aktuellen State
 */
export const getCurrentState = async () => {
  try {
    const response = await api.get('/state');
    return response.data;
  } catch (error) {
    console.error('Fehler beim Abrufen des State:', error);
    throw error;
  }
};

/**
 * Setzt den State zurück
 */
export const resetState = async () => {
  try {
    const response = await api.post('/reset');
    return response.data;
  } catch (error) {
    console.error('Fehler beim Zurücksetzen des State:', error);
    throw error;
  }
};

export default api;
