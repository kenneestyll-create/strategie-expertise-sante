import { createContext, useContext, useState, useEffect } from 'react';

const ForumAuthContext = createContext(null);

export const ForumAuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('forum_token'));
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('forum_user');
    return stored ? JSON.parse(stored) : null;
  });
  const [isAuthenticated, setIsAuthenticated] = useState(!!token);

  useEffect(() => {
    if (token && user) {
      localStorage.setItem('forum_token', token);
      localStorage.setItem('forum_user', JSON.stringify(user));
      setIsAuthenticated(true);
    } else {
      localStorage.removeItem('forum_token');
      localStorage.removeItem('forum_user');
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
