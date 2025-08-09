import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  role: 'employee' | 'manager' | 'hr' | 'admin';
  department: string;
  employeeId: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  hasRole: (roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Configure axios defaults
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  // Check authentication status on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setIsLoading(false);
        return;
      }

      // In a real app, verify token with backend
      // For demo, we'll simulate a user
      const demoUser: User = {
        id: 1,
        email: 'demo@peerpulse.com',
        firstName: 'Demo',
        lastName: 'User',
        role: 'manager',
        department: 'Engineering',
        employeeId: 'EMP001'
      };

      setUser(demoUser);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('authToken');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);

      // For demo purposes, accept any email/password
      // In production, this would call your API
      if (email && password) {
        const demoUser: User = {
          id: 1,
          email: email,
          firstName: email.split('@')[0].split('.')[0] || 'Demo',
          lastName: email.split('@')[0].split('.')[1] || 'User',
          role: email.includes('admin') ? 'admin' : 
                email.includes('manager') ? 'manager' :
                email.includes('hr') ? 'hr' : 'employee',
          department: 'Engineering',
          employeeId: 'EMP001'
        };

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));

        const fakeToken = btoa(JSON.stringify({ userId: demoUser.id, email: demoUser.email }));
        localStorage.setItem('authToken', fakeToken);
        axios.defaults.headers.common['Authorization'] = `Bearer ${fakeToken}`;
        
        setUser(demoUser);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const hasRole = (roles: string[]): boolean => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    hasRole,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
