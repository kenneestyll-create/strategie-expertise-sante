import { Link, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Shield, Scale, AlertTriangle, ShoppingCart } from 'lucide-react';
import { SEO } from '@/components/SEO';

export const MentionsLegalesPage = () => {
  const [searchParams] = useSearchParams();
  const defaultTab = searchParams.get('tab') || 'mentions';

  return (
    <main className="page-transition pt-20">
      <SEO title="Mentions légales, CGV et politique de confidentialité" description="Consultez les mentions légales, conditions générales de vente (CGV), politique de confidentialité et informations RGPD de Stratégie & Expertise Santé." path="/mentions-legales" />
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-4xl mx-auto">
          <span className="text-sm font-medium text-accent uppercase tracking-wider">Informations légales</span>
          <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="mentions-legales-title">
            Informations juridiques
          </h1>
          <p className="text-lg text-muted-foreground">
            Retrouvez ici toutes les informations légales, conditions générales de vente et d'utilisation,
            ainsi que notre politique de confidentialité.
          </p>
        </div>
      </section>

      {/* Content */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto">
          <Tabs defaultValue={defaultTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4 h-auto gap-1 mb-8">
              <TabsTrigger value="mentions" className="gap-2" data-testid="tab-mentions">
                <FileText className="w-4 h-4" />
                <span className="hidden sm:inline">Mentions légales</span>
                <span className="sm:hidden">Mentions</span>
              </TabsTrigger>
              <TabsTrigger value="cgv" className="gap-2" data-testid="tab-cgv">
                <ShoppingCart className="w-4 h-4" />
                CGV
              </TabsTrigger>
              <TabsTrigger value="cgu" className="gap-2" data-testid="tab-cgu">
                <Scale className="w-4 h-4" />
                CGU
              </TabsTrigger>
              <TabsTrigger value="confidentialite" className="gap-2" data-testid="tab-confidentialite">
                <Shield className="w-4 h-4" />
                <span className="hidden sm:inline">Confidentialité</span>
                <span className="sm:hidden">RGPD</span>
              </TabsTrigger>
            </TabsList>

            {/* ═══════════════════ MENTIONS LÉGALES ═══════════════════ */}
            <TabsContent value="mentions" className="space-y-6">
              <Card>
                <CardHeader><CardTitle>Identité de l'exploitant</CardTitle></CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                  <p>
                    <strong className="text-foreground">Stratégie & Expertise Santé</strong> est un service
                    édité et exploité par <strong className="text-foreground">KAPSULES KORPORATION</strong>.
                  </p>
                  <div className="space-y-1.5 text-sm">
                    <p><strong className="text-foreground">Marque / enseigne :</strong> Stratégie & Expertise Santé</p>
                    <p><strong className="text-foreground">Exploitant :</strong> KAPSULES KORPORATION</p>
                    <p><strong className="text-foreground">Forme juridique :</strong> Entreprise individuelle</p>
                    <p><strong className="text-foreground">RCS :</strong> 824 339 584 R.C.S. Chartres</p>
                    <p><strong className="text-foreground">Date d'immatriculation :</strong> 15/12/2016</p>
                    <p><strong className="text-foreground">Adresse du siège :</strong> 4 Rue de la Corne du Parc, 28310 Janville-en-Beauce</p>
                  </div>
                  <p>
                    <strong className="text-foreground">Contact :</strong><br />
                    Email : contact@strategie-expertise-sante.fr<br />
                    Téléphone : 07 59 93 60 67
                  </p>
                  <p>
                    <strong className="text-foreground">Responsable de la publication :</strong><br />
                    KAPSULES KORPORATION
                  </p>
                  <p className="text-xs text-muted-foreground/60">
                    N° TVA intracommunautaire : FR78824339584
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Hébergement</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground">
                  <p>
                    Ce site est hébergé par :<br />
                    <strong className="text-foreground">Vercel Inc.</strong><br />
                    340 S Lemon Ave #4133, Walnut, CA 91789, États-Unis<br />
                    <a href="https://vercel.com" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">https://vercel.com</a>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Activité déclarée</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-2 text-sm">
                  <p>
                    Conseil, accompagnement et assistance non réglementée pour les victimes de maladies professionnelles,
                    accidents du travail, litiges assurantiels, expertises médicales et démarches MDPH,
                    ainsi que création de contenus numériques informatifs.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Propriété intellectuelle</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    L'ensemble du contenu de ce site (textes, images, vidéos, logos, graphismes)
                    est la propriété exclusive de Stratégie & Expertise Santé, sauf mention contraire.
                  </p>
                  <p>
                    Toute reproduction, représentation, diffusion, adaptation, extraction, réutilisation,
                    exploitation ou transmission, totale ou partielle, sur quelque support que ce soit,
                    sans autorisation écrite préalable, est strictement interdite.
                  </p>
                  <p>
                    Sont également protégés les cadres méthodologiques, logiques d'analyse, structures
                    de restitution, mécanismes d'évaluation, architectures de lecture dossier, ainsi que
                    les contenus à forte valeur ajoutée développés dans le cadre des services proposés
                    par Stratégie & Expertise Santé.
                  </p>
                  <p className="font-medium text-foreground/80">
                    Toute utilisation non autorisée est susceptible d'engager la responsabilité civile
                    et/ou pénale de son auteur.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Limitation de responsabilité</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Les informations fournies sur ce site le sont à titre indicatif et ne
                    constituent en aucun cas des conseils médicaux ou juridiques.
                  </p>
                  <p>
                    Stratégie & Expertise Santé ne peut être tenu responsable des décisions prises sur la
                    base des informations contenues sur ce site. Pour toute question médicale
                    ou juridique, veuillez consulter les professionnels compétents.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            {/* ═══════════════════ CGV ═══════════════════ */}
            <TabsContent value="cgv" className="space-y-6" data-testid="cgv-content">
              <Card className="border-accent/30 bg-accent/5">
                <CardContent className="p-6">
                  <h3 className="font-semibold text-lg mb-1">Conditions Générales de Vente</h3>
                  <p className="text-sm text-muted-foreground">
                    Applicables à toutes les prestations payantes proposées par Stratégie & Expertise Santé.
                    En vigueur à compter du 11 avril 2026. Toute commande implique l'acceptation sans réserve des présentes CGV.
                  </p>
                </CardContent>
              </Card>

              {/* Article 1 — Identification */}
              <Card>
                <CardHeader><CardTitle>Article 1 — Identification du prestataire</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-3 text-sm">
                  <p><strong className="text-foreground">Nom commercial :</strong> Stratégie & Expertise Santé</p>
                  <p><strong className="text-foreground">Exploitant :</strong> KAPSULES KORPORATION — Entreprise individuelle</p>
                  <p><strong className="text-foreground">RCS :</strong> 824 339 584 R.C.S. Chartres</p>
                  <p><strong className="text-foreground">TVA intracommunautaire :</strong> FR78824339584</p>
                  <p><strong className="text-foreground">Siège :</strong> 4 Rue de la Corne du Parc, 28310 Janville-en-Beauce</p>
                  <p><strong className="text-foreground">Email :</strong> contact@strategie-expertise-sante.fr</p>
                  <p><strong className="text-foreground">Téléphone :</strong> 07 59 93 60 67</p>
                  <p><strong className="text-foreground">Responsable de la publication :</strong> KAPSULES KORPORATION</p>
                </CardContent>
              </Card>

              {/* Article 2 — Description des services */}
              <Card>
                <CardHeader><CardTitle>Article 2 — Description des services</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4 text-sm">
                  <p>Stratégie & Expertise Santé propose les prestations suivantes :</p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li><strong className="text-foreground">Analyse stratégique IA (StratégiIA) :</strong> analyse documentaire assistée par intelligence artificielle de dossiers liés aux maladies professionnelles, accidents du travail, MDPH, expertises médicales et litiges assurantiels.</li>
                    <li><strong className="text-foreground">Dossier Express IA :</strong> analyse accélérée et synthèse stratégique d'un dossier avec restitution sous format PDF.</li>
                    <li><strong className="text-foreground">Appel téléphonique Découverte :</strong> premier échange téléphonique gratuit de 10 minutes pour évaluer la situation du client.</li>
                    <li><strong className="text-foreground">Appel téléphonique Conseil :</strong> consultation téléphonique payante de 30 minutes avec analyse personnalisée.</li>
                    <li><strong className="text-foreground">Question urgente :</strong> prise en charge prioritaire avec réponse garantie sous 2 heures ou 30 minutes selon la formule choisie.</li>
                    <li><strong className="text-foreground">Accompagnement global :</strong> suivi personnalisé incluant stratégie, préparation aux expertises, assistance aux démarches MDPH et analyse des contrats d'assurance.</li>
                  </ul>
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg mt-4">
                    <p className="text-amber-900 text-xs leading-relaxed">
                      <strong>Mention obligatoire :</strong> Les services proposés sont des prestations d'information, d'analyse stratégique
                      et d'accompagnement. Ils ne constituent en aucun cas un conseil juridique, un avis médical, un diagnostic,
                      une prescription, un acte de représentation en justice, ni un acte relevant d'une profession réglementée
                      (avocat, médecin, expert judiciaire). Les décisions finales relèvent des organismes compétents (CPAM, MDPH, tribunaux, assureurs).
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Article 3 — Tarifs */}
              <Card>
                <CardHeader><CardTitle>Article 3 — Tarifs</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4 text-sm">
                  <p>Les tarifs des prestations sont les suivants (prix TTC, en euros) :</p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm border-collapse">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 pr-4 font-semibold text-foreground">Prestation</th>
                          <th className="text-right py-2 font-semibold text-foreground">Tarif TTC</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        <tr><td className="py-2 pr-4">Appel Découverte (10 min)</td><td className="py-2 text-right font-medium text-green-700">Gratuit</td></tr>
                        <tr><td className="py-2 pr-4">Appel Conseil (30 min)</td><td className="py-2 text-right font-medium">75,00 €</td></tr>
                        <tr><td className="py-2 pr-4">Question urgente — Réponse sous 2h</td><td className="py-2 text-right font-medium">50,00 €</td></tr>
                        <tr><td className="py-2 pr-4">Question urgente — Réponse sous 30 min</td><td className="py-2 text-right font-medium">80,00 €</td></tr>
                      </tbody>
                    </table>
                  </div>
                  <p className="text-xs text-muted-foreground/70 mt-2">
                    Les tarifs sont susceptibles d'être modifiés à tout moment. Les tarifs applicables sont ceux en vigueur
                    au jour de la commande. Pour les prestations sur devis, un devis personnalisé est établi selon la
                    complexité de chaque situation.
                  </p>
                </CardContent>
              </Card>

              {/* Article 4 — Modalités de paiement */}
              <Card>
                <CardHeader><CardTitle>Article 4 — Modalités de paiement</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-3 text-sm">
                  <p>Le paiement est exigible <strong className="text-foreground">immédiatement et intégralement avant l'exécution de la prestation</strong>.</p>
                  <p>Les moyens de paiement acceptés sont :</p>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Carte bancaire (Visa, Mastercard, American Express) via <strong className="text-foreground">Stripe</strong></li>
                    <li><strong className="text-foreground">PayPal</strong></li>
                  </ul>
                  <p>
                    Les transactions sont sécurisées par Stripe (certifié PCI DSS niveau 1) et PayPal.
                    Aucune donnée bancaire n'est stockée sur les serveurs de Stratégie & Expertise Santé.
                  </p>
                  <p>
                    Un email de confirmation est envoyé au client après chaque paiement validé.
                    En cas d'échec du paiement, la prestation ne sera pas exécutée.
                  </p>
                </CardContent>
              </Card>

              {/* Article 5 — Délais d'exécution */}
              <Card>
                <CardHeader><CardTitle>Article 5 — Délais d'exécution</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-3 text-sm">
                  <ul className="list-disc pl-6 space-y-2">
                    <li><strong className="text-foreground">Question urgente (formule 30 min) :</strong> réponse sous 30 minutes après confirmation du paiement.</li>
                    <li><strong className="text-foreground">Question urgente (formule 2h) :</strong> réponse sous 2 heures après confirmation du paiement.</li>
                    <li><strong className="text-foreground">Appel Conseil (30 min) :</strong> selon le créneau réservé par le client.</li>
                    <li><strong className="text-foreground">Dossier Express IA :</strong> analyse restituée sous 10 jours ouvrés maximum.</li>
                    <li><strong className="text-foreground">Accompagnement global :</strong> selon le planning convenu avec le client.</li>
                  </ul>
                  <p className="text-xs text-muted-foreground/70 mt-2">
                    Les délais sont donnés à titre indicatif et peuvent varier en fonction de la complexité du dossier,
                    du volume de demandes en cours et de circonstances indépendantes de notre volonté. En cas de retard
                    significatif, le client en sera informé dans les meilleurs délais.
                  </p>
                </CardContent>
              </Card>

              {/* Article 6 — DROIT DE RÉTRACTATION */}
              <Card className="border-red-200 bg-red-50/30">
                <CardHeader><CardTitle className="text-red-900">Article 6 — Droit de rétractation</CardTitle></CardHeader>
                <CardContent className="text-sm space-y-4">
                  <p className="text-red-900/80">
                    Conformément à l'<strong>article L.221-28, 1° du Code de la consommation</strong>, le droit de rétractation
                    de 14 jours ne peut être exercé pour les contrats de fourniture de services pleinement exécutés avant
                    la fin du délai de rétractation et dont l'exécution a commencé après accord préalable exprès du consommateur
                    et renoncement exprès à son droit de rétractation.
                  </p>
                  <div className="p-3 bg-red-100/60 border border-red-300 rounded-lg">
                    <p className="text-red-900 text-xs leading-relaxed font-medium">
                      En validant sa commande et en cochant la case prévue à cet effet, le client reconnaît et accepte expressément :
                    </p>
                    <ul className="list-disc pl-6 space-y-1 text-red-900/80 text-xs mt-2">
                      <li>Que l'exécution de la prestation commence <strong>immédiatement</strong> après la confirmation du paiement ;</li>
                      <li>Qu'il <strong>renonce expressément à son droit de rétractation</strong> dès lors que la prestation a été pleinement exécutée.</li>
                    </ul>
                  </div>
                  <p className="text-muted-foreground text-xs">
                    Cette renonciation est recueillie de manière explicite, non pré-cochée, avant tout paiement,
                    et enregistrée avec horodatage dans nos systèmes.
                  </p>
                </CardContent>
              </Card>

              {/* Article 7 — Politique de remboursement */}
              <Card>
                <CardHeader><CardTitle>Article 7 — Politique de remboursement</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-3 text-sm">
                  <p><strong className="text-foreground">Aucun remboursement</strong> ne sera effectué pour une prestation intégralement exécutée,
                    conformément à l'article 6 ci-dessus.</p>
                  <p>Un remboursement total ou partiel pourra être accordé uniquement dans les cas suivants :</p>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Prestation non réalisée du fait de Stratégie & Expertise Santé ;</li>
                    <li>Impossibilité technique avérée empêchant l'exécution du service ;</li>
                    <li>Annulation par le prestataire avant le début de l'exécution.</li>
                  </ul>
                  <p className="text-xs text-muted-foreground/70">
                    Toute demande de remboursement doit être adressée par email à contact@strategie-expertise-sante.fr
                    dans un délai de 7 jours suivant la date prévue de la prestation, accompagnée des justificatifs nécessaires.
                  </p>
                </CardContent>
              </Card>

              {/* Article 8 — Responsabilité */}
              <Card>
                <CardHeader><CardTitle>Article 8 — Limitation de responsabilité</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-3 text-sm">
                  <p>Stratégie & Expertise Santé s'engage à fournir ses services avec diligence et professionnalisme,
                    dans le cadre d'une <strong className="text-foreground">obligation de moyens</strong>, et non de résultat.</p>
                  <p>En aucun cas Stratégie & Expertise Santé ne pourra être tenu responsable :</p>
                  <ul className="list-disc pl-6 space-y-1">
                    <li>Des décisions prises par les organismes compétents (CPAM, MDPH, tribunaux, commissions médicales, assureurs) ;</li>
                    <li>Des résultats obtenus à la suite des démarches entreprises par le client ;</li>
                    <li>De l'interprétation faite par le client des informations et analyses fournies ;</li>
                    <li>Des dommages indirects, perte de chance ou préjudice moral liés à l'utilisation des services.</li>
                  </ul>
                  <p className="text-xs text-muted-foreground/70">
                    La responsabilité de Stratégie & Expertise Santé est limitée au montant effectivement payé par le client
                    pour la prestation concernée.
                  </p>
                </CardContent>
              </Card>

              {/* Article 9 — Données personnelles */}
              <Card>
                <CardHeader><CardTitle>Article 9 — Données personnelles</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-3 text-sm">
                  <p>
                    Les données personnelles collectées dans le cadre des prestations sont traitées conformément
                    au Règlement Général sur la Protection des Données (RGPD) et à la loi Informatique et Libertés.
                  </p>
                  <p>
                    Pour connaître vos droits et les modalités de traitement de vos données, consultez notre{' '}
                    <Link to="/politique-confidentialite" className="text-accent hover:underline font-medium">
                      Politique de confidentialité
                    </Link>.
                  </p>
                </CardContent>
              </Card>

              {/* Article 10 — Réclamations et litiges */}
              <Card>
                <CardHeader><CardTitle>Article 10 — Réclamations et litiges</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-3 text-sm">
                  <p>
                    Pour toute réclamation, le client peut contacter Stratégie & Expertise Santé par email à
                    contact@strategie-expertise-sante.fr. Une réponse sera apportée dans un délai de 30 jours.
                  </p>
                  <p>
                    Conformément aux articles L.611-1 et suivants du Code de la consommation, en cas de litige non résolu,
                    le client peut recourir gratuitement à un médiateur de la consommation.
                  </p>
                  <p>
                    Les présentes CGV sont soumises au droit français. En cas de litige, les tribunaux compétents sont
                    ceux du ressort du siège social du prestataire (Chartres), sauf disposition légale contraire.
                  </p>
                </CardContent>
              </Card>

              {/* Article 11 — Force majeure */}
              <Card>
                <CardHeader><CardTitle>Article 11 — Force majeure</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-3 text-sm">
                  <p>
                    Stratégie & Expertise Santé ne pourra être tenu responsable de l'inexécution totale ou partielle
                    de ses obligations si cette inexécution est imputable à un cas de force majeure au sens de l'article 1218
                    du Code civil (panne technique majeure, catastrophe naturelle, pandémie, décision administrative, etc.).
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            {/* ═══════════════════ CGU ═══════════════════ */}
            <TabsContent value="cgu" className="space-y-6" data-testid="cgu-content">
              <Card>
                <CardHeader><CardTitle>Article 1 — Objet</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Les présentes Conditions Générales d'Utilisation (CGU) ont pour objet de
                    définir les modalités d'accès et d'utilisation du site Stratégie & Expertise Santé,
                    service édité et exploité par KAPSULES KORPORATION (RCS 824 339 584 R.C.S. Chartres),
                    4 Rue de la Corne du Parc, 28310 Janville-en-Beauce.
                  </p>
                  <p>
                    L'utilisation du site implique l'acceptation pleine et entière des présentes CGU.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Article 2 — Services proposés</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>Stratégie & Expertise Santé propose les services suivants :</p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Accompagnement et conseil dans les démarches liées aux maladies professionnelles et accidents du travail</li>
                    <li>Préparation aux expertises médicales</li>
                    <li>Aide aux démarches MDPH</li>
                    <li>Accompagnement dans les litiges assurantiels</li>
                    <li>Analyse stratégique IA (StratégiIA) et Dossier Express IA</li>
                    <li>Séminaires et formations</li>
                    <li>Forum d'entraide communautaire</li>
                  </ul>
                  <p className="mt-4">
                    <strong className="text-foreground">Important :</strong> Ces services ne se substituent
                    pas aux conseils de professionnels de santé, d'avocats ou d'experts agréés.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Article 3 — Inscription et compte utilisateur</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    L'accès à certaines fonctionnalités (forum, demande de rendez-vous) peut
                    nécessiter la création d'un compte utilisateur.
                  </p>
                  <p>
                    L'utilisateur s'engage à fournir des informations exactes et à maintenir
                    la confidentialité de ses identifiants de connexion.
                  </p>
                  <p>
                    L'inscription anonyme au forum est possible. L'utilisateur s'engage à ne
                    pas utiliser cette fonctionnalité à des fins malveillantes.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Article 4 — Règles du forum</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>Les utilisateurs du forum s'engagent à :</p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Respecter les autres membres et s'exprimer de manière courtoise</li>
                    <li>Ne pas publier de contenu illégal, diffamatoire ou offensant</li>
                    <li>Ne pas divulguer d'informations personnelles permettant d'identifier des tiers</li>
                    <li>Ne pas tenter d'identifier les membres anonymes</li>
                    <li>Signaler tout contenu inapproprié aux modérateurs</li>
                  </ul>
                  <p className="mt-4">
                    Le non-respect de ces règles peut entraîner la suspension ou la suppression du compte.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Article 5 — Tarifs et paiement</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Les tarifs des prestations sont indiqués sur la page dédiée et dans les CGV.
                    Les prix affichés sont en euros TTC. Un devis personnalisé peut être établi
                    selon la complexité de chaque situation.
                  </p>
                  <p>
                    Le paiement peut s'effectuer en ligne par carte bancaire via Stripe ou via PayPal.
                    Le paiement est exigible avant l'exécution de la prestation.
                  </p>
                  <p>
                    Le premier échange téléphonique (Appel Découverte) est gratuit et sans engagement — 10 minutes
                    pour évaluer votre situation.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Article 6 — Droit de rétractation</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Conformément à l'article L.221-28, 1° du Code de la consommation, le droit de rétractation
                    ne peut être exercé pour les services pleinement exécutés avant la fin du délai de rétractation
                    et dont l'exécution a commencé après accord préalable exprès du consommateur et renoncement
                    exprès à son droit de rétractation. Les conditions détaillées figurent dans les CGV.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            {/* ═══════════════════ CONFIDENTIALITÉ ═══════════════════ */}
            <TabsContent value="confidentialite" className="space-y-6">
              <Card className="border-accent/30 bg-accent/5">
                <CardContent className="p-6 flex items-start gap-4">
                  <Shield className="w-6 h-6 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                  <div>
                    <h3 className="font-semibold text-lg mb-1">Politique de confidentialité complète (RGPD)</h3>
                    <p className="text-sm text-muted-foreground mb-3">
                      Consultez notre politique de confidentialité détaillée pour connaître vos droits,
                      les données collectées, leur traitement et leur durée de conservation.
                    </p>
                    <Link to="/politique-confidentialite" className="inline-flex items-center gap-1.5 text-sm font-medium text-accent hover:underline" data-testid="mentions-privacy-link">
                      Accéder à la politique de confidentialité complète <span aria-hidden="true">&rarr;</span>
                    </Link>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Collecte des données personnelles</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Dans le cadre de l'utilisation du site, Stratégie & Expertise Santé est amené à collecter
                    les données personnelles suivantes :
                  </p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Nom, prénom, adresse email (formulaire de contact, paiement)</li>
                    <li>Numéro de téléphone (rendez-vous, questions urgentes)</li>
                    <li>Pseudonyme (forum)</li>
                    <li>Adresse IP et données de navigation</li>
                    <li>Données de paiement (traitées exclusivement par Stripe et PayPal)</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Finalité du traitement</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>Les données collectées sont utilisées pour :</p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Répondre à vos demandes de contact et de rendez-vous</li>
                    <li>Exécuter les prestations commandées et gérer les paiements</li>
                    <li>Gérer votre compte utilisateur sur le forum</li>
                    <li>Améliorer nos services et l'expérience utilisateur</li>
                    <li>Envoyer des informations relatives à nos services (avec votre consentement)</li>
                    <li>Respecter nos obligations légales et comptables</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Conservation des données</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Les données personnelles sont conservées pendant une durée n'excédant pas
                    celle nécessaire aux finalités pour lesquelles elles sont collectées,
                    conformément à la réglementation en vigueur.
                  </p>
                  <p>
                    Les données de contact sont conservées pendant 3 ans à compter du dernier contact.
                    Les données de paiement sont conservées conformément aux obligations comptables (10 ans).
                    Les comptes forum inactifs depuis plus de 2 ans peuvent être supprimés.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Vos droits</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Conformément au Règlement Général sur la Protection des Données (RGPD),
                    vous disposez des droits suivants :
                  </p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li><strong className="text-foreground">Droit d'accès :</strong> obtenir la confirmation que des données vous concernant sont traitées</li>
                    <li><strong className="text-foreground">Droit de rectification :</strong> demander la correction de données inexactes</li>
                    <li><strong className="text-foreground">Droit à l'effacement :</strong> demander la suppression de vos données</li>
                    <li><strong className="text-foreground">Droit à la portabilité :</strong> recevoir vos données dans un format structuré</li>
                    <li><strong className="text-foreground">Droit d'opposition :</strong> vous opposer au traitement de vos données</li>
                  </ul>
                  <p className="mt-4">
                    Pour exercer ces droits, contactez-nous à : contact@strategie-expertise-sante.fr
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Cookies</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Ce site utilise des cookies techniques nécessaires à son fonctionnement.
                    Ces cookies ne collectent pas de données personnelles à des fins publicitaires.
                  </p>
                  <p>
                    Vous pouvez configurer votre navigateur pour refuser les cookies,
                    mais cela pourrait affecter le fonctionnement de certaines fonctionnalités.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Sécurité des données</CardTitle></CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Stratégie & Expertise Santé met en oeuvre des mesures techniques et organisationnelles
                    appropriées pour protéger vos données personnelles contre tout accès non
                    autorisé, modification, divulgation ou destruction.
                  </p>
                  <p>
                    Les paiements en ligne sont sécurisés par Stripe (certifié PCI DSS) et PayPal.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Disclaimer */}
          <Card className="mt-10 border-amber-300 bg-amber-50/50" data-testid="mentions-disclaimer">
            <CardContent className="p-6 space-y-4">
              <h3 className="text-lg font-semibold text-amber-900 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                Clause de non-responsabilité — Avertissement important
              </h3>
              <div className="space-y-3 text-sm text-amber-900/80 leading-relaxed">
                <p>
                  <strong>Nature des services :</strong> Stratégie & Expertise Santé propose un accompagnement
                  stratégique et une analyse documentaire destinés à aider les personnes confrontées à des situations
                  complexes liées aux maladies professionnelles, accidents du travail, procédures MDPH, expertises
                  médicales et litiges assurantiels.
                </p>
                <p>
                  <strong>Distinction avec les expertises officielles :</strong> Ce service ne constitue pas une
                  expertise médicale officielle ni une expertise judiciaire. Les expertises médicales officielles
                  sont réalisées exclusivement par des médecins experts agréés et les expertises judiciaires par
                  des experts judiciaires désignés par les tribunaux. Stratégie & Expertise Santé n'intervient
                  ni en qualité de médecin expert, ni en qualité d'expert judiciaire.
                </p>
                <p>
                  <strong>Absence de conseil juridique et médical :</strong> Les informations, analyses et stratégies
                  fournies par Stratégie & Expertise Santé, y compris celles générées par les outils d'intelligence
                  artificielle (StratégiIA, Dossier Express IA), ont un caractère exclusivement informationnel et
                  pédagogique. Elles ne constituent en aucun cas :
                </p>
                <ul className="list-disc list-inside space-y-1 pl-2">
                  <li>Un conseil juridique ou une consultation juridique au sens de la loi</li>
                  <li>Un avis médical, un diagnostic ou une prescription médicale</li>
                  <li>Un acte de représentation ou d'assistance devant une juridiction</li>
                  <li>Un acte relevant de la profession d'avocat, de médecin ou de tout autre professionnel réglementé</li>
                </ul>
                <p>
                  <strong>Recommandation :</strong> Pour toute décision juridique, médicale ou administrative ayant
                  des conséquences sur vos droits, votre santé ou votre situation personnelle, nous vous recommandons
                  vivement de consulter un professionnel qualifié (avocat, médecin, conseiller juridique agréé).
                </p>
                <p>
                  <strong>Outils d'aide à l'analyse :</strong> Les analyses produites avec l'aide de StratégiIA et
                  du Dossier Express IA utilisent des modèles d'intelligence artificielle comme outil d'assistance.
                  Ces résultats constituent une pré-analyse qui vient enrichir l'accompagnement humain. Ils sont indicatifs
                  et peuvent contenir des imprécisions. L'intelligence artificielle est utilisée comme outil de précision
                  au service de l'expertise humaine, et ne se substitue pas à l'accompagnement d'un professionnel
                  qualifié. L'utilisateur reconnaît utiliser ces outils sous sa propre responsabilité.
                </p>
                <p>
                  <strong>Limitation de responsabilité :</strong> Stratégie & Expertise Santé décline toute
                  responsabilité quant aux décisions prises par l'utilisateur sur la base des informations fournies
                  par le site, ses outils ou ses services. L'utilisation des services vaut acceptation de cette clause.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Date */}
          <p className="text-center text-sm text-muted-foreground mt-12">
            Dernière mise à jour : {new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
      </section>
    </main>
  );
};
