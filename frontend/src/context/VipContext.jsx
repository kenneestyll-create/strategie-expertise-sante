import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const VipContext = createContext({ isVip: false, vipName: '', vipLogout: () => {}, refreshVip: () => {} });

export const useVip = () => useContext(VipContext);

export const VipProvider = ({ children }) => {
  const [isVip, setIsVip] = useState(false);
  const [vipName, setVipName] = useState('');

  const refreshVip = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/vip/session`, { withCredentials: true });
      if (res.data.active) {
        setIsVip(true);
        setVipName(res.data.name);
      } else {
        setIsVip(false);
        setVipName('');
      }
    } catch {
      setIsVip(false);
      setVipName('');
    }
  }, []);

  useEffect(() => { refreshVip(); }, [refreshVip]);

  const vipLogout = async () => {
    try {
      await axios.post(`${API}/vip/logout`, {}, { withCredentials: true });
    } catch {}
    setIsVip(false);
    setVipName('');
  };

  return (
    <VipContext.Provider value={{ isVip, vipName, vipLogout, refreshVip }}>
      {children}
    </VipContext.Provider>
  );
};
