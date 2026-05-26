import { useState, useEffect, createContext, useContext } from 'react';
import { useAuth } from '@/context/AuthContext';
import { safeSessionStorage } from '../utils/safeStorage';

const AdminTestContext = createContext({ isAdminMode: false, adminToken: null, setIsAdminMode: () => {} });

export const useAdminTest = () => useContext(AdminTestContext);

export const AdminTestProvider = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [isAdminMode, setIsAdminMode] = useState(() => {
    return safeSessionStorage.get('admin_test_mode') === 'true';
  });

  useEffect(() => {
    if (!isAuthenticated) {
      setIsAdminMode(false);
      safeSessionStorage.remove('admin_test_mode');
    }
  }, [isAuthenticated]);

  useEffect(() => {
    safeSessionStorage.set('admin_test_mode', isAdminMode ? 'true' : 'false');
  }, [isAdminMode]);

  return (
    <AdminTestContext.Provider value={{ isAdminMode, adminToken: isAdminMode ? token : null, setIsAdminMode }}>
      {children}
    </AdminTestContext.Provider>
  );
};
