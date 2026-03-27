import { Card, CardContent } from '@/components/ui/card';
import { SEO } from '@/components/SEO';
import { Shield, Lock, Eye, Trash2, Mail, Server, FileText, Users, Cpu, Clock } from 'lucide-react';

export const PolitiqueConfidentialitePage = () => {
  const sections = [
    {
      icon: Users, title: "1. Responsable du traitement",
      content: "Le responsable du traitement des données personnelles est Stratégie & Expertise Santé. Pour toute question relative à la protection de vos données, vous pouvez nous contacter à l'adresse : contact@strategie-expertise-sante.fr."
    },
    {
      icon: FileText, title: "2. Données collectées",
      content: null,
      list: [
        "Données d'identification : nom, prénom, adresse email, numéro de téléphone",
        "Données relatives à votre situation : type de dossier, régime, description de votre situation",
        "Documents transmis : documents médicaux, administratifs et juridiques que vous choisissez de nous transmettre",
        "Données de navigation : adresse IP, cookies techniques, pages visitées (à des fins d'amélioration du service)",
        "Données de santé : informations médicales transmises volontairement dans le cadre de l'accompagnement"
      ]
    },
    {
      icon: Eye, title: "3. Finalités du traitement",
      content: null,
      list: [
        "Analyse de votre situation dans le cadre de l'accompagnement administratif et stratégique",
        "Fourniture des services StratégiIA et Dossier Express IA (pré-analyse assistée par intelligence artificielle)",
        "Génération de rapports personnalisés à partir du texte extrait de vos documents",
        "Communication avec vous concernant votre dossier et envoi du rapport par email",
        "Amélioration de nos services et de l'expérience utilisateur",
        "Respect de nos obligations légales"
      ]
    },
    {
      icon: Lock, title: "4. Base légale du traitement",
      content: "Le traitement de vos données repose sur : votre consentement explicite (article 6.1.a du RGPD), notamment pour les données de santé qui font l'objet d'un consentement spécifique ; l'exécution du contrat de service (article 6.1.b) ; nos intérêts légitimes (article 6.1.f) pour l'amélioration de nos services."
    },
    {
      icon: Shield, title: "5. Données de santé — Protection renforcée",
      content: "Les données de santé bénéficient d'une protection renforcée conformément à l'article 9 du RGPD. Elles sont traitées uniquement avec votre consentement explicite, dans le cadre strict de l'accompagnement administratif et stratégique. Elles ne sont jamais utilisées à des fins commerciales ou de profilage. Les analyses réalisées par nos outils d'aide (StratégiIA, Dossier Express IA) ne constituent ni un diagnostic médical ni un avis médical, mais un accompagnement à la compréhension de votre situation administrative."
    },
    {
      icon: Cpu, title: "6. Traitement par intelligence artificielle",
      content: null,
      list: [
        "Le texte extrait de vos documents est transmis à un service d'intelligence artificielle tiers (Anthropic — modèle Claude) pour générer votre rapport d'analyse personnalisé",
        "Seul le texte extrait est transmis, jamais le fichier original complet",
        "Le texte est tronqué à 8 000 caractères maximum avant transmission",
        "Conformément aux conditions d'Anthropic, les données transmises via l'API ne sont pas utilisées pour entraîner les modèles d'IA",
        "L'extraction de texte (OCR) est réalisée localement sur nos serveurs — aucun service OCR tiers n'intervient",
        "Le résultat de l'analyse IA est conservé pour vous permettre de consulter et télécharger votre rapport"
      ]
    },
    {
      icon: Clock, title: "7. Durée de conservation",
      content: null,
      list: [
        "Fichiers originaux transmis (Dossier Express IA) : non conservés après extraction du texte",
        "Texte extrait des documents : conservé pendant la durée du traitement, puis automatiquement purgé 30 jours après la finalisation du rapport",
        "Rapport d'analyse généré : conservé pendant la durée de la relation contractuelle",
        "Documents de l'Espace Client : conservés tant que votre compte est actif, supprimables à votre demande",
        "Données de compte et de dossier : conservées pendant la durée de la relation, puis 3 ans après le dernier contact",
        "Données de navigation : 13 mois maximum",
        "Données de facturation : 10 ans (obligation légale)"
      ]
    },
    {
      icon: Server, title: "8. Destinataires et sous-traitants",
      content: "Vos données personnelles sont accessibles uniquement à l'équipe restreinte de Stratégie & Expertise Santé dans le cadre de votre accompagnement. Elles ne sont jamais vendues ni cédées. Les sous-traitants techniques suivants peuvent y avoir accès dans le cadre strict de la fourniture du service :",
      list: [
        "Anthropic (États-Unis) : traitement du texte extrait pour la génération des rapports d'analyse IA",
        "Service d'hébergement et de stockage sécurisé : hébergement de l'application et stockage des rapports générés",
        "Resend : envoi des emails transactionnels (confirmation, livraison de rapport)",
        "Stripe : traitement sécurisé des paiements (Stripe ne reçoit aucune donnée médicale)"
      ],
      footer: "Ces sous-traitants sont tenus contractuellement au respect de la confidentialité et du RGPD."
    },
    {
      icon: Trash2, title: "9. Vos droits",
      content: "Conformément au RGPD, vous disposez des droits suivants :",
      list: [
        "Droit d'accès : obtenir une copie de vos données personnelles",
        "Droit de rectification : corriger des données inexactes ou incomplètes",
        "Droit à l'effacement : demander la suppression de vos données",
        "Droit à la limitation du traitement",
        "Droit à la portabilité : recevoir vos données dans un format structuré",
        "Droit d'opposition : vous opposer au traitement de vos données",
        "Droit de retirer votre consentement à tout moment"
      ],
      footer: "Pour exercer ces droits, contactez-nous à contact@strategie-expertise-sante.fr. Nous répondrons dans un délai de 30 jours. En cas de litige, vous pouvez introduire une réclamation auprès de la CNIL (www.cnil.fr)."
    },
    {
      icon: Lock, title: "10. Sécurité des données",
      content: null,
      list: [
        "Communications chiffrées (HTTPS/TLS) sur l'ensemble du site",
        "Accès authentifié et restreint aux données sensibles",
        "Extraction OCR réalisée localement (aucun envoi vers un service OCR tiers)",
        "Purge automatique du texte extrait des documents 30 jours après traitement",
        "Fichiers originaux non conservés après extraction du texte",
        "Accès administrateur limité et tracé"
      ],
      footer: "En cas de violation de données, vous serez informé conformément aux obligations du RGPD (articles 33 et 34)."
    },
    {
      icon: Mail, title: "11. Contact",
      content: "Pour toute question relative à la protection de vos données personnelles ou pour exercer vos droits, contactez-nous : Email : contact@strategie-expertise-sante.fr. Nous nous engageons à traiter votre demande avec diligence et confidentialité."
    }
  ];

  return (
    <main className="min-h-screen bg-background">
      <SEO 
        title="Politique de confidentialité — RGPD" 
        description="Politique de confidentialité et protection des données personnelles de Stratégie & Expertise Santé. Conformité RGPD, droits des utilisateurs, traitement des données de santé." 
        path="/politique-confidentialite" 
      />
      <section className="section-padding">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Shield className="w-8 h-8 text-accent" strokeWidth={1.5} />
            </div>
            <h1 className="text-3xl sm:text-4xl font-semibold mb-3">Politique de confidentialité</h1>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Protection de vos données personnelles conformément au Règlement Général sur la Protection des Données (RGPD).
            </p>
            <p className="text-sm text-muted-foreground mt-2">Dernière mise à jour : 27 mars 2026</p>
          </div>

          <div className="space-y-6">
            {sections.map((s, i) => (
              <Card key={i} className="border-border" data-testid={`privacy-section-${i}`}>
                <CardContent className="p-6">
                  <div className="flex items-start gap-3 mb-3">
                    <s.icon className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                    <h2 className="font-semibold text-lg">{s.title}</h2>
                  </div>
                  {s.content && <p className="text-sm text-muted-foreground leading-relaxed ml-8">{s.content}</p>}
                  {s.list && (
                    <ul className="text-sm text-muted-foreground leading-relaxed ml-8 mt-2 space-y-1.5">
                      {s.list.map((item, j) => (
                        <li key={j} className="flex items-start gap-2">
                          <span className="text-accent mt-1.5 text-xs">&#9679;</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                  {s.footer && <p className="text-sm text-muted-foreground leading-relaxed ml-8 mt-3">{s.footer}</p>}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
};

export default PolitiqueConfidentialitePage;
