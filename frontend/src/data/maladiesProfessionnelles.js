export const MALADIES_PRO_TABLEAUX = [
  { numero: "25", titre: "Affections consécutives à l'inhalation de poussières minérales renfermant de la silice", delai: "35 ans", travaux: "Travaux exposant à la silice libre (mines, carrières, fonderies, BTP, céramique)" },
  { numero: "30", titre: "Affections professionnelles consécutives à l'inhalation de poussières d'amiante", delai: "40 ans", travaux: "Fabrication, transformation d'amiante, flocage, calorifugeage, travaux d'isolation" },
  { numero: "30 bis", titre: "Cancer broncho-pulmonaire provoqué par l'inhalation de poussières d'amiante", delai: "40 ans", travaux: "Tous travaux exposant à l'amiante" },
  { numero: "42", titre: "Atteinte auditive provoquée par les bruits lésionnels", delai: "1 an", travaux: "Travaux exposant aux bruits (marteaux-piqueurs, moteurs, machines industrielles)" },
  { numero: "57", titre: "Affections périarticulaires provoquées par certains gestes et postures (TMS)", delai: "Variable selon localisation", travaux: "Travaux comportant des mouvements répétitifs, postures contraignantes" },
  { numero: "57A", titre: "TMS — Épaule (tendinopathie de la coiffe des rotateurs)", delai: "6 mois à 1 an", travaux: "Mouvements répétés ou forcés de l'épaule, travail bras au-dessus de l'horizontale" },
  { numero: "57B", titre: "TMS — Coude (épicondylite, épitrochléite)", delai: "6 mois à 1 an", travaux: "Mouvements répétés de préhension ou d'extension du poignet, vissage, utilisation d'outils" },
  { numero: "57C", titre: "TMS — Poignet et main (syndrome du canal carpien)", delai: "6 mois à 1 an", travaux: "Mouvements répétés de flexion/extension du poignet, appui prolongé, vibrations" },
  { numero: "57D", titre: "TMS — Genou (hygroma, tendinite)", delai: "6 mois à 1 an", travaux: "Travaux en position agenouillée prolongée, accroupissement répété" },
  { numero: "57E", titre: "TMS — Cheville et pied (tendinite d'Achille)", delai: "6 mois à 1 an", travaux: "Mouvements répétés du pied, marche prolongée, terrain accidenté" },
  { numero: "69", titre: "Affections provoquées par les vibrations et chocs transmis par certaines machines-outils", delai: "5 ans", travaux: "Utilisation de machines vibrantes (marteaux-piqueurs, tronçonneuses, meuleuses)" },
  { numero: "79", titre: "Lésions chroniques du ménisque", delai: "2 ans", travaux: "Travaux en position agenouillée ou accroupie prolongée (carreleurs, plombiers)" },
  { numero: "97", titre: "Affections chroniques du rachis lombaire (lombalgie, sciatique)", delai: "6 mois", travaux: "Manutention manuelle de charges lourdes, vibrations du corps entier, postures pénibles" },
  { numero: "98", titre: "Affections chroniques du rachis lombaire (hernie discale)", delai: "6 mois", travaux: "Manutention manuelle habituelle de charges lourdes" },
  { numero: "66", titre: "Rhinites et asthmes professionnels", delai: "7 jours à 1 an", travaux: "Exposition à des agents allergisants (farine, bois, latex, produits chimiques)" },
  { numero: "47", titre: "Affections professionnelles provoquées par les bois", delai: "Variable", travaux: "Travaux de menuiserie, scierie, ébénisterie exposant aux poussières de bois" },
  { numero: "36", titre: "Affections provoquées par les huiles et graisses d'origine minérale ou de synthèse", delai: "7 jours à 6 mois", travaux: "Usinage des métaux, mécanique, entretien de machines" },
  { numero: "4", titre: "Hémopathies provoquées par le benzène et ses homologues", delai: "30 ans", travaux: "Industries chimiques, pétrochimie, imprimerie, collage" },
  { numero: "6", titre: "Affections provoquées par les rayonnements ionisants", delai: "50 ans", travaux: "Industries nucléaires, radiologie médicale, recherche" },
  { numero: "16 bis", titre: "Affections cancéreuses provoquées par les goudrons de houille", delai: "20 ans", travaux: "Travaux routiers, étanchéité, ramonage" },
];

export const TMS_LOCALISATION = [
  { zone: "Épaule", tableau: "57A", pathologies: ["Tendinopathie de la coiffe des rotateurs", "Capsulite rétractile"], delai: "6 mois à 1 an" },
  { zone: "Coude", tableau: "57B", pathologies: ["Épicondylite latérale (tennis elbow)", "Épitrochléite (golf elbow)", "Hygroma du coude"], delai: "6 mois à 1 an" },
  { zone: "Poignet / Main", tableau: "57C", pathologies: ["Syndrome du canal carpien", "Tendinite des fléchisseurs", "Syndrome de De Quervain"], delai: "6 mois à 1 an" },
  { zone: "Genou", tableau: "57D", pathologies: ["Hygroma aigu ou chronique", "Tendinite sous-quadricipitale", "Syndrome de la bandelette ilio-tibiale"], delai: "6 mois à 1 an" },
  { zone: "Cheville / Pied", tableau: "57E", pathologies: ["Tendinite d'Achille"], delai: "6 mois à 1 an" },
];

export const IPP_EXEMPLES = [
  { taux: 3, description: "Légère limitation de la mobilité d'un doigt", indemnisation: "Capital forfaitaire : environ 1 111 €", consequences: "Versement unique, pas de rente. Pas de majoration pour tierce personne." },
  { taux: 5, description: "Perte partielle de l'audition d'une oreille", indemnisation: "Capital forfaitaire : environ 2 222 €", consequences: "Versement unique. Possibilité de contester si le taux semble sous-évalué." },
  { taux: 10, description: "Syndrome du canal carpien opéré avec séquelles modérées", indemnisation: "Rente viagère trimestrielle basée sur le salaire", consequences: "Passage au régime de la rente. Taux utile = 5%. Droit à majoration pour accident de trajet." },
  { taux: 15, description: "Lombalgie chronique avec limitation fonctionnelle", indemnisation: "Rente viagère (ex: ~1 875 €/an pour salaire de 25 000 €)", consequences: "Taux utile = 7,5%. Protection contre le licenciement renforcée." },
  { taux: 25, description: "Hernie discale opérée avec séquelles importantes", indemnisation: "Rente viagère (ex: ~3 125 €/an pour salaire de 25 000 €)", consequences: "Taux utile = 12,5%. Possibilité de demander la RQTH." },
  { taux: 40, description: "Amputation partielle d'un membre, surdité bilatérale importante", indemnisation: "Rente viagère (ex: ~5 000 €/an pour salaire de 25 000 €)", consequences: "Taux utile = 20%. Droit à l'AAH possible si conditions remplies." },
  { taux: 50, description: "Amputation d'une main, perte fonctionnelle majeure", indemnisation: "Rente viagère (ex: ~6 250 €/an pour salaire de 25 000 €)", consequences: "Taux utile = 25%. Seuil où le calcul de la rente change (majoration au-delà de 50%)." },
  { taux: 67, description: "Incapacité majeure, perte d'autonomie significative", indemnisation: "Rente majorée (ex: ~12 500 €/an pour salaire de 25 000 €)", consequences: "Taux utile = 50,5%. Possible majoration pour tierce personne." },
  { taux: 80, description: "Handicap très lourd, dépendance pour les actes quotidiens", indemnisation: "Rente importante + majoration tierce personne possible", consequences: "Taux utile = 70%. Droit automatique à l'AAH sans limite de durée." },
  { taux: 100, description: "Incapacité totale (tétraplégie, cécité complète)", indemnisation: "Rente = salaire de référence + majoration tierce personne", consequences: "Taux utile = 100%. Rente égale au salaire. Majoration pour tierce personne systématique." },
];
