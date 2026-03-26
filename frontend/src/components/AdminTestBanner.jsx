import { useState, useEffect, createContext, useContext } from 'react';
import { useAuth } from '@/context/AuthContext';

const AdminTestContext = createContext({ isAdminMode: false, adminToken: null, setIsAdminMode: () => {} });

export const useAdminTest = () => useContext(AdminTestContext);

export const AdminTestProvider = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [isAdminMode, setIsAdminMode] = useState(() => {
    return sessionStorage.getItem('admin_test_mode') === 'true';
  });

  useEffect(() => {
    if (!isAuthenticated) {
      setIsAdminMode(false);
      sessionStorage.removeItem('admin_test_mode');
    }
  }, [isAuthenticated]);

  useEffect(() => {
    sessionStorage.setItem('admin_test_mode', isAdminMode ? 'true' : 'false');
  }, [isAdminMode]);

  return (
    <AdminTestContext.Provider value={{ isAdminMode, adminToken: isAdminMode ? token : null, setIsAdminMode }}>
      {children}
    </AdminTestContext.Provider>
  );
};
