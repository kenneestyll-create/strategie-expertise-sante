import { useState, useEffect, createContext, useContext } from 'react';
import { useAuth } from '@/context/AuthContext';

const AdminTestContext = createContext({ isAdminMode: false, adminToken: null, setIsAdminMode: () => {} });

export const useAdminTest = () => useContext(AdminTestContext);

export const AdminTestProvider = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [isAdminMode, setIsAdminMode] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) setIsAdminMode(false);
  }, [isAuthenticated]);

  return (
    <AdminTestContext.Provider value={{ isAdminMode, adminToken: isAdminMode ? token : null, setIsAdminMode }}>
      {children}
    </AdminTestContext.Provider>
  );
};
