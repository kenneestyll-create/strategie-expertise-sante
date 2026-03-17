import { Helmet } from 'react-helmet-async';

const SITE_NAME = 'Stratégie & Expertise Santé';
const BASE_URL = 'https://secure-payment-flow-5.preview.emergentagent.com';

export const SEO = ({ title, description, path = '', noindex = false }) => {
  const fullTitle = title ? `${title} | ${SITE_NAME}` : `${SITE_NAME} — Conseil en maladie professionnelle et AT/MP`;
  const fullUrl = `${BASE_URL}${path}`;
  const desc = description || "Accompagnement humain expert en maladie professionnelle, accident du travail, MDPH et protection juridique. Outils d'aide à l'analyse, calculatrices et ressources gratuites.";

  return (
    <Helmet
      title={fullTitle}
      meta={[
        { name: 'description', content: desc },
        ...(noindex ? [{ name: 'robots', content: 'noindex, nofollow' }] : []),
        { property: 'og:title', content: fullTitle },
        { property: 'og:description', content: desc },
        { property: 'og:url', content: fullUrl },
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: SITE_NAME },
        { property: 'og:locale', content: 'fr_FR' },
        { name: 'twitter:card', content: 'summary' },
        { name: 'twitter:title', content: fullTitle },
        { name: 'twitter:description', content: desc },
      ]}
      link={[{ rel: 'canonical', href: fullUrl }]}
    />
  );
};
