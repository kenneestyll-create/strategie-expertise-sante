/**
 * Encart E-E-A-T discret affichant l'ancrage terrain de l'auteur.
 * À placer APRÈS la FAQ sur les pages piliers.
 * Design : fond neutre léger, pulse dorée à gauche, texte italic.
 */
export const TerrainNote = ({ text, testId }) => {
  return (
    <section className="px-4 sm:px-6 lg:px-8 pb-12 sm:pb-14" data-testid={testId || 'terrain-note'}>
      <div className="max-w-3xl mx-auto">
        <div className="relative flex items-start gap-4 p-5 rounded-xl bg-muted/20 border border-border/40">
          <div className="relative flex-shrink-0 mt-1.5">
            <span className="block w-2 h-2 rounded-full bg-accent" />
            <span className="absolute inset-0 w-2 h-2 rounded-full bg-accent animate-ping opacity-60" />
          </div>
          <p className="text-sm text-muted-foreground italic leading-relaxed">
            {text}
          </p>
        </div>
      </div>
    </section>
  );
};
