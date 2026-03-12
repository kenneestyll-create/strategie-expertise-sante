import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { 
  ArrowRight, 
  ArrowLeft, 
  CheckCircle, 
  AlertTriangle, 
  HelpCircle,
  FileSearch,
  Shield,
  Users,
  Scale,
  ClipboardList
} from 'lucide-react';
import axios from 'axios';

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
  const situation = answers.situation;
  const demarche = answers.demarche;
  const besoin = answers.besoin;
  const accompagnement = answers.accompagnement;
  const anciennete = answers.anciennete;

  let profile = '';
  let urgency = 'normal';
  let recommendations = [];
  let services = [];

  // Determine profile
  if (situation === 'at' || situation === 'mp') {
    profile = 'Victime d\'accident du travail ou maladie professionnelle';
    services.push({ id: 'analyse_dossier', label: 'Analyse de dossier' });
    if (demarche === 'refus' || demarche === 'recours') {
      urgency = 'important';
      recommendations.push("Votre situation nécessite une analyse approfondie de votre dossier pour identifier les points de contestation.");
      recommendations.push("Un accompagnement pour la préparation d'un recours peut significativement améliorer vos chances.");
      services.push({ id: 'preparation_expertise', label: 'Préparation expertise médicale' });
    }
    if (demarche === 'expertise') {
      urgency = 'urgent';
      recommendations.push("La préparation à une expertise médicale est essentielle. Ne la négligez pas.");
      services.push({ id: 'preparation_expertise', label: 'Préparation expertise médicale' });
    }
    if (demarche === 'debut') {
      recommendations.push("Il est important de bien démarrer vos démarches avec un dossier solide dès le début.");
    }
  } else if (situation === 'mdph') {
    profile = 'Demande MDPH';
    services.push({ id: 'accompagnement_mdph', label: 'Accompagnement MDPH' });
    recommendations.push("Le dossier MDPH requiert une attention particulière dans sa constitution.");
    if (demarche === 'refus') {
      recommendations.push("Un refus MDPH peut être contesté. Il est important d'analyser les motifs pour préparer un recours adapté.");
      urgency = 'important';
    }
  } else if (situation === 'assurance') {
    profile = 'Litige assurantiel';
    services.push({ id: 'protection_juridique', label: 'Protection juridique' });
    recommendations.push("Vérifiez si votre contrat inclut une protection juridique qui pourrait couvrir vos frais.");
    if (anciennete === 'long' || anciennete === 'tres_long') {
      urgency = 'important';
      recommendations.push("La durée de votre situation suggère un dossier complexe. Un accompagnement personnalisé est recommandé.");
    }
  } else if (situation === 'expertise') {
    profile = 'Préparation expertise médicale';
    urgency = 'urgent';
    services.push({ id: 'preparation_expertise', label: 'Préparation expertise médicale' });
    recommendations.push("La préparation à une expertise est cruciale pour faire valoir vos droits correctement.");
  } else {
    profile = 'Situation spécifique';
    recommendations.push("Votre situation mérite une analyse personnalisée lors d'un premier échange gratuit.");
  }

  // General recommendations
  if (accompagnement === 'seul') {
    recommendations.push("Vous n'êtes pas accompagné(e). Un regard expert sur votre situation peut faire une réelle différence.");
    if (besoin === 'global') {
      services.push({ id: 'accompagnement_complet', label: 'Accompagnement complet' });
    }
  }

  if (besoin === 'comprendre') {
    recommendations.push("Un premier échange gratuit vous permettra de mieux comprendre vos droits et les démarches possibles.");
  }

  if (recommendations.length === 0) {
    recommendations.push("Votre situation mérite un échange personnalisé pour définir la meilleure stratégie.");
  }

  return { profile, urgency, recommendations, services };
};

export const SimulateurPage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [email, setEmail] = useState('');
  const [saving, setSaving] = useState(false);

  const handleAnswer = (questionId, value) => {
    const newAnswers = { ...answers, [questionId]: value };
    setAnswers(newAnswers);

    if (currentStep < QUESTIONS.length - 1) {
      setTimeout(() => setCurrentStep(currentStep + 1), 300);
    } else {
      setTimeout(() => setShowResults(true), 300);
    }
  };

  const handleSaveResult = async () => {
    const result = getResults(answers);
    setSaving(true);
    try {
      await axios.post(`${API}/simulator/result`, {
        answers,
        profile: result.profile,
        recommendations: result.recommendations,
        email: email || null
      });
      toast.success("Résultat enregistré ! Nous vous recontacterons.");
    } catch { toast.error("Erreur lors de l'enregistrement"); }
    finally { setSaving(false); }
  };

  const restart = () => {
    setCurrentStep(0);
    setAnswers({});
    setShowResults(false);
    setEmail('');
  };

  const results = showResults ? getResults(answers) : null;
  const progress = showResults ? 100 : ((currentStep) / QUESTIONS.length) * 100;

  return (
    <main className="page-transition pt-20">
      <section className="section-padding bg-secondary">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-3xl">
            <span className="text-sm font-medium text-accent uppercase tracking-wider">Simulateur</span>
            <h1 className="text-4xl sm:text-5xl font-semibold mt-2 mb-6" data-testid="simulator-title">
              Évaluez votre situation
            </h1>
            <p className="text-lg text-muted-foreground">
              Répondez à quelques questions pour obtenir une première évaluation de votre situation
              et des recommandations personnalisées.
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

          {!showResults ? (
            /* Questions */
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
                          : 'border-border hover:border-accent/50 hover:bg-muted/30'
                        }
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
          ) : (
            /* Results */
            <div data-testid="simulator-results">
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
                  <p className="text-sm mt-1 text-muted-foreground">Profil identifié : <strong>{results.profile}</strong></p>
                </div>
              </div>

              <h2 className="text-xl font-semibold mb-4">Nos recommandations</h2>
              <div className="space-y-3 mb-8">
                {results.recommendations.map((rec, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-muted/30 rounded-lg">
                    <ClipboardList className="w-4 h-4 text-accent flex-shrink-0 mt-1" strokeWidth={1.5} />
                    <p className="text-sm">{rec}</p>
                  </div>
                ))}
              </div>

              {results.services.length > 0 && (
                <div className="mb-8">
                  <h3 className="font-semibold mb-3">Services recommandés</h3>
                  <div className="flex flex-wrap gap-2">
                    {results.services.map((s) => (
                      <Link key={s.id} to="/tarifs">
                        <span className="inline-flex items-center gap-1 bg-accent/10 text-accent px-3 py-1.5 rounded-full text-sm font-medium hover:bg-accent/20 transition-colors">
                          <ArrowRight className="w-3 h-3" />
                          {s.label}
                        </span>
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Save & Contact */}
              <Card className="border-border">
                <CardContent className="p-6">
                  <h3 className="font-semibold mb-2">Recevoir une analyse personnalisée</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Laissez votre email pour que je vous recontacte avec une analyse plus détaillée de votre situation.
                  </p>
                  <div className="flex gap-2">
                    <Input value={email} onChange={e => setEmail(e.target.value)} placeholder="votre@email.fr" type="email" className="flex-1" data-testid="result-email" />
                    <Button onClick={handleSaveResult} disabled={saving || !email} className="gap-2" data-testid="save-result-button">
                      {saving ? 'Envoi...' : 'Envoyer'}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <div className="flex flex-col sm:flex-row gap-3 mt-6">
                <Link to="/contact" className="flex-1">
                  <Button className="w-full rounded-lg gap-2" data-testid="result-contact-button">
                    Prendre contact <ArrowRight className="w-4 h-4" />
                  </Button>
                </Link>
                <Link to="/agenda" className="flex-1">
                  <Button variant="outline" className="w-full rounded-lg gap-2" data-testid="result-agenda-button">
                    Prendre rendez-vous <ArrowRight className="w-4 h-4" />
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
