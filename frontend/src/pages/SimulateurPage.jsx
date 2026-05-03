import { useState, useCallback, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import {
  ArrowRight, ArrowLeft, CheckCircle, AlertTriangle, HelpCircle,
  FileSearch, Shield, Users, Scale, ClipboardList, Mail, Download,
  MessageSquare, Phone, Share2, Copy, Check, CalendarPlus, FileText,
  ChevronDown, Target, Sparkles, Lock
} from 'lucide-react';
import axios from 'axios';
import jsPDF from 'jspdf';
import QRCode from 'qrcode';
import { SEO } from '@/components/SEO';
import { TerrainNote } from '@/components/TerrainNote';
import { SHIELD_B64 } from './shieldLogo';
import { useAdminTest } from '@/components/AdminTestBanner';

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
      { value: 'médecin', label: "Oui, par un médecin conseil" }
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

const getResults = (answers, autreTexte = '') => {
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
      services.push({ id: 'préparation_recours', label: 'Préparation du recours', prix: '250€' });
    }
    if (demarche === 'expertise') {
      urgency = 'urgent';
      recommendations.push("La préparation à l'expertise médicale est une étape cruciale. Ne vous y rendez pas sans préparation.");
      recommendations.push("Un dossier médical bien structuré et une chronologie précise font la différence.");
      services.push({ id: 'préparation_expertise', label: 'Préparation expertise médicale', prix: '200€' });
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
    services.push({ id: 'préparation_expertise', label: 'Préparation expertise médicale', prix: '200€' });
    recommendations.push("La préparation est cruciale pour faire valoir vos droits. Ne sous-estimez pas cette étape.");
  } else {
    profile = autreTexte ? `Situation spécifique : ${autreTexte}` : 'Situation spécifique';
    recommendations.push("Votre situation mérite une analyse personnalisée lors d'une première consultation gratuite de 10 minutes.");
    if (autreTexte) {
      recommendations.push(`Vous avez décrit votre situation comme suit : « ${autreTexte} ». Un expert pourra analyser votre cas en détail.`);
    }
    demarches.push("Prendre contact pour une première consultation gratuite de 10 minutes, sans engagement");
    services.push({ id: 'consultation_personnalisée', label: 'Consultation personnalisée', prix: '100€' });
  }

  if (accompagnement === 'seul') {
    recommendations.push("Vous n'êtes pas accompagné(e). Un regard expert peut faire une réelle différence dans l'issue de votre dossier.");
    if (besoin === 'global') {
      services.push({ id: 'accompagnement_complet', label: 'Accompagnement complet', prix: '350€' });
    }
  }

  if (besoin === 'comprendre') {
    recommendations.push("Une première consultation gratuite de 10 minutes vous permettra de comprendre vos droits et les démarches à entreprendre.");
  }

  if (recommendations.length === 0) {
    recommendations.push("Votre situation mérite un échange personnalisé pour définir la meilleure stratégie.");
  }

  // Select best service recommendation
  const prestation = services.length > 0 ? services[0].label : 'Accompagnement personnalisé';

  return { profile, urgency, recommendations, services, droits, demarches, delais, prestation };
};


/* ─── Premium PDF Generation (Noir / Or / Ivoire) ─── */
const generatePDF = (results, email, qrDataUrl = null) => {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' });
  const w = doc.internal.pageSize.getWidth();
  const h = doc.internal.pageSize.getHeight();
  const LM = 16;
  const RM = 16;
  const CW = w - LM - RM;
  const FOOTER_Y = h - 14;
  const maxY = FOOTER_Y - 4;
  let y = 0;

  /* ── Palette premium ── */
  const BLACK    = [26, 26, 26];
  const GOLD     = [201, 168, 76];
  const GOLD_LT  = [218, 195, 130];
  const IVORY    = [250, 248, 243];
  const DARK_TXT = [35, 35, 35];
  const BODY_TXT = [55, 55, 55];
  const MUTED    = [130, 125, 118];

  const genDate = new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
  const reportNum = `SES-${new Date().getFullYear()}-${String(Math.floor(10000 + Math.random() * 90000))}`;
  const year = new Date().getFullYear();

  /* ── Header (repeated on each page) ── */
  const drawHeader = () => {
    doc.setFillColor(...BLACK);
    doc.rect(0, 0, w, 22, 'F');
    doc.setFillColor(...GOLD);
    doc.rect(0, 22, w, 0.6, 'F');
    /* Shield logo */
    const shieldW = 10;
    const shieldH = shieldW * (48 / 44);
    const shieldX = LM + 1;
    const shieldY = (22 - shieldH) / 2;
    try { doc.addImage(SHIELD_B64, 'PNG', shieldX, shieldY, shieldW, shieldH); } catch (_) { /* fallback: no image */ }
    /* Brand text (offset right of shield) */
    const txtX = LM + shieldW + 4;
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(11);
    doc.text("Strat\u00e9gie & Expertise Sant\u00e9", txtX, 10);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(6.5);
    doc.setTextColor(...GOLD_LT);
    doc.text("PIONNIER EN FRANCE", txtX, 16);
    doc.setFontSize(7);
    doc.setTextColor(180, 180, 180);
    doc.text(genDate, w - RM, 10, { align: 'right' });
    doc.setTextColor(...GOLD_LT);
    doc.text(reportNum, w - RM, 16, { align: 'right' });
    y = 26;
  };

  /* ── Footer (drawn once per page at the end) ── */
  const drawFooter = () => {
    doc.setDrawColor(...GOLD);
    doc.setLineWidth(0.3);
    doc.line(LM, FOOTER_Y, w - RM, FOOTER_Y);
    doc.setTextColor(...MUTED);
    doc.setFontSize(6);
    doc.setFont('helvetica', 'normal');
    doc.text(
      `\u00A9 ${year} Strat\u00e9gie & Expertise Sant\u00e9  \u2014  strategie-expertise-sante.fr  \u2014  Document confidentiel`,
      w / 2, FOOTER_Y + 5, { align: 'center' }
    );
  };

  /* ── Watermark ── */
  const drawWatermark = () => {
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(38);
    doc.setTextColor(240, 238, 232);
    doc.text("Strat\u00e9gie & Expertise Sant\u00e9", w / 2, h / 2, { align: 'center', angle: 35 });
  };

  /* ── Page break helper ── */
  const checkBreak = (needed) => {
    if (y + needed > maxY) {
      doc.addPage();
      drawHeader();
    }
  };

  /* ═══════════════ PAGE 1 ═══════════════ */
  drawHeader();

  /* Client info bar */
  doc.setFillColor(...IVORY);
  doc.rect(LM, y, CW, 10, 'F');
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(7.5);
  doc.setTextColor(...DARK_TXT);
  doc.text(email || 'Client', LM + 4, y + 4.5);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(6.5);
  doc.setTextColor(...GOLD);
  doc.text("Rapport Auto-diagnostic", LM + 4, y + 8.5);
  doc.setFontSize(7);
  doc.setTextColor(...MUTED);
  doc.text(genDate, w - RM - 4, y + 6, { align: 'right' });
  y += 14;

  /* Profile block */
  doc.setFillColor(...IVORY);
  doc.roundedRect(LM, y, CW, 14, 2, 2, 'F');
  doc.setFillColor(...GOLD);
  doc.rect(LM, y, 2, 14, 'F');
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(9);
  doc.setTextColor(...BLACK);
  doc.text("Profil identifi\u00e9", LM + 6, y + 5.5);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(8.5);
  doc.setTextColor(...BODY_TXT);
  doc.text(results.profile, LM + 6, y + 11);
  y += 20;

  /* ── Section renderer ── */
  const addSection = (title, items) => {
    if (!items || items.length === 0) return;
    checkBreak(16);
    /* Gold left accent */
    doc.setFillColor(...GOLD);
    doc.rect(LM, y, 2, 5.5, 'F');
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9.5);
    doc.setTextColor(...BLACK);
    doc.text(title, LM + 5, y + 4);
    y += 9;

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    items.forEach(item => {
      const lines = doc.splitTextToSize(item, CW - 12);
      const blockH = lines.length * 4 + 1.5;
      checkBreak(blockH);
      /* Gold bullet */
      doc.setFillColor(...GOLD);
      doc.rect(LM + 4, y + 0.8, 1.2, 1.2, 'F');
      doc.setTextColor(...BODY_TXT);
      doc.text(lines, LM + 8, y + 2.5);
      y += blockH;
    });
    y += 3;
  };

  addSection("R\u00e9sum\u00e9 de votre situation", results.recommendations);
  addSection("Vos droits potentiels", results.droits);
  addSection("D\u00e9marches prioritaires", results.demarches);
  addSection("D\u00e9lais importants", results.delais);

  /* Services block */
  if (results.services.length > 0) {
    checkBreak(22);
    doc.setFillColor(...IVORY);
    doc.roundedRect(LM, y, CW, 18, 2, 2, 'F');
    doc.setDrawColor(...GOLD);
    doc.setLineWidth(0.3);
    doc.roundedRect(LM, y, CW, 18, 2, 2, 'S');
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8.5);
    doc.setTextColor(...BLACK);
    doc.text("Prestation recommand\u00e9e", LM + 5, y + 6);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(8);
    doc.setTextColor(...BODY_TXT);
    const svcTxt = results.services.map(s => `${s.label}${s.prix ? ' \u2014 ' + s.prix : ''}`).join(' | ');
    doc.text(svcTxt, LM + 5, y + 12);
    doc.setFontSize(6.5);
    doc.setTextColor(...MUTED);
    doc.text("Premi\u00e8re consultation gratuite \u2014 10 min, sans engagement", LM + 5, y + 16);
    y += 24;
  }

  /* ── Signature émotionnelle premium ── */
  checkBreak(32);
  y += 4;
  doc.setFillColor(...IVORY);
  doc.roundedRect(LM, y, CW, 24, 2, 2, 'F');
  doc.setFillColor(...GOLD);
  doc.rect(LM, y, 2, 24, 'F');
  doc.setFont('helvetica', 'italic');
  doc.setFontSize(9);
  doc.setTextColor(...BLACK);
  doc.text("Vous n'\u00eates plus seul(e) face \u00e0 cette \u00e9preuve.", LM + 7, y + 8);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(9.5);
  doc.setTextColor(...GOLD);
  doc.text("D\u00e9sormais, Strat\u00e9gie & Expertise Sant\u00e9 est votre bouclier.", LM + 7, y + 16);
  y += 30;

  /* Contact & CTA */
  checkBreak(24);
  y += 4;
  doc.setDrawColor(...GOLD);
  doc.setLineWidth(0.3);
  doc.line(65, y, 145, y);
  y += 5;
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(8.5);
  doc.setTextColor(...BLACK);
  doc.text("Strat\u00e9gie & Expertise Sant\u00e9", w / 2, y, { align: 'center' });
  y += 5;
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7);
  doc.setTextColor(...MUTED);
  doc.text("Prendre rendez-vous : strategie-expertise-sante.fr/contact", w / 2, y, { align: 'center' });
  y += 4;
  doc.setFont('helvetica', 'italic');
  doc.setFontSize(6.5);
  doc.text("Consultation personnalis\u00e9e sur rendez-vous \u2014 Premi\u00e8re consultation gratuite", w / 2, y, { align: 'center' });

  /* ── QR code (cohérence visuelle avec PDFs Dossier Express et StrategiIA) ── */
  if (qrDataUrl) {
    y += 8;
    /* Si l'espace restant est insuffisant, nouvelle page */
    if (y + 32 > maxY) {
      doc.addPage();
      y = 32;
    }
    /* Ligne séparatrice fine */
    doc.setDrawColor(...GOLD_LT);
    doc.setLineWidth(0.15);
    doc.line(LM + 25, y, w - RM - 25, y);
    y += 5;

    /* Libellé "Prochaine étape recommandée" */
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(7);
    doc.setTextColor(...MUTED);
    doc.text("Prochaine \u00e9tape recommand\u00e9e", w / 2, y, { align: 'center' });
    y += 4;

    /* QR centré 22×22 mm — identique aux PDFs backend */
    const qrSize = 22;
    const qrX = (w - qrSize) / 2;
    try { doc.addImage(qrDataUrl, 'PNG', qrX, y, qrSize, qrSize); } catch (_) { /* fallback silencieux */ }
    y += qrSize + 3;

    /* Libellé sous le QR */
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(6.5);
    doc.setTextColor(...MUTED);
    doc.text("Scanner pour prendre contact", w / 2, y, { align: 'center' });
  }

  /* ── Apply footer + watermark on every page ── */
  const totalPages = doc.internal.getNumberOfPages();
  for (let p = 1; p <= totalPages; p++) {
    doc.setPage(p);
    drawWatermark();
    drawFooter();
  }

  return doc;
};

export const SimulateurPage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [autreTexte, setAutreTexte] = useState('');
  const [showAutreInput, setShowAutreInput] = useState(false);
  const [showEmailStep, setShowEmailStep] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [email, setEmail] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [copied, setCopied] = useState(false);
  const { isAdminMode } = useAdminTest();

  const handleAnswer = (questionId, value) => {
    const newAnswers = { ...answers, [questionId]: value };
    setAnswers(newAnswers);

    // If "Autre situation" is selected on the first question, show text input first
    if (questionId === 'situation' && value === 'autre') {
      setShowAutreInput(true);
      return; // Don't advance to next step yet
    }

    setShowAutreInput(false);
    if (currentStep < QUESTIONS.length - 1) {
      setTimeout(() => setCurrentStep(currentStep + 1), 300);
    } else {
      setTimeout(() => setShowEmailStep(true), 300);
    }
  };

  const handleAutreSubmit = () => {
    if (!autreTexte.trim() || autreTexte.trim().length < 5) {
      toast.error("Veuillez décrire brièvement votre situation (au moins 5 caractères)");
      return;
    }
    setShowAutreInput(false);
    if (currentStep < QUESTIONS.length - 1) {
      setTimeout(() => setCurrentStep(currentStep + 1), 300);
    } else {
      setTimeout(() => setShowEmailStep(true), 300);
    }
  };

  const handleSubmitEmail = async () => {
    // Admin bypass: skip email gate entirely
    if (isAdminMode) {
      setEmail('admin-test@ses-interne.fr');
      setSaved(true);
      setShowEmailStep(false);
      setShowResults(true);
      toast.success("Mode Admin : email bypass, aucun lead créé.");
      return;
    }
    const trimmed = email.trim().toLowerCase();
    if (!trimmed || !trimmed.includes('@') || !trimmed.includes('.') || trimmed.length < 5) {
      toast.error("Veuillez renseigner une adresse email valide pour recevoir votre rapport personnalisé.");
      return;
    }
    setSaving(true);
    const result = getResults(answers, autreTexte);
    try {
      await axios.post(`${API}/simulator/result`, {
        answers,
        autre_situation: autreTexte.trim() || undefined,
        email: trimmed,
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
    } catch (e) {
      toast.error("Erreur lors de l'enregistrement");
    } finally {
      setSaving(false);
    }
  };

  const handleDownloadPDF = useCallback(async () => {
    const result = getResults(answers, autreTexte);
    /* Génération du QR — cohérence visuelle avec les PDFs Dossier Express et StrategiIA */
    let qrDataUrl = null;
    try {
      qrDataUrl = await QRCode.toDataURL(
        'https://strategie-expertise-sante.fr/contact?via=qr&source=auto_diagnostic',
        { errorCorrectionLevel: 'M', margin: 2, scale: 8, color: { dark: '#1a1a1a', light: '#FAF8F3' } }
      );
    } catch (_) { /* fallback silencieux : PDF généré sans QR */ }
    const doc = generatePDF(result, email, qrDataUrl);
    doc.save(`rapport-diagnostic-SES-${new Date().getFullYear()}.pdf`);
    toast.success("PDF téléchargé !");
  }, [answers, email, autreTexte]);

  const getShareText = () => {
    const result = getResults(answers, autreTexte);
    return `J'ai réalisé mon auto-diagnostic sur Stratégie & Expertise Santé. Profil : ${result.profile}. Faites le vôtre :`;
  };

  const getShareUrl = () => `${window.location.origin}/simulateur`;

  const handleWhatsApp = () => {
    window.open(`https://wa.me/?text=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  };
  const handleSMS = () => {
    window.open(`sms:?body=${encodeURIComponent(getShareText() + ' ' + getShareUrl())}`, '_blank');
  };
  const handleShareEmail = () => {
    window.open(`mailto:?subject=${encodeURIComponent('Mon auto-diagnostic — Stratégie & Expertise Santé')}&body=${encodeURIComponent(getShareText() + '\n\n' + getShareUrl())}`, '_blank');
  };
  const handleCopyLink = () => {
    navigator.clipboard.writeText(getShareUrl());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const restart = () => {
    setCurrentStep(0);
    setAnswers({});
    setAutreTexte('');
    setShowAutreInput(false);
    setShowEmailStep(false);
    setShowResults(false);
    setEmail('');
    setSaved(false);
  };

  const results = (showResults || showEmailStep) ? getResults(answers, autreTexte) : null;
  const progress = showResults ? 100 : showEmailStep ? 90 : ((currentStep) / QUESTIONS.length) * 100;

  return (
    <main className="page-transition pt-20">
      <SEO title="Diagnostic stratégique gratuit — 5 minutes" description="Un diagnostic personnalisé de votre situation : AT/MP, MDPH, expertise médicale, protection juridique. Rapport téléchargeable, 100% confidentiel." path="/simulateur" />
      {/* HERO — Diagnostic stratégique */}
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Diagnostic stratégique</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6 leading-tight" data-testid="simulator-title">
              Diagnostic stratégique gratuit — en 5 minutes
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed mb-4">
              Ce n'est pas un simple quiz : c'est un diagnostic conçu à partir de dossiers réels en AT/MP, MDPH, expertise médicale et litiges d'assurance. Vous obtenez un rapport personnalisé avec vos priorités, vos démarches clés et les pièges à éviter sur votre situation précise.
            </p>
            <div className="flex flex-wrap gap-4 items-center text-xs text-muted-foreground mb-8">
              <span className="inline-flex items-center gap-1.5"><Lock className="w-3.5 h-3.5 text-accent" strokeWidth={2} /> 100 % confidentiel</span>
              <span className="inline-flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5 text-accent" strokeWidth={2} /> Sans engagement</span>
              <span className="inline-flex items-center gap-1.5"><Sparkles className="w-3.5 h-3.5 text-accent" strokeWidth={2} /> Rapport téléchargeable</span>
            </div>
            <a href="#diagnostic-form" data-testid="hero-cta-scroll">
              <Button size="lg" className="rounded-full px-8 gap-2 bg-accent text-accent-foreground hover:bg-accent/90">
                Démarrer mon diagnostic <ArrowRight className="w-4 h-4" />
              </Button>
            </a>
          </div>
        </div>
      </section>

      <section id="diagnostic-form" className="section-padding scroll-mt-24">
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

              {/* Champ texte "Autre situation" */}
              {showAutreInput && QUESTIONS[currentStep].id === 'situation' && (
                <div className="mt-5 p-4 rounded-xl border border-accent/30 bg-accent/5 space-y-3" data-testid="autre-situation-input-wrapper">
                  <Label htmlFor="autre-texte" className="font-medium text-sm">
                    Décrivez brièvement votre situation
                  </Label>
                  <Input
                    id="autre-texte"
                    value={autreTexte}
                    onChange={e => setAutreTexte(e.target.value)}
                    placeholder="Ex. : conflit avec mon employeur suite à un reclassement..."
                    maxLength={200}
                    data-testid="autre-situation-input"
                  />
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">{autreTexte.length}/200 caractères</span>
                    <Button
                      onClick={handleAutreSubmit}
                      size="sm"
                      className="gap-2 rounded-lg"
                      data-testid="autre-situation-submit"
                    >
                      Continuer <ArrowRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}

              {currentStep > 0 && (
                <Button variant="ghost" className="mt-6 gap-2" onClick={() => { setShowAutreInput(false); setCurrentStep(currentStep - 1); }} data-testid="prev-question">
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
                    <Label htmlFor="diag-email" className="font-medium">Votre adresse email <span className="text-red-500">*</span></Label>
                    <Input
                      id="diag-email"
                      value={email}
                      onChange={e => setEmail(e.target.value)}
                      placeholder="votre@email.fr"
                      type="email"
                      data-testid="email-step-input"
                      onKeyDown={e => e.key === 'Enter' && handleSubmitEmail()}
                    />
                    <p className="text-xs text-muted-foreground">Votre email est nécessaire pour vous envoyer le rapport et assurer le suivi de votre dossier.</p>
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

      {/* ENRICHMENT — Comment ça marche */}
      <section className="section-padding bg-secondary/30" data-testid="simulateur-how-it-works">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-semibold mb-3">Comment ça marche</h2>
            <p className="text-sm text-muted-foreground">Trois étapes, quelques minutes, un rapport personnalisé.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-5">
            {[
              { icon: Target, num: "01", title: "Vous répondez à quelques questions ciblées", desc: "Situation, démarches en cours, ancienneté, accompagnement. Des questions conçues pour cerner votre contexte sans entrer dans le médical." },
              { icon: FileSearch, num: "02", title: "L'algorithme analyse votre situation", desc: "Le moteur croise vos réponses avec les règles CPAM, MDPH, AT/MP et les stratégies de recours éprouvées sur le terrain." },
              { icon: Download, num: "03", title: "Vous recevez un rapport personnalisé", desc: "Priorités classées, démarches et délais, pièges identifiés, ressources et guides recommandés. Téléchargement immédiat." },
            ].map((s, i) => (
              <Card key={i} className="border-border/50">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-full bg-accent/10 border border-accent/30 flex items-center justify-center">
                      <s.icon className="w-5 h-5 text-accent" strokeWidth={1.75} />
                    </div>
                    <span className="text-xs font-semibold text-accent/70 tracking-widest">ÉTAPE {s.num}</span>
                  </div>
                  <h3 className="font-semibold text-base text-foreground mb-2">{s.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{s.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* ENRICHMENT — Ce que vous recevez */}
      <section className="section-padding" data-testid="simulateur-what-you-get">
        <div className="max-w-5xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-10 items-start">
            <div>
              <h2 className="text-2xl sm:text-3xl font-semibold mb-3">Ce que contient votre rapport</h2>
              <p className="text-sm text-muted-foreground leading-relaxed mb-6">
                Un document synthétique et actionnable, conçu pour vous donner une feuille de route claire sur votre situation.
              </p>
              <ul className="space-y-3 text-sm">
                {[
                  "Vos priorités stratégiques classées par urgence",
                  "Les démarches à engager et leurs délais précis",
                  "Les pièges identifiés sur votre situation",
                  "Les ressources, guides et outils recommandés",
                  "Une orientation vers l'accompagnement adapté si utile",
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={2} />
                    <span className="text-muted-foreground">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="relative">
              <div className="rounded-2xl bg-gradient-to-br from-[#1a1a2e]/[0.03] to-accent/[0.03] border border-border/60 p-6 sm:p-8">
                <div className="flex items-center gap-3 mb-5 pb-4 border-b border-border/50">
                  <div className="w-10 h-10 rounded-lg bg-accent/15 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-accent" strokeWidth={1.75} />
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider">Aperçu du rapport</p>
                    <p className="text-sm font-semibold text-foreground">Diagnostic Stratégique — Personnalisé</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="h-2 bg-accent/30 rounded w-1/3 mb-2"></div>
                    <div className="h-1.5 bg-muted rounded w-full"></div>
                    <div className="h-1.5 bg-muted rounded w-5/6 mt-1"></div>
                  </div>
                  <div>
                    <div className="h-2 bg-accent/20 rounded w-2/5 mb-2 mt-4"></div>
                    <div className="h-1.5 bg-muted rounded w-full"></div>
                    <div className="h-1.5 bg-muted rounded w-4/5 mt-1"></div>
                    <div className="h-1.5 bg-muted rounded w-3/4 mt-1"></div>
                  </div>
                  <div>
                    <div className="h-2 bg-accent/20 rounded w-1/2 mb-2 mt-4"></div>
                    <div className="h-1.5 bg-muted rounded w-full"></div>
                    <div className="h-1.5 bg-muted rounded w-5/6 mt-1"></div>
                  </div>
                </div>
                <p className="text-[10px] text-muted-foreground/70 italic mt-5 pt-4 border-t border-border/50">Aperçu stylisé — le rapport réel est personnalisé selon vos réponses.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ENRICHMENT — Pour qui (cartes maillage pages piliers) */}
      <section className="section-padding bg-secondary/30" data-testid="simulateur-for-whom">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-semibold mb-3">Pour qui est ce diagnostic ?</h2>
            <p className="text-sm text-muted-foreground">Le simulateur couvre toutes les situations que nous accompagnons.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Accident du travail / MP", href: "/accident-travail-maladie-professionnelle", icon: AlertTriangle },
              { label: "MDPH", href: "/mdph", icon: Users },
              { label: "AAH", href: "/calculatrice-aah", icon: HelpCircle },
              { label: "Expertise médicale", href: "/expertise-medicale", icon: FileSearch },
              { label: "Médecin conseil", href: "/medecin-conseil", icon: Shield },
              { label: "Protection juridique", href: "/protection-juridique", icon: Scale },
              { label: "Calcul IPP", href: "/calculatrice-ipp", icon: ClipboardList },
              { label: "Autre situation", href: "#diagnostic-form", icon: HelpCircle },
            ].map((c, i) => {
              const Wrapper = c.href.startsWith('#') ? 'a' : Link;
              const props = c.href.startsWith('#') ? { href: c.href } : { to: c.href };
              return (
                <Wrapper key={i} {...props} data-testid={`for-whom-card-${i}`}>
                  <div className="group p-4 rounded-xl bg-background border border-border/60 hover:border-accent/40 hover:bg-accent/[0.02] transition-colors duration-300 h-full flex flex-col gap-3">
                    <c.icon className="w-5 h-5 text-accent" strokeWidth={1.75} />
                    <p className="text-sm font-medium text-foreground group-hover:text-accent transition-colors">{c.label}</p>
                    <ArrowRight className="w-4 h-4 text-muted-foreground/40 group-hover:text-accent group-hover:translate-x-0.5 transition-all mt-auto" strokeWidth={2} />
                  </div>
                </Wrapper>
              );
            })}
          </div>
        </div>
      </section>

      {/* ENRICHMENT — Confidentialité RGPD */}
      <section className="section-padding" data-testid="simulateur-rgpd">
        <div className="max-w-3xl mx-auto">
          <div className="p-6 sm:p-8 rounded-2xl bg-muted/20 border border-border/50">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-6 h-6 text-accent" strokeWidth={1.75} />
              <h2 className="text-xl font-semibold">Confidentialité & protection de vos données</h2>
            </div>
            <ul className="space-y-2.5 text-sm text-muted-foreground">
              <li className="flex items-start gap-2.5"><CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={2} /><span>Aucune donnée médicale stockée sans votre accord explicite</span></li>
              <li className="flex items-start gap-2.5"><CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={2} /><span>Email facultatif — le rapport est téléchargeable directement</span></li>
              <li className="flex items-start gap-2.5"><CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={2} /><span>Aucune revente de données, aucun partenaire commercial</span></li>
              <li className="flex items-start gap-2.5"><CheckCircle className="w-4 h-4 text-accent flex-shrink-0 mt-0.5" strokeWidth={2} /><span>Suppression possible à la demande — droit d'accès et d'effacement RGPD</span></li>
            </ul>
          </div>
        </div>
      </section>

      {/* ENRICHMENT — FAQ */}
      <SimulateurFaq />

      {/* E-E-A-T Terrain Note */}
      <TerrainNote
        testId="simulateur-terrain-note"
        text="Ce diagnostic a été construit à partir des situations que j'accompagne réellement : AT/MP, MDPH, expertises, litiges d'assurance, protection juridique."
      />
    </main>
  );
};

const simulateurFaqData = [
  {
    question: "Combien de temps prend le diagnostic ?",
    answer: "Environ 5 minutes. Quelques questions ciblées suffisent à cerner votre contexte et à générer un rapport personnalisé. Vous pouvez revenir en arrière à tout moment pour ajuster vos réponses."
  },
  {
    question: "Est-ce vraiment gratuit ?",
    answer: "Oui, le diagnostic et le rapport sont entièrement gratuits. Il n'y a ni engagement, ni inscription obligatoire, ni prélèvement automatique. Vous pouvez télécharger votre rapport sans fournir d'email si vous préférez."
  },
  {
    question: "Que contient le rapport ?",
    answer: "Le rapport personnalisé contient : vos priorités stratégiques classées par urgence, les démarches à engager et leurs délais, les pièges identifiés sur votre situation, les ressources et guides recommandés, et une orientation vers l'accompagnement adapté si utile."
  },
  {
    question: "Mes données sont-elles confidentielles ?",
    answer: "Oui. Aucune donnée médicale n'est stockée sans votre accord explicite. Si vous ne fournissez pas d'email, rien n'est conservé côté serveur au-delà du temps de génération du rapport. Aucune revente, aucun partenaire commercial, et vous disposez d'un droit d'accès et d'effacement (RGPD)."
  },
  {
    question: "À quoi sert le résultat concrètement ?",
    answer: "Le diagnostic vous donne une feuille de route claire : quelles démarches engager, dans quel ordre, dans quels délais, et quels pièges éviter. Vous repartez avec un document actionnable — utile pour préparer un rendez-vous administratif, un recours, ou un échange avec un professionnel."
  },
  {
    question: "Dois-je créer un compte ?",
    answer: "Non. Le diagnostic se fait sans création de compte. Vous répondez aux questions, vous obtenez votre rapport, vous le téléchargez. Si vous souhaitez le recevoir par email, vous pouvez le faire — mais ce n'est jamais obligatoire."
  }
];

const SimulateurFaq = () => {
  const [openIndex, setOpenIndex] = useState(null);

  useEffect(() => {
    // Cleanup any existing FAQPage + HowTo schemas to avoid duplicates
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try {
        const t = JSON.parse(s.textContent)['@type'];
        if (t === 'FAQPage' || t === 'HowTo') s.remove();
      } catch {}
    });
    // Inject FAQPage
    const faqScript = document.createElement('script');
    faqScript.id = 'simulateur-faq-schema';
    faqScript.type = 'application/ld+json';
    faqScript.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": simulateurFaqData.map(f => ({
        "@type": "Question",
        "name": f.question,
        "acceptedAnswer": { "@type": "Answer", "text": f.answer }
      }))
    });
    document.head.appendChild(faqScript);
    // Inject HowTo
    const howtoScript = document.createElement('script');
    howtoScript.id = 'simulateur-howto-schema';
    howtoScript.type = 'application/ld+json';
    howtoScript.textContent = JSON.stringify({
      "@context": "https://schema.org",
      "@type": "HowTo",
      "name": "Comment obtenir votre diagnostic stratégique",
      "description": "Obtenez un diagnostic personnalisé en trois étapes simples sur votre situation AT/MP, MDPH, expertise ou protection juridique.",
      "step": [
        { "@type": "HowToStep", "position": 1, "name": "Répondez aux questions ciblées", "text": "Indiquez votre situation, l'état de vos démarches et votre contexte en quelques clics." },
        { "@type": "HowToStep", "position": 2, "name": "Laissez l'algorithme analyser", "text": "Le moteur croise vos réponses avec les règles CPAM, MDPH, AT/MP et les stratégies de recours éprouvées." },
        { "@type": "HowToStep", "position": 3, "name": "Recevez votre rapport personnalisé", "text": "Téléchargez immédiatement un document avec vos priorités, démarches, délais et pièges à éviter." }
      ]
    });
    document.head.appendChild(howtoScript);
    return () => {
      const faq = document.getElementById('simulateur-faq-schema');
      const howto = document.getElementById('simulateur-howto-schema');
      if (faq) faq.remove();
      if (howto) howto.remove();
    };
  }, []);

  return (
    <section className="section-padding bg-secondary/20" data-testid="simulateur-faq">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl sm:text-3xl font-semibold mb-8 text-center">Questions fréquentes</h2>
        <div className="space-y-2">
          {simulateurFaqData.map((faq, i) => (
            <div key={i} className="border border-border rounded-xl overflow-hidden bg-background">
              <button
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/30 transition-colors"
                data-testid={`simulateur-faq-${i}`}
              >
                <span className="font-medium text-sm text-foreground pr-4">{faq.question}</span>
                <ChevronDown className={`w-4 h-4 text-muted-foreground shrink-0 transition-transform ${openIndex === i ? 'rotate-180' : ''}`} />
              </button>
              {openIndex === i && (
                <div className="px-4 pb-4">
                  <p className="text-sm text-muted-foreground leading-relaxed">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
