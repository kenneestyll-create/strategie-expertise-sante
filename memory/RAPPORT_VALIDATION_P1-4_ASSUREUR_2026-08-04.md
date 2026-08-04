# Rapport de validation preview — /expertise-medicale/assureur (P1-4)
Date : 2026-08-04 — Statut : VALIDÉ EN PREVIEW, prêt pour déploiement production

## 1. SEO
- Title : "Expertise médicale assureur : stratégie, préparation, recours | Stratégie & Expertise Santé" (V1 validée par l'utilisateur)
- Meta description : 150 caractères, orientée intention + CTR ("Convoqué à une expertise médicale par votre assureur ? Pièges à connaître, préparation en 5 étapes, contestation des conclusions — le guide stratégique.")
- H1 unique : "Expertise médicale demandée par votre assureur : la stratégie complète"
- 8 H2 + H3 hiérarchisés (pourquoi / 3 pièges / préparation 5 étapes / 3 voies de contestation / cas concret / FAQ / CTA / maillage)
- Robots : index, follow — Canonical : https://strategie-expertise-sante.fr/expertise-medicale/assureur ✓
- Schemas injectés et vérifiés dans le DOM : FAQPage (5 Q/R), BreadcrumbList (3 niveaux), Article (+ ProfessionalService et WebSite globaux)
- Sitemap : entrée présente, priority 0.7 ✓
- Volume : ~1 455 mots dans <main>
- Cannibalisation : intentions distinctes (page fille = longue traîne "assureur", pilier = requête générique multi-facettes). Chevauchement résiduel temporaire avec la section "Volet assureur" du pilier (H2 quasi identique) — résolu à l'étape suivante (réduction du pilier après indexation GSC, conformément au plan Option A).

## 2. Contenu
- Intention "expertise médicale assureur" couverte : mission de l'expert, définitions contractuelles vs sécurité sociale, consolidation prématurée, barème AIPP vs Concours Médical, imputabilité/état antérieur, dires contradictoires, contre-expertise amiable, expertise judiciaire art. 145 CPC, prescription biennale L.114-1/L.114-2.
- Exactitude juridique vérifiée : articles cités corrects, délai de 2 ans + actes interruptifs exacts, distinction amiable/judiciaire correcte.
- Disclaimer YMYL : présent en bas de page ("ni un avis médical ni un avis juridique") + disclaimer global footer ✓
- Équilibre info/conversion : 90 % informationnel, 1 CTA principal Dossier Express en fin de page + 4 cartes ressources.

## 3. Maillage
- Sortants (6) : /expertise-medicale (breadcrumb + carte pilier), /calculatrice-ipp (x2), /protection-juridique (x2), /dossier-express (CTA), /guide/expertise-medicale-defavorable-recours
- Entrants : 0 pour l'instant — VOULU (Option A : le lien depuis le pilier sera ajouté lors de la réduction du "Volet assureur", après indexation). Découverte via sitemap uniquement → recommander une demande d'indexation manuelle dans GSC après déploiement.
- CTA Dossier Express : "Faire analyser mon rapport d'expertise" ✓

## 4. UX
- Mobile 390×844 : aucun débordement horizontal, lisibilité OK, breadcrumb wrap correct
- Desktop 1920 : rendu propre, sections alternées bg-secondary/bg-card, aucune régression header/footer
- data-testid présents sur toutes les sections

## Prochaines étapes
1. Utilisateur : déploiement en production
2. Utilisateur : demande d'indexation manuelle GSC (URL Inspection > Request Indexing)
3. Après confirmation d'indexation : réduction section "Volet assureur" du pilier (~150-200 mots + lien vers la page fille)
