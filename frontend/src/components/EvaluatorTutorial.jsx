import { PlayCircle } from 'lucide-react';

const STEPS = [
  {
    t: 'Commencez par le cas fictif',
    d: "Téléchargez les documents proposés ci-dessus (« Un cas fictif prêt à tester »), puis déposez-les dans Dossier Express IA via le bouton « Démarrer le test ».",
  },
  {
    t: 'Plusieurs documents = une seule analyse',
    d: "Quand plusieurs fichiers constituent le même dossier, déposez-les ensemble dans une même analyse plutôt que de lancer une analyse par document. L'outil traite alors l'ensemble comme un dossier cohérent : il reconstitue mieux la chronologie, croise les informations entre documents, repère les pièces manquantes, identifie les incohérences et hiérarchise les points d'attention.",
  },
  {
    t: 'Limites techniques',
    d: "Jusqu'à 10 fichiers par analyse, 50 Mo maximum par fichier et 100 Mo au total. Formats acceptés : PDF, images (JPG, PNG), Word et Excel.",
  },
  {
    t: 'Dossier réel : pas nécessaire',
    d: "Un dossier professionnel réel n'est absolument pas nécessaire pour la première analyse : le cas fictif permet de tester intégralement le parcours. Si vous souhaitez ensuite utiliser un dossier réel, anonymisez-le au préalable par vos soins (aucun nom, NIR, adresse ou élément identifiant) — les documents déposés restent confidentiels et ne servent qu'à votre analyse.",
  },
  {
    t: "Lancez l'analyse",
    d: "L'outil extrait, structure et analyse les éléments documentaires, puis produit un rapport avec les points d'attention et les sources correspondantes.",
  },
  {
    t: 'Lisez le résultat',
    d: "Le rapport (PDF) vous est envoyé par email, à l'adresse de votre invitation. Vérifiez particulièrement : les informations extraites, les citations, la chronologie, les pièces manquantes ou problématiques, les points procéduraux — et ce que l'outil n'a volontairement PAS conclu.",
  },
];

export const EvaluatorTutorial = () => (
  <section className="mb-10" data-testid="eval-tutorial">
    <h2 className="text-lg md:text-lg font-semibold mb-4 text-[#C9A84C] flex items-center gap-2">
      <PlayCircle className="w-4 h-4" /> Votre premier test, en 2 minutes
    </h2>
    <ol className="space-y-3">
      {STEPS.map((s, i) => (
        <li key={i} className="flex gap-3 p-3.5 rounded-xl border border-white/8 bg-white/[0.02]" data-testid={`eval-tuto-step-${i + 1}`}>
          <span className="w-6 h-6 rounded-full bg-[#C9A84C]/15 border border-[#C9A84C]/40 text-[#C9A84C] text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">{i + 1}</span>
          <div>
            <p className="text-sm font-medium text-[#f5f0e8] mb-0.5">{s.t}</p>
            <p className="text-xs text-[#f5f0e8]/55 leading-relaxed">{s.d}</p>
          </div>
        </li>
      ))}
    </ol>
    <div className="mt-4 p-4 rounded-xl border-2 border-[#C9A84C]/50 bg-[#C9A84C]/10" data-testid="eval-tuto-consigne">
      <p className="text-sm text-[#f5f0e8] leading-relaxed font-medium">
        « L'objectif de votre test n'est pas de constater que l'outil fonctionne, mais de vérifier ce qu'il apporte
        réellement à votre travail, ce qu'il fait correctement et surtout les situations dans lesquelles il pourrait
        vous induire en erreur ou vous faire perdre du temps. »
      </p>
    </div>
  </section>
);
