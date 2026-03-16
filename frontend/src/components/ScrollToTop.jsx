import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export const ScrollToTop = () => {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    // Skip auto-scroll if navigating with an anchor (search highlight)
    if (hash) return;
    window.scrollTo(0, 0);
  }, [pathname, hash]);

  return null;
};
