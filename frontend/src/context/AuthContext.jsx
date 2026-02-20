import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('admin_token'));
  const [adminName, setAdminName] = useState(localStorage.getItem('admin_name'));
  const [isAuthenticated, setIsAuthenticated] = useState(!!token);

  useEffect(() => {
    if (token) {
      localStorage.setItem('admin_token', token);
      setIsAuthenticated(true);
    } else {
      localStorage.removeItem('admin_token');
      localStorage.removeItem('admin_name');
      setIsAuthenticated(false);
    }
  }, [token]);

  const login = (accessToken, name) => {
    setToken(accessToken);
    setAdminName(name);
    localStorage.setItem('admin_name', name);
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
