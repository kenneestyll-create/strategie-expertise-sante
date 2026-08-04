# RAPPORT LOT A — REPOSITIONNEMENT SÉMANTIQUE /dossier-express (04/08/2026)
Variante 1 validée par l'utilisateur (title + H1), meta orientée valeur du service.
Fichier modifié : `frontend/src/pages/DossierExpressPage.jsx` uniquement. Zéro changement de design, zéro impact tunnel.

## LIVRÉ
1. **Title** : « Analyse de dossier maladie professionnelle — rapport sous 2 h » (+ suffixe marque auto)
2. **Meta** : « Faites analyser votre dossier maladie professionnelle ou accident du travail : rapport personnalisé sous 2 h, jurisprudences et barèmes croisés — 97 €. »
3. **H1** : « Faites analyser votre dossier / accident du travail ou maladie professionnelle » (span ambre conservé) + sous-titre héro portant la promesse « rapport complet et personnalisé sous 2 h »
4. **H2 requalifiés** (design intact) : « Ce que contient votre rapport d'analyse de dossier » · « Quels dossiers analysons-nous ? CPAM, MDPH, assurance, expertise » · « Questions fréquentes sur l'analyse de dossier »
5. **Contenu SEO enrichi** (~200 → ~540 mots) : H2 « Faire analyser son dossier : maladie professionnelle, accident du travail, MDPH, assurance » + 4 H3 par intention :
   - « Analyse de dossier maladie professionnelle et accident du travail » (cluster A)
   - « Faire analyser un rapport d'expertise médicale » (cluster B)
   - « Aide pour un recours MDPH ou un litige assurance » (clusters C/E)
   - « Une analyse avant d'engager vos démarches » (timing + disclaimer YMYL conservé)
6. **FAQ** : 3 → 6 questions (+ « Combien coûte une analyse de dossier maladie professionnelle ? », « Puis-je faire analyser un rapport d'expertise médicale ? », « Est-ce utile avant un recours CPAM ou MDPH ? ») — schema FAQPage automatique
7. **Schema Service** avec Offer 97 € EUR (injecté/nettoyé avec le schema FAQ)
8. **Bloc « Ressources utiles »** (fin du cul-de-sac sortant) : 4 liens contextuels vérifiés → /calculatrice-ipp, /guide/expertise-medicale-defavorable-recours, /guide/refus-maladie-professionnelle-cpam-recours, /guide/refus-mdph-aah-que-faire

## TESTS (tous PASS)
- Title/meta/H1 rendus conformes (mesure Playwright)
- Schemas présents : ProfessionalService, WebSite, **FAQPage, Service** (4 JSON-LD)
- 4 liens ressources → pages réelles (aucun 404, contenus 8-10k chars)
- **Tunnel intact** : CTA « Analyser mon dossier — 97 € » → formulaire OK
- Mobile 390×844 : 0 px de débordement, héro lisible — Desktop : rendu propre (captures)

## SUIVI (Lot C, à la charge du déploiement)
- Baseline GSC de la page à relever AVANT déploiement, puis demander l'indexation de l'URL (inspection GSC) après mise en prod. KPI : J+28 impressions non-marque > 100 ; J+90 top 20 sur 2-3 requêtes clusters A-C.
- Lot B (ancres des 7 DossierExpressCTA) : NON lancé — attendra validation + premiers résultats, conformément à l'ordre.
