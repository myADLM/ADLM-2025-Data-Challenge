// API configuration - works for both local and Docker environments
const getApiBaseUrl = () => {
  // Both Docker (nginx) and local dev (Vite) use relative URLs
  // Docker: nginx proxies /api/* to http://backend:5174/
  // Local: Vite proxies /api/* to http://localhost:5174/
  console.log('🌐 API Base URL configured for:', window.location.href);
  return ''; // Use relative URLs, proxy will handle routing
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  PING: '/api/ping',
  CHAT: '/api/chat',
  DOCUMENTS: '/documents',
  STATUS: '/api/status'
};

// Helper function to build full API URLs
export const buildApiUrl = (endpoint) => {
  return `${API_BASE_URL}${endpoint}`;
};
