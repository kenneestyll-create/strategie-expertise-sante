/**
 * register.js — Scene Engine V1
 * Enregistre les scenes disponibles auprès du SceneFactory.
 * À enrichir au fil des sprints.
 */
import { SceneFactory } from './SceneFactory.js';
import { StatsFocusScene } from './scenes/stats_focus.js';
import { AlertUrgencyScene } from './scenes/alert_urgency.js';

// Sprint 2 — 2 scenes
SceneFactory.register('stats_focus', StatsFocusScene);
SceneFactory.register('alert_urgency', AlertUrgencyScene);

// Sprint 3 ajoutera : legal_balance, office_admin, testimony_quote

export { SceneFactory };
