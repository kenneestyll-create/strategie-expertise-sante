/**
 * timeline.js — Scene Engine V1 (option P1.B validée)
 *
 * Reconstruction des chunks proportionnellement à la durée audio TTS réelle.
 * On NE consomme PAS les timestamps SRT bruts (drift jusqu'à 1s).
 * On répartit chaque phrase du script sur la timeline audio en fonction
 * de son poids en mots (≈ proportionnel au temps de prononciation).
 *
 * Précision empirique : ~95% (drift < 300ms sur scripts FR de 30-60s).
 */

/**
 * Découpe un script en phrases, allouant à chacune une fenêtre [start, end]
 * proportionnelle au nombre de mots, sur la durée audio totale.
 *
 * @param {string} script - texte brut généré par Claude
 * @param {number} audioDurationSec - durée réelle du MP3 voix-off
 * @returns {Array<{idx,text,wordCount,startSec,endSec,durationSec}>}
 */
export function buildChunksFromAudio(script, audioDurationSec) {
  if (!script || !audioDurationSec || audioDurationSec <= 0) return [];
  // Split sur points + ! + ? tout en conservant la ponctuation finale
  const raw = script
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
  if (raw.length === 0) return [];

  // Pondérer par nb de mots
  const wordCounts = raw.map((s) => s.split(/\s+/).filter(Boolean).length);
  const totalWords = wordCounts.reduce((a, b) => a + b, 0) || 1;

  const chunks = [];
  let cursor = 0;
  for (let i = 0; i < raw.length; i++) {
    const dur = (wordCounts[i] / totalWords) * audioDurationSec;
    chunks.push({
      idx: i,
      text: raw[i],
      wordCount: wordCounts[i],
      startSec: cursor,
      endSec: cursor + dur,
      durationSec: dur,
    });
    cursor += dur;
  }
  // Cale la fin du dernier chunk exactement sur audioDurationSec
  if (chunks.length > 0) {
    chunks[chunks.length - 1].endSec = audioDurationSec;
    chunks[chunks.length - 1].durationSec =
      audioDurationSec - chunks[chunks.length - 1].startSec;
  }
  return chunks;
}

/**
 * Convertit des chunks en cues d'animation.
 * Chaque cue déclenche une animation au début d'un chunk (time = startSec).
 *
 * @param {Array} chunks
 * @returns {Array<{time:number, chunkIdx:number, text:string}>}
 */
export function chunksToCues(chunks) {
  return chunks.map((c) => ({
    time: c.startSec,
    chunkIdx: c.idx,
    text: c.text,
    durationSec: c.durationSec,
  }));
}

/**
 * Trouve le chunk actif à un instant donné.
 */
export function findActiveChunk(chunks, audioTime) {
  for (let i = chunks.length - 1; i >= 0; i--) {
    if (audioTime >= chunks[i].startSec) return chunks[i];
  }
  return chunks[0] || null;
}

/**
 * Helper pour les scenes : `if (cue.fired) return;` + déclenchement unique.
 * Renvoie true UNE SEULE FOIS dès que audioTime >= cue.time.
 */
export class CueTracker {
  constructor(cues) {
    this.cues = cues || [];
    this.fired = new Set();
  }
  reset() {
    this.fired = new Set();
  }
  /** Renvoie l'index du dernier cue franchi à audioTime, ou -1 si aucun */
  current(audioTime) {
    let last = -1;
    for (let i = 0; i < this.cues.length; i++) {
      if (audioTime >= this.cues[i].time) last = i;
      else break;
    }
    return last;
  }
  /** True une seule fois quand audioTime franchit le cue idx */
  trigger(idx, audioTime) {
    if (this.fired.has(idx)) return false;
    if (audioTime >= (this.cues[idx]?.time ?? Infinity)) {
      this.fired.add(idx);
      return true;
    }
    return false;
  }
}
