import { useState, useEffect, createContext, useContext } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Shield, Eye, EyeOff } from 'lucide-react';

const AdminTestContext = createContext({ isAdminMode: false, adminToken: null });

export const useAdminTest = () => useContext(AdminTestContext);

export const AdminTestProvider = ({ children }) => {
  const { token, isAuthenticated } = useAuth();
  const [isAdminMode, setIsAdminMode] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) setIsAdminMode(false);
  }, [isAuthenticated]);

  return (
    <AdminTestContext.Provider value={{ isAdminMode, adminToken: isAdminMode ? token : null }}>
      {children}
      {isAuthenticated && (
        <div className="fixed bottom-4 left-48 z-[9999]" data-testid="admin-test-toggle-container">
          <button
            onClick={() => setIsAdminMode(prev => !prev)}
            data-testid="admin-test-toggle"
            className={`flex items-center gap-2 px-3 py-2 rounded-full text-xs font-semibold shadow-lg transition-all duration-200 border ${
              isAdminMode
                ? 'bg-amber-500 text-amber-950 border-amber-600 hover:bg-amber-400'
                : 'bg-zinc-800 text-zinc-300 border-zinc-600 hover:bg-zinc-700'
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            {isAdminMode ? (
              <><EyeOff className="w-3 h-3" /> Mode Admin</>
            ) : (
              <><Eye className="w-3 h-3" /> Mode Client</>
            )}
          </button>
        </div>
      )}
    </AdminTestContext.Provider>
  );
};
