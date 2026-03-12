import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Shield, Scale } from 'lucide-react';

export const MentionsLegalesPage = () => {
  return (
    <main className="page-transition pt-20">
      {/* Hero Section */}
      <section className="section-padding bg-secondary">
        <div className="max-w-4xl mx-auto">
          <span className="text-sm font-medium text-accent uppercase tracking-wider">Informations légales</span>
          <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="mentions-legales-title">
            Mentions légales & CGU
          </h1>
          <p className="text-lg text-muted-foreground">
            Retrouvez ici toutes les informations légales concernant le site Stratégie & Expertise Santé 
            ainsi que nos conditions générales d'utilisation.
          </p>
        </div>
      </section>

      {/* Content */}
      <section className="section-padding">
        <div className="max-w-4xl mx-auto">
          <Tabs defaultValue="mentions" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-8">
              <TabsTrigger value="mentions" className="gap-2">
                <FileText className="w-4 h-4" />
                Mentions légales
              </TabsTrigger>
              <TabsTrigger value="cgu" className="gap-2">
                <Scale className="w-4 h-4" />
                CGU
              </TabsTrigger>
              <TabsTrigger value="confidentialite" className="gap-2">
                <Shield className="w-4 h-4" />
                Confidentialité
              </TabsTrigger>
            </TabsList>

            {/* Mentions Légales */}
            <TabsContent value="mentions" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Éditeur du site</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-muted-foreground">
                  <p>
                    <strong className="text-foreground">Stratégie & Expertise Santé</strong><br />
                    Service d'accompagnement et de conseil<br />
                    [Adresse à compléter]<br />
                    [Code postal - Ville]
                  </p>
                  <p>
                    <strong className="text-foreground">Contact :</strong><br />
                    Email : contact@strategie-expertise-sante.fr<br />
                    Téléphone : [Numéro à compléter]
                  </p>
                  <p>
                    <strong className="text-foreground">Responsable de la publication :</strong><br />
                    [Nom du responsable à compléter]
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Hébergement</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground">
                  <p>
                    Ce site est hébergé par :<br />
                    [Nom de l'hébergeur]<br />
                    [Adresse de l'hébergeur]
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Propriété intellectuelle</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    L'ensemble du contenu de ce site (textes, images, vidéos, logos, graphismes) 
                    est la propriété exclusive de Stratégie & Expertise Santé, sauf mention contraire.
                  </p>
                  <p>
                    Toute reproduction, représentation, modification, publication ou adaptation 
                    de tout ou partie des éléments du site, quel que soit le moyen ou le procédé 
                    utilisé, est interdite sans autorisation écrite préalable.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Limitation de responsabilité</CardTitle>
                </CardHeader>
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

            {/* CGU */}
            <TabsContent value="cgu" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Article 1 - Objet</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Les présentes Conditions Générales d'Utilisation (CGU) ont pour objet de 
                    définir les modalités d'accès et d'utilisation du site Stratégie & Expertise Santé 
                    et des services proposés.
                  </p>
                  <p>
                    L'utilisation du site implique l'acceptation pleine et entière des présentes CGU.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Article 2 - Services proposés</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>Stratégie & Expertise Santé propose les services suivants :</p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Accompagnement et conseil dans les démarches liées aux maladies professionnelles et accidents du travail</li>
                    <li>Préparation aux expertises médicales</li>
                    <li>Aide aux démarches MDPH</li>
                    <li>Accompagnement dans les litiges assurantiels</li>
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
                <CardHeader>
                  <CardTitle>Article 3 - Inscription et compte utilisateur</CardTitle>
                </CardHeader>
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
                <CardHeader>
                  <CardTitle>Article 4 - Règles du forum</CardTitle>
                </CardHeader>
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
                <CardHeader>
                  <CardTitle>Article 5 - Tarifs et paiement</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Les tarifs des prestations sont indiqués sur la page dédiée et peuvent être 
                    modifiés à tout moment. Les prix affichés sont des tarifs de départ, un devis 
                    personnalisé étant établi selon la complexité de chaque situation.
                  </p>
                  <p>
                    Le paiement peut s'effectuer en ligne par carte bancaire via notre plateforme 
                    sécurisée (Stripe) ou par virement bancaire.
                  </p>
                  <p>
                    Le premier échange téléphonique est gratuit et sans engagement.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Article 6 - Droit de rétractation</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Conformément aux dispositions légales, vous disposez d'un délai de 14 jours 
                    à compter de la souscription pour exercer votre droit de rétractation, 
                    sauf si la prestation a déjà été exécutée avec votre accord.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Politique de confidentialité */}
            <TabsContent value="confidentialite" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Collecte des données personnelles</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Dans le cadre de l'utilisation du site, Stratégie & Expertise Santé est amené à collecter 
                    les données personnelles suivantes :
                  </p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Nom, prénom, adresse email (formulaire de contact)</li>
                    <li>Numéro de téléphone (optionnel)</li>
                    <li>Pseudonyme (forum)</li>
                    <li>Adresse IP et données de navigation</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Finalité du traitement</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>Les données collectées sont utilisées pour :</p>
                  <ul className="list-disc pl-6 space-y-2">
                    <li>Répondre à vos demandes de contact et de rendez-vous</li>
                    <li>Gérer votre compte utilisateur sur le forum</li>
                    <li>Améliorer nos services et l'expérience utilisateur</li>
                    <li>Envoyer des informations relatives à nos services (avec votre consentement)</li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Conservation des données</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Les données personnelles sont conservées pendant une durée n'excédant pas 
                    celle nécessaire aux finalités pour lesquelles elles sont collectées, 
                    conformément à la réglementation en vigueur.
                  </p>
                  <p>
                    Les données de contact sont conservées pendant 3 ans à compter du dernier contact.
                    Les comptes forum inactifs depuis plus de 2 ans peuvent être supprimés.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Vos droits</CardTitle>
                </CardHeader>
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
                <CardHeader>
                  <CardTitle>Cookies</CardTitle>
                </CardHeader>
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
                <CardHeader>
                  <CardTitle>Sécurité des données</CardTitle>
                </CardHeader>
                <CardContent className="text-muted-foreground space-y-4">
                  <p>
                    Stratégie & Expertise Santé met en œuvre des mesures techniques et organisationnelles 
                    appropriées pour protéger vos données personnelles contre tout accès non 
                    autorisé, modification, divulgation ou destruction.
                  </p>
                  <p>
                    Les paiements en ligne sont sécurisés par Stripe, certifié PCI DSS.
                  </p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Date de mise à jour */}
          <p className="text-center text-sm text-muted-foreground mt-12">
            Dernière mise à jour : {new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
      </section>
    </main>
  );
};
