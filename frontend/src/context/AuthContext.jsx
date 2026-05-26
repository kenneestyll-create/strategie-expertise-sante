import { createContext, useContext, useState, useEffect } from 'react';
import { safeStorage } from '../utils/safeStorage';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(safeStorage.get('admin_token'));
  const [adminName, setAdminName] = useState(safeStorage.get('admin_name'));
  const [isAuthenticated, setIsAuthenticated] = useState(!!token);

  useEffect(() => {
    if (token) {
      safeStorage.set('admin_token', token);
      setIsAuthenticated(true);
    } else {
      safeStorage.remove('admin_token');
      safeStorage.remove('admin_name');
      setIsAuthenticated(false);
    }
  }, [token]);

  const login = (accessToken, name) => {
    setToken(accessToken);
    setAdminName(name);
    safeStorage.set('admin_name', name);
  };

  const logout = () => {
    setToken(null);
    setAdminName(null);
  };

  return (
    <AuthContext.Provider value={{ token, adminName, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
