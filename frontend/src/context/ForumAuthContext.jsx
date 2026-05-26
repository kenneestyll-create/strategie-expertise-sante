import { createContext, useContext, useState, useEffect } from 'react';
import { safeStorage } from '../utils/safeStorage';

const ForumAuthContext = createContext(null);

export const ForumAuthProvider = ({ children }) => {
  const [token, setToken] = useState(safeStorage.get('forum_token'));
  const [user, setUser] = useState(() => safeStorage.getJSON('forum_user', null));
  const [isAuthenticated, setIsAuthenticated] = useState(!!token);

  useEffect(() => {
    if (token && user) {
      safeStorage.set('forum_token', token);
      safeStorage.setJSON('forum_user', user);
      setIsAuthenticated(true);
    } else {
      safeStorage.remove('forum_token');
      safeStorage.remove('forum_user');
      setIsAuthenticated(false);
    }
  }, [token, user]);

  const login = (accessToken, userData) => {
    setToken(accessToken);
    setUser(userData);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  return (
    <ForumAuthContext.Provider value={{ token, user, isAuthenticated, login, logout }}>
      {children}
    </ForumAuthContext.Provider>
  );
};

export const useForumAuth = () => {
  const context = useContext(ForumAuthContext);
  if (!context) {
    throw new Error('useForumAuth must be used within a ForumAuthProvider');
  }
  return context;
};
