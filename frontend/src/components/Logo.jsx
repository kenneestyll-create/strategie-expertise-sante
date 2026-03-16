export const LogoShield = ({ size = 44, className = '' }) => {
  const s = size / 44;
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 48" width={44 * s} height={48 * s} className={className} role="img" aria-label="Blason Stratégie & Expertise Santé">
      <defs>
        <linearGradient id="shieldGold" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#D4B85C"/>
          <stop offset="50%" stopColor="#C9A84C"/>
          <stop offset="100%" stopColor="#B8943F"/>
        </linearGradient>
      </defs>
      <path d="M22 2 L40 8 L40 26 C40 38 32 44 22 48 C12 44 4 38 4 26 L4 8 Z" fill="#1a1a1a" stroke="url(#shieldGold)" strokeWidth="1.5"/>
      <line x1="22" y1="10" x2="22" y2="42" stroke="#C9A84C" strokeWidth="0.8" strokeLinecap="round" opacity="0.4"/>
      <text x="13" y="29" fontFamily="'Cormorant Garamond', 'Great Vibes', Georgia, serif" fontStyle="italic" fontSize="16" fontWeight="300" fill="#C9A84C" textAnchor="middle">F</text>
      <text x="31" y="29" fontFamily="'Cormorant Garamond', 'Great Vibes', Georgia, serif" fontStyle="italic" fontSize="16" fontWeight="300" fill="#C9A84C" textAnchor="middle">S</text>
    </svg>
  );
};

export const LogoFull = ({ className = '', textColor = '#1a1a1a' }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 310 48" className={className} role="img" aria-label="Stratégie & Expertise Santé">
    <defs>
      <linearGradient id="logoGold" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#D4B85C"/>
        <stop offset="50%" stopColor="#C9A84C"/>
        <stop offset="100%" stopColor="#B8943F"/>
      </linearGradient>
    </defs>
    {/* Shield */}
    <g transform="translate(2, 2)">
      <path d="M18 2 L33 7 L33 22 C33 32 26 38 18 42 C10 38 3 32 3 22 L3 7 Z" fill="#1a1a1a" stroke="url(#logoGold)" strokeWidth="1.5"/>
      <line x1="18" y1="9" x2="18" y2="36" stroke="#C9A84C" strokeWidth="0.7" strokeLinecap="round" opacity="0.4"/>
      <text x="11" y="24" fontFamily="'Cormorant Garamond', 'Great Vibes', Georgia, serif" fontStyle="italic" fontSize="14" fontWeight="300" fill="#C9A84C" textAnchor="middle">F</text>
      <text x="25" y="24" fontFamily="'Cormorant Garamond', 'Great Vibes', Georgia, serif" fontStyle="italic" fontSize="14" fontWeight="300" fill="#C9A84C" textAnchor="middle">S</text>
    </g>
    {/* Text */}
    <text x="48" y="23" fontFamily="'Playfair Display', 'Cinzel', Georgia, serif" fontSize="16" fontWeight="700" fill={textColor} letterSpacing="0.3">Stratégie &amp; Expertise Santé</text>
    <line x1="48" y1="33" x2="68" y2="33" stroke="url(#logoGold)" strokeWidth="0.6" strokeLinecap="round"/>
    <text x="73" y="37" fontFamily="'Playfair Display', 'Cinzel', Georgia, serif" fontSize="6.5" fill="#C9A84C" letterSpacing="4.2" fontWeight="400">PIONNIER EN FRANCE</text>
    <line x1="224" y1="33" x2="244" y2="33" stroke="url(#logoGold)" strokeWidth="0.6" strokeLinecap="round"/>
  </svg>
);
