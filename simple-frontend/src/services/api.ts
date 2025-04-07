import axios, { InternalAxiosRequestConfig, AxiosHeaders } from 'axios';

// IMPORTANT: Configuration flags
// const DISABLE_AUTO_REFRESH = false;  // Enable automatic token refresh
// const REDIRECT_ON_AUTH_ERROR = true; // Redirects to login on auth errors
const DEBUG_MODE = true; // Enable detailed logging for debugging
const DEV_MODE = process.env.NODE_ENV === 'development';

// Get the base URL from environment or use default
const baseURL = process.env.REACT_APP_API_URL || 'http://myBackEndUrlOrIP:8000/api';

// Simple API instance without any interceptors initially
const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Log API requests in debug mode
if (DEBUG_MODE) {
  console.log('API configured with baseURL:', api.defaults.baseURL);
}

// Helper to ensure path has leading /api if needed
const ensureApiPath = (path: string): string => {
  // Check if the baseURL already includes /api
  if (baseURL.endsWith('/api')) {
    return path;
  }
  
  // Check if the path already starts with /api
  if (path.startsWith('/api/')) {
    return path;
  } else if (path.startsWith('/')) {
    return `/api${path}`;
  } else {
    return `/api/${path}`;
  }
};

// Check if dev mock is active
const isDevMockActive = (): boolean => {
  return DEV_MODE && localStorage.getItem('authToken') === 'dev-mock-token';
};

// Helper functions for safer storage operations
const setStoredToken = (token: string) => {
  try {
    localStorage.setItem('authToken', token);
    sessionStorage.setItem('authToken', token); // Use both for redundancy
    return true;
  } catch (error) {
    console.error('Error storing auth token:', error);
    return false;
  }
};

const setStoredRefreshToken = (token: string) => {
  try {
    localStorage.setItem('refreshToken', token);
    sessionStorage.setItem('refreshToken', token); // Use both for redundancy
    return true;
  } catch (error) {
    console.error('Error storing refresh token:', error);
    return false;
  }
};

const getStoredToken = () => {
  // Try sessionStorage first (more reliable during refresh cycles)
  let token = sessionStorage.getItem('authToken');
  
  // Fall back to localStorage if not in sessionStorage
  if (!token) {
    token = localStorage.getItem('authToken');
    // If found in localStorage but not sessionStorage, sync back to sessionStorage
    if (token) {
      sessionStorage.setItem('authToken', token);
    }
  }
  
  return token;
};

const getStoredRefreshToken = () => {
  // Same pattern as getStoredToken
  let token = sessionStorage.getItem('refreshToken');
  
  if (!token) {
    token = localStorage.getItem('refreshToken');
    if (token) {
      sessionStorage.setItem('refreshToken', token);
    }
  }
  
  return token;
};

const clearTokens = () => {
  try {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    sessionStorage.removeItem('authToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('user');
    return true;
  } catch (error) {
    console.error('Error clearing tokens:', error);
    return false;
  }
};

// Auth service
export const auth = {
  login: async (email: string, password: string) => {
    if (DEBUG_MODE) {
      console.log('Attempting login for', email);
    }
    try {
      const normalizedUrl = '/token/';
      if (DEBUG_MODE) {
        console.log('Normalized URL:', normalizedUrl);
        console.log('Auth request to', normalizedUrl, { email, password });
      }
      const response = await api.post(normalizedUrl, { email, password });
      if (DEBUG_MODE) {
        console.log('Auth response:', response.status, response.data);
      }
      // Store tokens securely
      if (response.data && response.data.access) {
        setStoredToken(response.data.access);
        if (response.data.refresh) {
          setStoredRefreshToken(response.data.refresh);
        }
        // Save token timestamp for expiry tracking
        localStorage.setItem('tokenTimestamp', Date.now().toString());
        sessionStorage.setItem('tokenTimestamp', Date.now().toString());
      }
      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  refreshToken: async () => {
    try {
      const refreshToken = getStoredRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }
      if (DEBUG_MODE) {
        console.log('Attempting token refresh');
      }
      const response = await api.post('/token/refresh/', { refresh: refreshToken });
      if (DEBUG_MODE) {
        console.log('Refresh response:', response.status, response.data);
      }
      if (response.data && response.data.access) {
        setStoredToken(response.data.access);
        // Update token timestamp
        localStorage.setItem('tokenTimestamp', Date.now().toString());
        sessionStorage.setItem('tokenTimestamp', Date.now().toString());
      }
      return response;
    } catch (error) {
      console.error('Refresh token error:', error);
      // Clear tokens on refresh failure
      clearTokens();
      throw error;
    }
  },

  logout: () => {
    if (DEBUG_MODE) {
      console.log('Logging out, clearing tokens');
    }
    clearTokens();
  },
  
  // Helper to check if token is valid
  isAuthenticated: () => {
    return !!getStoredToken();
  }
};

// Request interceptor
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Ensure URL has the correct /api prefix
    if (config.url && !config.url.startsWith('http')) {
      config.url = ensureApiPath(config.url);
      
      if (DEBUG_MODE) {
        console.log(`Normalized URL: ${config.url}`);
      }
    }
    
    // Skip auth for login and refresh endpoints
    if (config.url?.includes('/token/') || config.url?.includes('/token/refresh/')) {
      if (DEBUG_MODE) {
        console.log(`Auth request to ${config.url}`, config.data);
      }
      return config;
    }
    
    const token = getStoredToken();
    if (token) {
      const headers = new AxiosHeaders(config.headers);
      headers.set('Authorization', `Bearer ${token}`);
      config.headers = headers;
      
      if (DEBUG_MODE) {
        console.log(`Request to ${config.url} with auth token`);
      }
    } else if (DEBUG_MODE) {
      console.warn(`Request to ${config.url} without auth token`);
    }
    return config;
  },
  (error: any) => {
    if (DEBUG_MODE) {
      console.error('Request error:', error);
    }
    return Promise.reject(error);
  }
);

// Add a response interceptor - handles auth errors with clean redirect
api.interceptors.response.use(
  function(response) {
    return response;
  },
  function(error) {
    // Don't use TypeScript features that could cause errors
    if (!error.response || !error.config) {
      return Promise.reject(error);
    }

    if (error.response.status === 401) {
      // Avoid adding properties to the original config
      // Instead, create a simple flag in localStorage
      if (localStorage.getItem('token_refresh_in_progress') === 'true') {
        // Already refreshing, just reject the error
        return Promise.reject(error);
      }

      try {
        // Set flag that we're attempting a refresh
        localStorage.setItem('token_refresh_in_progress', 'true');
        
        // Get refresh token
        var refreshToken = getStoredRefreshToken();
        
        if (!refreshToken) {
          // No refresh token, clear auth and redirect
          auth.logout();
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        // Try to refresh the token
        return api.post('/token/refresh/', { refresh: refreshToken })
          .then(function(response) {
            // Success - store the new token
            var newToken = response.data.access;
            setStoredToken(newToken);
            
            // Clear refresh flag
            localStorage.removeItem('token_refresh_in_progress');
            
            // Create a clean config for the retry
            var newConfig = JSON.parse(JSON.stringify(error.config));
            newConfig.headers.Authorization = 'Bearer ' + newToken;
            
            // Retry the original request
            return axios(newConfig);
          })
          .catch(function(refreshError) {
            // Refresh failed, clear auth and redirect
            localStorage.removeItem('token_refresh_in_progress');
            auth.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          });
      } catch (e) {
        // Something went wrong, clear auth and redirect
        localStorage.removeItem('token_refresh_in_progress');
        auth.logout();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }
    
    // Not a 401 error, just reject it
    return Promise.reject(error);
  }
);

// Export API services
export const device = {
  checkUpdates: () => api.get('/device/updates/check_updates/'),
  getStatus: () => api.get('/device/updates/status/'),
};

export const organizations = {
  list: () => api.get('/organizations/?include_counts=true'),
  get: (id: string) => api.get(`/organizations/${id}/`),
  create: (data: any) => api.post('/organizations/', data),
  update: (id: string, data: any) => api.put(`/organizations/${id}/`, data),
  delete: (id: string) => api.delete(`/organizations/${id}/`, { data: { confirmation: true } }),
  // Add members endpoints
  members: {
    list: (slug: string) => api.get(`/organizations/${slug}/members/`),
    get: (slug: string, id: string) => api.get(`/organizations/${slug}/members/${id}/`),
    create: (slug: string, data: any) => api.post(`/organizations/${slug}/members/`, data),
    update: (slug: string, id: string, data: any) => api.put(`/organizations/${slug}/members/${id}/`, data),
    delete: (slug: string, id: string) => api.delete(`/organizations/${slug}/members/${id}/`)
  }
};

export const networks = {
  list: (organizationId: string) => api.get(`/organizations/${organizationId}/networks/`),
  get: (organizationId: string, id: string) =>
    api.get(`/organizations/${organizationId}/networks/${id}/`),
  create: (organizationId: string, data: any) =>
    api.post(`/organizations/${organizationId}/networks/`, data),
  update: (organizationId: string, id: string, data: any) =>
    api.put(`/organizations/${organizationId}/networks/${id}/`, data),
  delete: (organizationId: string, id: string) =>
    api.delete(`/organizations/${organizationId}/networks/${id}/`),
};

export const nodes = {
  list: (organizationId: string) => api.get(`/organizations/${organizationId}/nodes/`),
  get: (organizationId: string, id: string) =>
    api.get(`/organizations/${organizationId}/nodes/${id}/`),
  create: (organizationId: string, data: any) =>
    api.post(`/organizations/${organizationId}/nodes/`, data),
  update: (organizationId: string, id: string, data: any) =>
    api.put(`/organizations/${organizationId}/nodes/${id}/`, data),
  delete: (organizationId: string, id: string) =>
    api.delete(`/organizations/${organizationId}/nodes/${id}/`),
  checkIn: (organizationId: string, id: string, data: any) =>
    api.post(`/organizations/${organizationId}/nodes/${id}/check_in/`, data),
  generateConfig: (organizationId: string, id: string) =>
    api.post(`/organizations/${organizationId}/nodes/${id}/generate_config/`),
};

export const lighthouses = {
  list: (organizationId?: string) => organizationId 
    ? api.get(`/organizations/${organizationId}/lighthouses/`) 
    : api.get('/lighthouses/'),
  get: (id: string) => api.get(`/lighthouses/${id}/`),
  create: (data: any) => api.post('/lighthouses/', data),
  update: (id: string, data: any) => api.put(`/lighthouses/${id}/`, data),
  delete: (id: string) => api.delete(`/lighthouses/${id}/`),
  checkIn: (id: string, data: any) => api.post(`/lighthouses/${id}/check_in/`, data),
  generateConfig: (id: string) => api.post(`/lighthouses/${id}/generate_config/`),
  getNodes: (id: string) => api.get(`/lighthouses/${id}/nodes/`),
};

export const securityGroups = {
  list: (organizationId: string) => api.get(`/organizations/${organizationId}/security-groups/`),
  get: (organizationId: string, id: string) =>
    api.get(`/organizations/${organizationId}/security-groups/${id}/`),
  create: (organizationId: string, data: any) =>
    api.post(`/organizations/${organizationId}/security-groups/`, data),
  update: (organizationId: string, id: string, data: any) =>
    api.put(`/organizations/${organizationId}/security-groups/${id}/`, data),
  delete: (organizationId: string, id: string) =>
    api.delete(`/organizations/${organizationId}/security-groups/${id}/`),
};

export const certificates = {
  list: (organizationId: string) => api.get(`/organizations/${organizationId}/certificates/`),
  get: (organizationId: string, id: string) =>
    api.get(`/organizations/${organizationId}/certificates/${id}/`),
  create: (organizationId: string, data: any) =>
    api.post(`/organizations/${organizationId}/certificates/`, data),
  update: (organizationId: string, id: string, data: any) =>
    api.put(`/organizations/${organizationId}/certificates/${id}/`, data),
  delete: (organizationId: string, id: string) =>
    api.delete(`/organizations/${organizationId}/certificates/${id}/`),
  renew: (organizationId: string, id: string) =>
    api.post(`/organizations/${organizationId}/certificates/${id}/renew/`),
  revoke: (organizationId: string, id: string) =>
    api.post(`/organizations/${organizationId}/certificates/${id}/revoke/`),
};

// Users API
export const users = {
  list: () => api.get('/users/'),
  get: (id: string) => api.get(`/users/${id}/`),
  create: (data: any) => api.post('/users/', data),
  update: (id: string, data: any) => api.put(`/users/${id}/`, data),
  delete: (id: string) => api.delete(`/users/${id}/`),
};

export default api; 