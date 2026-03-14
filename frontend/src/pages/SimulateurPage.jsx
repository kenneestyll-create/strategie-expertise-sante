import { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import {
  ArrowRight, ArrowLeft, CheckCircle, AlertTriangle, HelpCircle,
  FileSearch, Shield, Users, Scale, ClipboardList, Mail, Download,
  MessageSquare, Phone, Share2, Copy, Check, CalendarPlus, FileText
} from 'lucide-react';
import axios from 'axios';
import jsPDF from 'jspdf';
import { SEO } from '@/components/SEO';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const QUESTIONS = [
  {
    id: 'situation',
    question: "Quelle est votre situation actuelle ?",
    options: [
      { value: 'at', label: "J'ai eu un accident du travail", icon: AlertTriangle },
      { value: 'mp', label: "J'ai une maladie professionnelle", icon: Shield },
      { value: 'mdph', label: "Je souhaite faire une demande MDPH", icon: Users },
      { value: 'assurance', label: "J'ai un litige avec mon assurance", icon: Scale },
      { value: 'expertise', label: "J'ai une expertise médicale à venir", icon: FileSearch },
      { value: 'autre', label: "Autre situation", icon: HelpCircle }
    ]
  },
  {
    id: 'demarche',
    question: "Où en êtes-vous dans vos démarches ?",
    options: [
      { value: 'debut', label: "Je n'ai pas encore commencé" },
      { value: 'en_cours', label: "J'ai entamé des démarches" },
      { value: 'refus', label: "J'ai reçu un refus" },
      { value: 'recours', label: "Je suis en recours ou contestation" },
      { value: 'expertise', label: "J'attends ou prépare une expertise" }
    ]
  },
  {
    id: 'anciennete',
    question: "Depuis combien de temps dure votre situation ?",
    options: [
      { value: 'recent', label: "Moins de 3 mois" },
      { value: 'moyen', label: "3 mois à 1 an" },
      { value: 'long', label: "Plus d'un an" },
      { value: 'tres_long', label: "Plus de 3 ans" }
    ]
  },
  {
    id: 'accompagnement',
    question: "Êtes-vous accompagné(e) dans vos démarches ?",
    options: [
      { value: 'seul', label: "Non, je suis seul(e)" },
      { value: 'syndicat', label: "Oui, par un syndicat" },
      { value: 'avocat', label: "Oui, par un avocat" },
      { value: 'association', label: "Oui, par une association" },
      { value: 'medecin', label: "Oui, par un médecin conseil" }
    ]
  },
  {
    id: 'besoin',
    question: "Quel est votre besoin principal ?",
    options: [
      { value: 'comprendre', label: "Comprendre mes droits" },
      { value: 'dossier', label: "Aide pour constituer un dossier" },
      { value: 'preparer', label: "Me préparer à une expertise" },
      { value: 'contester', label: "Contester une décision" },
      { value: 'global', label: "Un accompagnement global" }
    ]
  }
];

const getResults = (answers) => {
  const { situation, demarche, besoin, accompagnement, anciennete } = answers;

  let profile = '';
  let urgency = 'normal';
  let recommendations = [];
  let services = [];
  let droits = [];
  let demarches = [];
  let delais = [];

  if (situation === 'at' || situation === 'mp') {
    profile = situation === 'at' ? "Victime d'accident du travail" : "Victime de maladie professionnelle";
    droits.push("Prise en charge à 100% des soins liés à l'AT/MP");
    droits.push("Indemnités journalières majorées pendant l'arrêt de travail");
    droits.push("Rente ou capital en cas de séquelles (IPP)");
    droits.push("Protection contre le licenciement pendant l'arrêt");
    services.push({ id: 'analyse_dossier', label: 'Analyse de dossier AT/MP', prix: '150€' });

    if (situation === 'mp') {
      demarches.push("Obtenir un certificat médical initial (CMI) de votre médecin");
      demarches.push("Remplir la déclaration de maladie professionnelle (Cerfa n°60-3950)");
      demarches.push("Envoyer le dossier complet à votre CPAM");
      demarches.push("Attendre l'instruction et la décision de la CPAM");
      delais.push("Déclaration : dans les 15 jours suivant le certificat médical");
      delais.push("Instruction CPAM : 3 mois (+ 3 mois si enquête complémentaire)");
      delais.push("Contestation : 2 mois après notification de la décision");
    } else {
      demarches.push("Faire constater l'accident par votre employeur (déclaration AT)");
      demarches.push("Consulter un médecin pour le certificat médical initial");
      demarches.push("Vérifier que votre employeur a bien déclaré l'AT à la CPAM");
      delais.push("Déclaration employeur : 48h après l'accident");
      delais.push("Certificat médical : dans les 24h si possible");
      delais.push("Contestation : 2 mois après notification");
    }

    if (demarche === 'refus' || demarche === 'recours') {
      urgency = 'important';
      recommendations.push("Votre refus doit être analysé en détail pour identifier les motifs et préparer un recours solide.");
      recommendations.push("Un accompagnement spécialisé peut significativement améliorer vos chances de succès en recours.");
      demarches.push("Demander la notification écrite du refus avec ses motifs");
      demarches.push("Saisir la Commission de Recours Amiable (CRA) de votre CPAM");
      delais.push("Recours CRA : 2 mois après la notification du refus");
      delais.push("Tribunal (TASS/TJ) : 2 mois après la décision de la CRA");
      services.push({ id: 'preparation_recours', label: 'Préparation du recours', prix: '250€' });
    }
    if (demarche === 'expertise') {
      urgency = 'urgent';
      recommendations.push("La préparation à l'expertise médicale est une étape cruciale. Ne vous y rendez pas sans préparation.");
      recommendations.push("Un dossier médical bien structuré et une chronologie précise font la différence.");
      services.push({ id: 'preparation_expertise', label: 'Préparation expertise médicale', prix: '200€' });
    }
    if (demarche === 'debut') {
      recommendations.push("Bien démarrer vos démarches avec un dossier solide dès le début est essentiel pour la suite.");
    }
  } else if (situation === 'mdph') {
    profile = 'Demande MDPH (Handicap)';
    droits.push("AAH — Allocation aux Adultes Handicapés (jusqu'à 971,37€/mois)");
    droits.push("RQTH — Reconnaissance de la Qualité de Travailleur Handicapé");
    droits.push("CMI — Carte Mobilité Inclusion (invalidité, priorité, stationnement)");
    droits.push("PCH — Prestation de Compensation du Handicap");
    droits.push("Orientation professionnelle ou en établissement");
    demarches.push("Retirer le formulaire Cerfa n°15692 auprès de votre MDPH");
    demarches.push("Faire remplir le certificat médical par votre médecin");
    demarches.push("Constituer le dossier complet avec pièces justificatives");
    demarches.push("Déposer le dossier à la MDPH de votre département");
    delais.push("Instruction MDPH : 4 mois en moyenne (peut aller jusqu'à 6 mois)");
    delais.push("Renouvellement : déposer 6 mois avant l'expiration des droits");
    delais.push("Contestation : 2 mois après notification de la décision");
    services.push({ id: 'accompagnement_mdph', label: 'Accompagnement dossier MDPH', prix: '180€' });
    recommendations.push("Le dossier MDPH requiert une attention particulière, notamment le projet de vie.");
    if (demarche === 'refus') {
      urgency = 'important';
      recommendations.push("Un refus MDPH peut être contesté via un recours administratif préalable (RAPO) puis au tribunal.");
      services.push({ id: 'recours_mdph', label: 'Recours décision MDPH', prix: '250€' });
    }
  } else if (situation === 'assurance') {
    profile = 'Litige assurantiel';
    droits.push("Droit à l'indemnisation selon les garanties de votre contrat");
    droits.push("Protection juridique (si incluse dans votre contrat)");
    droits.push("Droit de contester l'évaluation de l'assureur");
    droits.push("Droit à une contre-expertise médicale");
    demarches.push("Relire attentivement votre contrat d'assurance et ses garanties");
    demarches.push("Vérifier si vous disposez d'une protection juridique");
    demarches.push("Contester par écrit (LRAR) l'évaluation de l'assureur si inadéquate");
    delais.push("Prescription : 2 ans pour les contrats d'assurance (L.114-1 Code Assurances)");
    delais.push("Contestation expertise : dans les meilleurs délais après réception du rapport");
    services.push({ id: 'protection_juridique', label: 'Activation protection juridique', prix: '150€' });
    recommendations.push("Vérifiez si votre contrat inclut une protection juridique qui pourrait couvrir vos frais.");
    if (anciennete === 'long' || anciennete === 'tres_long') {
      urgency = 'important';
      recommendations.push("La durée de votre situation suggère un dossier complexe nécessitant un accompagnement personnalisé.");
    }
  } else if (situation === 'expertise') {
    profile = 'Préparation expertise médicale';
    urgency = 'urgent';
    droits.push("Droit d'être accompagné par un médecin-conseil de votre choix");
    droits.push("Droit de fournir tous documents médicaux utiles");
    droits.push("Droit de contester les conclusions de l'expert");
    droits.push("Droit de demander une contre-expertise");
    demarches.push("Rassembler l'intégralité de votre dossier médical");
    demarches.push("Préparer une chronologie précise de vos symptômes et traitements");
    demarches.push("Lister les impacts concrets sur votre vie quotidienne et professionnelle");
    demarches.push("Envisager d'être assisté par un médecin-conseil lors de l'expertise");
    delais.push("Convocation expertise : se présenter impérativement à la date fixée");
    delais.push("Contestation rapport : dans les 2 mois suivant la notification");
    services.push({ id: 'preparation_expertise', label: 'Préparation expertise médicale', prix: '200€' });
    recommendations.push("La préparation est cruciale pour faire valoir vos droits. Ne sous-estimez pas cette étape.");
  } else {
    profile = 'Situation spécifique';
    recommendations.push("Votre situation mérite une analyse personnalisée lors d'un premier échange gratuit.");
    demarches.push("Prendre contact pour un premier échange gratuit et sans engagement");
  }

  if (accompagnement === 'seul') {
    recommendations.push("Vous n'êtes pas accompagné(e). Un regard expert peut faire une réelle différence dans l'issue de votre dossier.");
    if (besoin === 'global') {
      services.push({ id: 'accompagnement_complet', label: 'Accompagnement complet', prix: '350€' });
    }
  }

  if (besoin === 'comprendre') {
    recommendations.push("Un premier échange gratuit vous permettra de comprendre vos droits et les démarches à entreprendre.");
  }

  if (recommendations.length === 0) {
    recommendations.push("Votre situation mérite un échange personnalisé pour définir la meilleure stratégie.");
  }

  // Select best service recommendation
  const prestation = services.length > 0 ? services[0].label : 'Accompagnement personnalisé';

  return { profile, urgency, recommendations, services, droits, demarches, delais, prestation };
};

/* ─── PDF Generation ─── */
const generatePDF = (results, email) => {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' });
  const w = doc.internal.pageSize.getWidth();
  const margin = 20;
  const contentW = w - margin * 2;
  let y = 0;

  // Colors matching the site theme
  const accent = [185, 78, 72]; // #B94E48 warm red
  const dark = [47, 44, 40];   // #2F2C28 dark brown
  const muted = [120, 115, 108];
  const bgLight = [249, 247, 242]; // #F9F7F2

  // Header band
  doc.setFillColor(...accent);
  doc.rect(0, 0, w, 38, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(20);
  doc.setFont('helvetica', 'bold');
  doc.text("Stratégie & Expertise Santé", margin, 18);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text("Rapport de diagnostic personnalisé", margin, 28);
  doc.text(new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }), w - margin, 28, { align: 'right' });
  y = 48;

  // Profile box
  doc.setFillColor(...bgLight);
  doc.roundedRect(margin, y, contentW, 22, 3, 3, 'F');
  doc.setTextColor(...accent);
  doc.setFontSize(12);
  doc.setFont('helvetica', 'bold');
  doc.text("Profil identifié", margin + 6, y + 9);
  doc.setTextColor(...dark);
  doc.setFontSize(11);
  doc.setFont('helvetica', 'normal');
  doc.text(results.profile, margin + 6, y + 17);
  y += 30;

  // Helper for sections
  const addSection = (title, items, icon) => {
    if (!items || items.length === 0) return;
    if (y > 260) { doc.addPage(); y = 20; }
    doc.setFillColor(...accent);
    doc.rect(margin, y, 3, 8, 'F');
    doc.setTextColor(...dark);
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.text(title, margin + 7, y + 6);
    y += 14;

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9.5);
    doc.setTextColor(...dark);
    items.forEach(item => {
      if (y > 270) { doc.addPage(); y = 20; }
      const lines = doc.splitTextToSize(`• ${item}`, contentW - 10);
      doc.text(lines, margin + 7, y);
      y += lines.length * 5 + 2;
    });
    y += 4;
  };

  addSection("Résumé de votre situation", results.recommendations, "clipboard");
  addSection("Vos droits potentiels", results.droits, "shield");
  addSection("Démarches prioritaires", results.demarches, "list");
  addSection("Délais importants", results.delais, "clock");

  // Recommended service box
  if (results.services.length > 0) {
    if (y > 240) { doc.addPage(); y = 20; }
    doc.setFillColor(...bgLight);
    doc.roundedRect(margin, y, contentW, 30, 3, 3, 'F');
    doc.setDrawColor(...accent);
    doc.roundedRect(margin, y, contentW, 30, 3, 3, 'S');
    doc.setTextColor(...accent);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text("Prestation recommandée", margin + 6, y + 10);
    doc.setTextColor(...dark);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const svcText = results.services.map(s => `${s.label}${s.prix ? ' — ' + s.prix : ''}`).join(' | ');
    doc.text(svcText, margin + 6, y + 19);
    doc.setFontSize(8);
    doc.setTextColor(...muted);
    doc.text("Premier échange gratuit et sans engagement", margin + 6, y + 26);
    y += 38;
  }

  // Footer
  if (y > 250) { doc.addPage(); y = 20; }
  doc.setFillColor(...dark);
  doc.rect(0, 277, w, 20, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.text("Stratégie & Expertise Santé", margin, 285);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8);
  doc.text("Prendre rendez-vous : " + window.location.origin + "/agenda", margin, 291);
  doc.text("Contact : " + window.location.origin + "/contact", w - margin, 291, { align: 'right' });

  // Disclaimer
  doc.setTextColor(...muted);
  doc.setFontSize(7);
  doc.text("Ce rapport est fourni à titre indicatif et ne constitue pas un avis juridique. Consultez un professionnel pour une analyse complète.", margin, y + 4);

  return doc;
};

export const SimulateurPage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showEmailStep, setShowEmailStep] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [email, setEmail] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleAnswer = (questionId, value) => {
    const newAnswers = { ...answers, [questionId]: value };
    setAnswers(newAnswers);

    if (currentStep < QUESTIONS.length - 1) {
      setTimeout(() => setCurrentStep(currentStep + 1), 300);
    } else {
      setTimeout(() => setShowEmailStep(true), 300);
    }
  };

  const handleSubmitEmail = async () => {
    if (!email.trim() || !email.includes('@')) {
      toast.error("Veuillez saisir un email valide");
      return;
    }
    setSaving(true);
    const result = getResults(answers);
    try {
      await axios.post(`${API}/simulator/result`, {
        answers,
        email,
        profile: result.profile,
        recommendations: result.recommendations,
        droits: result.droits,
        demarches: result.demarches,
        delais: result.delais,
        prestation: result.prestation,
      });
      setSaved(true);
      setShowEmailStep(false);
      setShowResults(true);
      toast.success("Rapport enregistré !");
    } catch {
      toast.error("Erreur lors de l'enregistrement");
    } finally {
      setSaving(false);
    }
  };

  const handleSkipEmail = () => {
    setShowEmailStep(false);
    setShowResults(true);
  };

  const handleDownloadPDF = useCallback(() => {
    const result = getResults(answers);
    const doc = generatePDF(result, email);
    doc.save('diagnostic-strategie-expertise-sante.pdf');
    toast.success("PDF téléchargé !");
  }, [answers, email]);

  const getShareText = () => {
    const result = getResults(answers);
    return `J'ai réalisé mon diagnostic sur Stratégie & Expertise Santé. Profil : ${result.profile}. Faites le vôtre :`;
  };

  const getShareUrl = () => `${window.location.origin}/simulateur`;

  const handleWhatsApp = () => {
    window.open(`https://wa.me/?text=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  };
  const handleSMS = () => {
    window.open(`sms:?body=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  };
  const handleShareEmail = () => {
    window.open(`mailto:?subject=${encodeURIComponent('Mon diagnostic — Stratégie & Expertise Santé')}&body=${encodeURIComponent(getShareText() + '\n\n' + getShareUrl())}`, '_blank');
  };
  const handleCopyLink = () => {
    navigator.clipboard.writeText(getShareUrl());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const restart = () => {
    setCurrentStep(0);
    setAnswers({});
    setShowEmailStep(false);
    setShowResults(false);
    setEmail('');
    setSaved(false);
  };

  const results = (showResults || showEmailStep) ? getResults(answers) : null;
  const progress = showResults ? 100 : showEmailStep ? 90 : ((currentStep) / QUESTIONS.length) * 100;

  return (
    <main className="page-transition pt-20">
      <SEO title="Simulateur de droits" description="Simulez gratuitement vos droits en cas de maladie professionnelle, accident du travail ou handicap." path="/simulateur" />
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Diagnostic</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="simulator-title">
              Évaluez votre situation
            </h1>
            <p className="text-lg text-muted-foreground">
              Répondez à quelques questions pour obtenir un rapport personnalisé avec vos droits,
              les démarches prioritaires et une recommandation d'accompagnement.
            </p>
          </div>
        </div>
      </section>

      <section className="section-padding">
        <div className="max-w-2xl mx-auto">
          {/* Progress bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-muted-foreground mb-2">
              <span>Progression</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-accent rounded-full transition-all duration-500" style={{ width: `${progress}%` }} data-testid="progress-bar" />
            </div>
          </div>

          {!showEmailStep && !showResults ? (
            /* ── Questions ── */
            <div data-testid={`question-${currentStep}`}>
              <div className="mb-2 text-sm text-muted-foreground">
                Question {currentStep + 1} / {QUESTIONS.length}
              </div>
              <h2 className="text-2xl font-semibold mb-6">{QUESTIONS[currentStep].question}</h2>

              <div className="space-y-3">
                {QUESTIONS[currentStep].options.map((option) => {
                  const Icon = option.icon;
                  return (
                    <button
                      key={option.value}
                      onClick={() => handleAnswer(QUESTIONS[currentStep].id, option.value)}
                      className={`w-full text-left p-4 rounded-xl border transition-all flex items-center gap-3 group
                        ${answers[QUESTIONS[currentStep].id] === option.value
                          ? 'border-accent bg-accent/10 shadow-md'
                          : 'border-border hover:border-accent/50 hover:bg-muted/30'}
                      `}
                      data-testid={`option-${option.value}`}
                    >
                      {Icon && <Icon className="w-5 h-5 text-accent flex-shrink-0" strokeWidth={1.5} />}
                      <span className="font-medium">{option.label}</span>
                    </button>
                  );
                })}
              </div>

              {currentStep > 0 && (
                <Button variant="ghost" className="mt-6 gap-2" onClick={() => setCurrentStep(currentStep - 1)} data-testid="prev-question">
                  <ArrowLeft className="w-4 h-4" /> Précédent
                </Button>
              )}
            </div>
          ) : showEmailStep && !showResults ? (
            /* ── Email Step ── */
            <div data-testid="email-step">
              <div className="text-center mb-8">
                <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center mx-auto mb-4">
                  <Mail className="w-8 h-8 text-accent" />
                </div>
                <h2 className="text-2xl font-semibold mb-2">Votre rapport est prêt !</h2>
                <p className="text-muted-foreground">
                  Saisissez votre email pour recevoir votre rapport PDF personnalisé
                  et bénéficier d'un suivi de votre dossier.
                </p>
              </div>

              <Card className="border-accent/20">
                <CardContent className="p-6 space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="diag-email" className="font-medium">Votre adresse email</Label>
                    <Input
                      id="diag-email"
                      value={email}
                      onChange={e => setEmail(e.target.value)}
                      placeholder="votre@email.fr"
                      type="email"
                      data-testid="email-step-input"
                    />
                  </div>
                  <Button
                    onClick={handleSubmitEmail}
                    disabled={saving}
                    className="w-full rounded-lg gap-2"
                    data-testid="email-step-submit"
                  >
                    {saving ? 'Enregistrement...' : (
                      <>
                        <FileText className="w-4 h-4" /> Recevoir mon rapport
                      </>
                    )}
                  </Button>
                  <button
                    onClick={handleSkipEmail}
                    className="w-full text-center text-sm text-muted-foreground hover:text-foreground transition-colors py-2"
                    data-testid="email-step-skip"
                  >
                    Passer cette étape
                  </button>
                </CardContent>
              </Card>

              <Button variant="ghost" className="mt-4 gap-2" onClick={() => { setShowEmailStep(false); setCurrentStep(QUESTIONS.length - 1); }} data-testid="back-to-questions">
                <ArrowLeft className="w-4 h-4" /> Modifier mes réponses
              </Button>
            </div>
          ) : (
            /* ── Results ── */
            <div data-testid="simulator-results">
              {/* Urgency banner */}
              <div className={`p-4 rounded-xl border mb-6 flex items-start gap-3
                ${results.urgency === 'urgent' ? 'bg-red-50 border-red-200' :
                  results.urgency === 'important' ? 'bg-amber-50 border-amber-200' : 'bg-green-50 border-green-200'}
              `}>
                {results.urgency === 'urgent' ? (
                  <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                ) : results.urgency === 'important' ? (
                  <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                )}
                <div>
                  <p className="font-semibold">
                    {results.urgency === 'urgent' ? 'Action rapide recommandée' :
                     results.urgency === 'important' ? 'Attention particulière requise' : 'Situation à évaluer'}
                  </p>
                  <p className="text-sm mt-1 text-muted-foreground">Profil : <strong>{results.profile}</strong></p>
                </div>
              </div>

              {/* PDF Download */}
              <Card className="border-accent/20 mb-6">
                <CardContent className="p-5 flex items-center justify-between gap-4">
                  <div>
                    <h3 className="font-semibold flex items-center gap-2">
                      <FileText className="w-5 h-5 text-accent" /> Votre rapport PDF
                    </h3>
                    <p className="text-sm text-muted-foreground">Téléchargez votre diagnostic complet aux couleurs de Stratégie & Expertise Santé</p>
                  </div>
                  <Button onClick={handleDownloadPDF} className="gap-2 rounded-lg flex-shrink-0" data-testid="download-pdf-button">
                    <Download className="w-4 h-4" /> Télécharger
                  </Button>
                </CardContent>
              </Card>

              {/* Recommendations */}
              <h2 className="text-xl font-semibold mb-4">Résumé et recommandations</h2>
              <div className="space-y-3 mb-6">
                {results.recommendations.map((rec, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-muted/30 rounded-lg">
                    <ClipboardList className="w-4 h-4 text-accent flex-shrink-0 mt-1" strokeWidth={1.5} />
                    <p className="text-sm">{rec}</p>
                  </div>
                ))}
              </div>

              {/* Droits */}
              {results.droits.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Vos droits potentiels</h3>
                  <div className="space-y-2">
                    {results.droits.map((d, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                        <span>{d}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Démarches prioritaires */}
              {results.demarches.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Démarches prioritaires</h3>
                  <div className="space-y-2">
                    {results.demarches.map((d, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 bg-accent/5 border border-accent/10 rounded-lg">
                        <span className="w-6 h-6 rounded-full bg-accent/10 flex items-center justify-center text-xs font-bold text-accent flex-shrink-0">{i + 1}</span>
                        <span className="text-sm">{d}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Délais importants */}
              {results.delais.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Délais importants</h3>
                  <div className="space-y-2">
                    {results.delais.map((d, i) => (
                      <div key={i} className="flex items-start gap-2 text-sm">
                        <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                        <span>{d}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Services recommandés */}
              {results.services.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Prestations recommandées</h3>
                  <div className="flex flex-wrap gap-2">
                    {results.services.map((s) => (
                      <Link key={s.id} to="/tarifs">
                        <span className="inline-flex items-center gap-1 bg-accent/10 text-accent px-4 py-2 rounded-full text-sm font-medium hover:bg-accent/20 transition-colors">
                          {s.label}{s.prix && <span className="text-xs ml-1 opacity-75">({s.prix})</span>}
                          <ArrowRight className="w-3 h-3 ml-1" />
                        </span>
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Share buttons */}
              <div className="p-5 rounded-xl border border-border bg-muted/20 mb-6">
                <p className="text-sm font-medium flex items-center gap-2 mb-3">
                  <Share2 className="w-4 h-4 text-accent" /> Partager mon diagnostic
                </p>
                <div className="flex flex-wrap gap-2">
                  <button onClick={handleWhatsApp} className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-[#25D366]/10 text-[#25D366] hover:bg-[#25D366]/20 transition-colors" data-testid="diag-share-whatsapp">
                    <MessageSquare className="w-4 h-4" /> WhatsApp
                  </button>
                  <button onClick={handleSMS} className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-blue-500/10 text-blue-600 hover:bg-blue-500/20 transition-colors" data-testid="diag-share-sms">
                    <Phone className="w-4 h-4" /> SMS
                  </button>
                  <button onClick={handleShareEmail} className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-accent/10 text-accent hover:bg-accent/20 transition-colors" data-testid="diag-share-email">
                    <Mail className="w-4 h-4" /> Email
                  </button>
                  <button onClick={handleCopyLink} className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium bg-muted hover:bg-muted/80 transition-colors" data-testid="diag-share-copy">
                    {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
                    {copied ? 'Copié !' : 'Copier le lien'}
                  </button>
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3">
                <Link to="/agenda" className="flex-1">
                  <Button className="w-full rounded-lg gap-2" data-testid="result-agenda-button">
                    <CalendarPlus className="w-4 h-4" /> Prendre rendez-vous
                  </Button>
                </Link>
                <Link to="/contact" className="flex-1">
                  <Button variant="outline" className="w-full rounded-lg gap-2" data-testid="result-contact-button">
                    <Mail className="w-4 h-4" /> Nous contacter
                  </Button>
                </Link>
                <Button variant="ghost" onClick={restart} className="gap-2" data-testid="restart-button">
                  <ArrowLeft className="w-4 h-4" /> Recommencer
                </Button>
              </div>
            </div>
          )}
        </div>
      </section>
    </main>
  );
};
