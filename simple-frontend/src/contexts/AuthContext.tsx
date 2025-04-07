import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { auth, users } from '../services/api';

// Authentication control flags
const DEBUG_MODE = true; // Enable debug logging

interface User {
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
  refreshAuth: () => Promise<boolean>;
  checkAuthStatus: () => Promise<boolean>;
}

// Helper functions for localStorage to handle errors
const safeGetItem = (key: string): string | null => {
  try {
    return localStorage.getItem(key);
  } catch (error) {
    console.error(`Error getting ${key} from localStorage:`, error);
    return null;
  }
};

const safeSetItem = (key: string, value: string): boolean => {
  try {
    localStorage.setItem(key, value);
    return true;
  } catch (error) {
    console.error(`Error setting ${key} in localStorage:`, error);
    return false;
  }
};

const safeRemoveItem = (key: string): boolean => {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error(`Error removing ${key} from localStorage:`, error);
    return false;
  }
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const storedUser = safeGetItem('user');
      return storedUser ? JSON.parse(storedUser) : null;
    } catch (error) {
      console.error('Error parsing stored user:', error);
      return null;
    }
  });
  
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return !!safeGetItem('authToken');
  });
  
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check authentication status - can be called from anywhere
  const checkAuthStatus = useCallback(async (): Promise<boolean> => {
    try {
      const token = safeGetItem('authToken');
      const refreshToken = safeGetItem('refreshToken');
      
      if (DEBUG_MODE) {
        console.log('Checking auth status:', {
          hasToken: !!token,
          hasRefreshToken: !!refreshToken,
          tokenLength: token?.length,
          refreshTokenLength: refreshToken?.length,
          timeChecked: new Date().toISOString()
        });
      }

      if (!token) {
        if (DEBUG_MODE) {
          console.log('No auth token found');
        }
        setIsAuthenticated(false);
        setUser(null);
        setIsLoading(false);
        return false;
      }

      try {
        if (DEBUG_MODE) {
          console.log('Attempting to validate token');
        }
        // Try to access a protected endpoint to validate the token
        const userResponse = await users.list();
        if (userResponse && userResponse.data && userResponse.data.length > 0) {
          const userData = userResponse.data[0];
          const newUser = {
            email: userData.email || 'user@example.com',
            name: userData.name || 'User'
          };
          setUser(newUser);
          safeSetItem('user', JSON.stringify(newUser));
          setIsAuthenticated(true);
          if (DEBUG_MODE) {
            console.log('Token validation successful');
          }
          setIsLoading(false);
          return true;
        } else {
          // Empty response means no users, but token was valid
          const newUser = {
            email: 'user@example.com',
            name: 'User'
          };
          setUser(newUser);
          safeSetItem('user', JSON.stringify(newUser));
          setIsAuthenticated(true);
          if (DEBUG_MODE) {
            console.log('Token validation successful (empty response)');
          }
          setIsLoading(false);
          return true;
        }
      } catch (error) {
        console.log('Auth validation failed:', error);
        // Only clear tokens if refresh fails
        try {
          if (refreshToken && DEBUG_MODE) {
            console.log('Attempting token refresh');
          }
          
          if (!refreshToken) {
            throw new Error('No refresh token available');
          }
          
          await auth.refreshToken();
          setIsAuthenticated(true);
          if (DEBUG_MODE) {
            console.log('Token refresh successful');
          }
          setIsLoading(false);
          return true;
        } catch (refreshError) {
          console.log('Token refresh failed:', refreshError);
          safeRemoveItem('authToken');
          safeRemoveItem('refreshToken');
          safeRemoveItem('user');
          setIsAuthenticated(false);
          setUser(null);
          setIsLoading(false);
          return false;
        }
      }
    } catch (error) {
      console.error('Error in checkAuth:', error);
      setIsLoading(false);
      return false;
    }
  }, []);

  // Check authentication status on initial load
  useEffect(() => {
    checkAuthStatus();
    
    // Set up storage event listener to sync auth state across tabs
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === 'authToken') {
        // Token added or removed
        const hasToken = !!event.newValue;
        setIsAuthenticated(hasToken);
        if (!hasToken) {
          setUser(null);
        }
      } else if (event.key === 'user') {
        // User data changed
        try {
          const userData = event.newValue ? JSON.parse(event.newValue) : null;
          setUser(userData);
        } catch (error) {
          console.error('Error parsing user data from storage event:', error);
        }
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Check auth status periodically to handle token expiration
    const authCheckInterval = setInterval(() => {
      checkAuthStatus();
    }, 60000); // Check every minute
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(authCheckInterval);
    };
  }, [checkAuthStatus]);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      if (DEBUG_MODE) {
        console.log('Attempting login for:', email);
      }
      const response = await auth.login(email, password);
      
      // Store tokens
      if (response.data?.access) {
        safeSetItem('authToken', response.data.access);
        if (response.data.refresh) {
          safeSetItem('refreshToken', response.data.refresh);
        }
        
        // Store user data
        const newUser = {
          email,
          name: 'User' // This should come from the backend
        };
        setUser(newUser);
        safeSetItem('user', JSON.stringify(newUser));
        
        if (DEBUG_MODE) {
          console.log('Login successful, tokens stored:', {
            accessTokenLength: response.data.access.length,
            refreshTokenLength: response.data.refresh.length
          });
        }
        
        setIsAuthenticated(true);
      } else {
        throw new Error('Login response missing access token');
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    if (DEBUG_MODE) {
      console.log('Logging out, clearing tokens');
    }
    safeRemoveItem('authToken');
    safeRemoveItem('refreshToken');
    safeRemoveItem('user');
    setUser(null);
    setIsAuthenticated(false);
  };

  // Manual refresh function that can be called explicitly when needed
  const refreshAuth = async (): Promise<boolean> => {
    try {
      setIsLoading(true);
      if (DEBUG_MODE) {
        console.log('Manual token refresh attempt');
      }
      await auth.refreshToken();
      setIsAuthenticated(true);
      if (DEBUG_MODE) {
        console.log('Manual token refresh successful');
      }
      return true;
    } catch (error) {
      console.error('Auth refresh failed:', error);
      setIsAuthenticated(false);
      setUser(null);
      safeRemoveItem('authToken');
      safeRemoveItem('refreshToken');
      safeRemoveItem('user');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const contextValue: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated,
    isLoading,
    refreshAuth,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 