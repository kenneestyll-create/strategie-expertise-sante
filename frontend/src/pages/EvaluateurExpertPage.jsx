import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { SEO } from '@/components/SEO';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';
import { ShieldCheck, FileSearch, ScanSearch, FileCheck2, AlertTriangle, ArrowRight, Loader2, Lock, Download, FileText } from 'lucide-react';
import { ExpertEvaluationGrid } from '@/components/ExpertEvaluationGrid';
import { EvaluatorTutorial } from '@/components/EvaluatorTutorial';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function EvaluateurExpertPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('t') || '';
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [access, setAccess] = useState(null);

  useEffect(() => {
    try {
      const stored = JSON.parse(sessionStorage.getItem('expert_access') || 'null');
      if (stored && stored.token === token) setAccess(stored);
    } catch { /* ignore */ }
  }, [token]);

  const verify = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API}/expert-access/verify`, { token, email: email.trim() });
      const data = { ...res.data, token };
      sessionStorage.setItem('expert_access', JSON.stringify(data));
      setAccess(data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Vérification impossible");
    } finally {
      setLoading(false);
    }
  };

  const startTest = () => navigate('/dossier-express');

  if (!token) {
    return (
      <main className="min-h-screen bg-[#0a0a08] flex items-center justify-center px-4">
        <SEO title="Espace évaluateur" description="Accès réservé" path="/evaluation-expert" noindex={true} />
        <Card className="w-full max-w-md bg-white/[0.03] border-white/10" data-testid="eval-no-token">
          <CardContent className="p-8 text-center">
            <Lock className="w-8 h-8 text-[#C9A84C] mx-auto mb-4" />
            <p className="text-[#f5f0e8] font-medium mb-2">Espace réservé aux évaluateurs invités</p>
            <p className="text-sm text-[#f5f0e8]/50">L'accès nécessite un lien d'invitation personnel. Si vous avez été invité, utilisez le lien reçu par email.</p>
          </CardContent>
        </Card>
      </main>
    );
  }

  if (!access) {
    return (
      <main className="min-h-screen bg-[#0a0a08] flex items-center justify-center px-4">
        <SEO title="Espace évaluateur" description="Accès réservé" path="/evaluation-expert" noindex={true} />
        <Card className="w-full max-w-md bg-white/[0.03] border-white/10" data-testid="eval-login-card">
          <CardContent className="p-8">
            <p className="text-[11px] font-medium text-[#C9A84C] uppercase tracking-[0.2em] mb-2">Programme d'évaluation</p>
            <h1 className="text-xl font-semibold text-[#f5f0e8] mb-1" style={{ fontFamily: "'Playfair Display', serif" }}>Dossier Express IA</h1>
            <p className="text-sm text-[#f5f0e8]/50 mb-6">Confirmez l'adresse email à laquelle vous avez reçu l'invitation.</p>
            <form onSubmit={verify} className="space-y-4">
              <div>
                <Label htmlFor="eval-email" className="text-[#f5f0e8]/70 text-sm">Votre adresse email</Label>
                <Input id="eval-email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
                  className="mt-1.5 bg-white/5 border-white/10 text-[#f5f0e8]" placeholder="docteur@exemple.fr" data-testid="eval-email-input" />
              </div>
              <Button type="submit" disabled={loading || !email.trim()} className="w-full bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-medium" data-testid="eval-verify-button">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Accéder à mon espace'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </main>
    );
  }

  const steps = [
    { icon: FileSearch, t: 'Extraction', d: 'Lecture des documents déposés (OCR).' },
    { icon: ScanSearch, t: 'Contrôle qualité', d: 'Les pages illisibles sont détectées et signalées avant toute analyse.' },
    { icon: ShieldCheck, t: 'Analyse', d: "Analyse stratégique du dossier par IA, encadrée par des bases de connaissances métier." },
    { icon: FileCheck2, t: 'Citations vérifiées', d: 'Chaque citation du rapport est vérifiée programmatiquement contre le document source.' },
  ];

  return (
    <main className="min-h-screen bg-[#0a0a08] text-[#f5f0e8]" data-testid="eval-space">
      <SEO title="Espace évaluateur" description="Accès réservé" path="/evaluation-expert" noindex={true} />
      <div className="max-w-3xl mx-auto px-5 sm:px-8 py-14">
        <p className="text-[11px] font-medium text-[#C9A84C] uppercase tracking-[0.2em] mb-3">Programme d'évaluation expert</p>
        <h1 className="text-3xl sm:text-4xl font-semibold mb-2" style={{ fontFamily: "'Playfair Display', serif" }} data-testid="eval-welcome">
          Bienvenue, {access.name}
        </h1>
        <p className="text-[#f5f0e8]/60 mb-10 text-sm">
          Cet espace vous est réservé. Temps total estimé : environ 1 heure, en deux temps, à votre rythme.
        </p>

        <section className="mb-10">
          <h2 className="text-lg md:text-lg font-semibold mb-3 text-[#C9A84C]">Le concept en trois phrases</h2>
          <p className="text-sm text-[#f5f0e8]/75 leading-relaxed">
            Dossier Express IA s'adresse aux victimes d'accidents du travail, de maladies professionnelles ou de litiges
            assurantiels. La personne dépose ses documents (notification de refus, certificats, courriers CPAM) et reçoit
            une analyse stratégique structurée de son dossier, avec citations tracées vers les pièces sources.
            Ce service est vendu 97&nbsp;€ aux particuliers — votre accès d'évaluation est gratuit et n'entre dans aucune statistique commerciale.
          </p>
        </section>

        <section className="mb-10 p-5 rounded-xl border border-red-400/20 bg-red-500/5" data-testid="eval-what-not">
          <h2 className="text-lg md:text-lg font-semibold mb-3 text-[#f5f0e8]">Ce que cet outil n'est pas</h2>
          <ul className="space-y-1.5 text-sm text-[#f5f0e8]/70">
            <li>— Ce n'est pas un dispositif médical, ni un outil de diagnostic.</li>
            <li>— Il ne rend aucun avis médical et ne se substitue ni à un médecin, ni à un expert, ni à un avocat.</li>
            <li>— C'est un outil d'aide à la structuration du dossier, en amont des démarches et expertises.</li>
          </ul>
        </section>

        <section className="mb-10 p-5 sm:p-6 rounded-xl border border-[#C9A84C]/25 bg-white/[0.02]" data-testid="eval-professional-value">
          <h2 className="text-lg md:text-lg font-semibold mb-3 text-[#C9A84C]">Ce que l'outil peut vous apporter, concrètement</h2>
          <p className="text-sm text-[#f5f0e8]/75 leading-relaxed mb-4">
            « Dossier Express IA ne cherche pas à remplacer l'expertise du professionnel. Il cherche à lui faire gagner
            du temps sur le travail documentaire qui précède son expertise, afin qu'il puisse consacrer davantage de son
            temps à ce qui relève réellement de son jugement professionnel. »
          </p>
          <p className="text-xs text-[#f5f0e8]/50 mb-3">Pendant votre test, voici les gains concrets à mesurer :</p>
          <ul className="grid sm:grid-cols-2 gap-x-6 gap-y-1.5 text-sm text-[#f5f0e8]/70 mb-5">
            <li>— Réduction du temps de première lecture d'un dossier volumineux</li>
            <li>— Vision structurée et chronologique des éléments documentaires</li>
            <li>— Identification rapide des pièces manquantes, illisibles ou problématiques</li>
            <li>— Repérage des incohérences documentaires</li>
            <li>— Identification et hiérarchisation des points procéduraux à vérifier</li>
            <li>— Traçabilité des informations et de leurs sources documentaires</li>
            <li>— Préparation plus rapide d'un dossier avant votre propre travail d'expertise</li>
          </ul>
          {access.profile_type === 'medecin_expert' && (
            <div className="p-4 rounded-lg border border-white/8 bg-white/[0.02]" data-testid="eval-medecin-note">
              <p className="text-xs text-[#f5f0e8]/65 leading-relaxed italic">
                « L'outil ne se prononce pas sur le diagnostic, la gravité d'un état psychiatrique, l'imputabilité
                médicale ou toute autre conclusion clinique. Son intérêt potentiel est ailleurs : vous permettre
                d'arriver plus rapidement à une compréhension structurée du dossier documentaire et vous laisser
                ensuite exercer pleinement votre propre jugement. »
              </p>
            </div>
          )}
          <p className="text-[11px] text-[#f5f0e8]/35 mt-3">Aucun gain de temps chiffré n'est avancé : nous n'avons pas encore de mesure objective — c'est précisément ce que votre évaluation aidera à établir.</p>
        </section>

        <section className="mb-10">
          <h2 className="text-lg md:text-lg font-semibold mb-4 text-[#C9A84C]">La méthode, en quatre étapes</h2>
          <div className="grid sm:grid-cols-2 gap-3">
            {steps.map((s, i) => (
              <div key={i} className="p-4 rounded-xl border border-white/8 bg-white/[0.02]">
                <s.icon className="w-4 h-4 text-[#C9A84C] mb-2" />
                <p className="text-sm font-medium mb-1">{i + 1}. {s.t}</p>
                <p className="text-xs text-[#f5f0e8]/50 leading-relaxed">{s.d}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-10" data-testid="eval-limits">
          <h2 className="text-lg md:text-lg font-semibold mb-3 text-[#f5f0e8] flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-[#C9A84C]" /> Limites connues, assumées
          </h2>
          <ul className="space-y-1.5 text-sm text-[#f5f0e8]/70">
            <li>— Aucune validation clinique à ce jour : c'est précisément l'objet de ce programme d'évaluation.</li>
            <li>— La qualité de l'analyse dépend de la qualité des documents fournis (le contrôle qualité le signale, il ne le corrige pas).</li>
            <li>— Périmètre : AT/MP, MDPH, litiges assurantiels. Hors périmètre : dommage corporel pur, contentieux ordinal.</li>
          </ul>
        </section>

        <section className="mb-10 p-5 sm:p-6 rounded-xl border border-white/10 bg-white/[0.02]" data-testid="eval-demo-case">
          <div className="flex items-center gap-3 flex-wrap mb-3">
            <h2 className="text-lg md:text-lg font-semibold text-[#C9A84C]">Un cas fictif prêt à tester</h2>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border border-red-400/40 text-red-300 bg-red-500/10">Cas fictif de démonstration</span>
          </div>
          <p className="text-sm text-[#f5f0e8]/75 leading-relaxed mb-4">
            Pour vous éviter d'anonymiser un dossier réel, nous avons préparé un cas entièrement fictif, proche de votre
            pratique : <strong className="text-[#f5f0e8]">Mme DEMONSTRATION Claire, 45 ans</strong> — épisode dépressif
            caractérisé sévère en lien évoqué avec le travail, maladie hors tableau (art. L.461-1 CSS), refus CPAM au
            motif d'un taux d'IPP prévisible de 20&nbsp;% (inférieur au seuil de 25&nbsp;% requis pour saisir le CRRMP).
            Six pièces, dont un scan volontairement dégradé pour éprouver le contrôle qualité.
          </p>
          <ul className="space-y-1.5 text-xs text-[#f5f0e8]/60 mb-5">
            {[
              ['1-certificat-medical-initial.pdf', 'Certificat médical initial (épisode dépressif sévère, MP hors tableau)'],
              ['2-notification-refus-cpam.pdf', 'Notification de refus CPAM (IPP prévisible 20 % < 25 %, CRRMP non saisi)'],
              ['3-compte-rendu-psychiatrique.pdf', 'Compte rendu de suivi psychiatrique (PHQ-9, imputabilité professionnelle)'],
              ['4-arret-travail-scan-degrade.pdf', "Arrêt de travail — scan volontairement flou (test du contrôle qualité)"],
              ['5-elements-contexte-professionnel.pdf', 'Attestation et éléments de contexte professionnel (IRP)'],
              ['6-courrier-medecin-conseil.pdf', 'Courrier du médecin-conseil (évaluation du taux prévisible)'],
            ].map(([file, label], i) => (
              <li key={file} className="flex items-start gap-2">
                <FileText className="w-3.5 h-3.5 text-[#C9A84C]/70 mt-0.5 shrink-0" />
                <a href={`/cas-demonstration/${file}`} target="_blank" rel="noreferrer" className="hover:text-[#C9A84C] underline decoration-white/20 underline-offset-2" data-testid={`eval-demo-doc-${i + 1}`}>{label}</a>
              </li>
            ))}
          </ul>
          <div className="flex items-center gap-4 flex-wrap">
            <Button asChild variant="outline" className="border-[#C9A84C]/40 text-[#C9A84C] hover:bg-[#C9A84C]/10 hover:text-[#C9A84C] gap-2">
              <a href="/cas-demonstration/cas-demonstration-complet.zip" download data-testid="eval-demo-zip-download">
                <Download className="w-4 h-4" /> Télécharger le dossier complet (.zip)
              </a>
            </Button>
            <p className="text-[11px] text-[#f5f0e8]/40">6 PDF · chaque page porte le filigrane «&nbsp;CAS FICTIF DE DÉMONSTRATION&nbsp;»</p>
          </div>
          <div className="mt-5 p-4 rounded-lg border border-white/8 bg-white/[0.02]" data-testid="eval-demo-perimeter">
            <p className="text-xs text-[#f5f0e8]/65 leading-relaxed">
              <strong className="text-[#f5f0e8]">Périmètre volontairement strict&nbsp;:</strong> sur ce cas comme sur tout autre,
              l'outil analyse l'organisation documentaire et les éléments procéduraux (délais, voies de recours, pièces
              manquantes). Il ne porte aucun jugement clinique, ne discute aucun diagnostic et ne remplace jamais
              l'expertise psychiatrique. C'est précisément ce respect du périmètre que nous vous demandons d'éprouver.
            </p>
          </div>
        </section>

        <EvaluatorTutorial />

        <ExpertEvaluationGrid token={token} email={access.email} />

        <section className="p-6 rounded-xl border border-[#C9A84C]/30 bg-[#C9A84C]/5" data-testid="eval-start-section">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="font-medium mb-1">Commencer le test</p>
              <p className="text-xs text-[#f5f0e8]/50">
                Analyses restantes : <strong className="text-[#C9A84C]" data-testid="eval-quota">{access.quota_remaining} / {access.quota_analyses}</strong>
                {' '}· Accès valable jusqu'au {new Date(access.expires_at).toLocaleDateString('fr-FR')}
              </p>
              <p className="text-xs text-[#f5f0e8]/40 mt-1">Testez avec le cas fictif ci-dessus, ou un cas de votre choix (anonymisé par vos soins). N'hésitez pas à chercher à mettre l'outil en défaut : vos critiques, consignées dans la grille, sont le livrable attendu.</p>
            </div>
            <Button onClick={startTest} disabled={access.quota_remaining <= 0} className="bg-[#C9A84C] hover:bg-[#b8963e] text-[#0a0a08] font-medium gap-2" data-testid="eval-start-button">
              Démarrer le test <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
          {access.quota_remaining <= 0 && (
            <p className="text-xs text-[#f5f0e8]/50 mt-3">Quota épuisé — contactez-nous si vous souhaitez poursuivre l'évaluation : contact@strategie-expertise-sante.fr</p>
          )}
        </section>

        <p className="text-[11px] text-[#f5f0e8]/30 mt-8">
          Votre évaluation reste strictement confidentielle. Votre nom ne sera jamais cité sans votre accord écrit.
          Les dossiers soumis dans cet espace sont marqués comme tests et exclus de toute statistique.
        </p>
      </div>
    </main>
  );
}
