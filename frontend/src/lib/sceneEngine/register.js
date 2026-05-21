/**
 * register.js — Scene Engine V1
 * Enregistre les scenes disponibles auprès du SceneFactory.
 * Sprint 2 : stats_focus, alert_urgency
 * Sprint 3 : legal_balance, office_admin, testimony_quote → couverture F1-F7 complète
 */
import { SceneFactory } from './SceneFactory.js';
import { StatsFocusScene } from './scenes/stats_focus.js';
import { AlertUrgencyScene } from './scenes/alert_urgency.js';
import { LegalBalanceScene } from './scenes/legal_balance.js';
import { OfficeAdminScene } from './scenes/office_admin.js';
import { TestimonyQuoteScene } from './scenes/testimony_quote.js';

// Sprint 2
SceneFactory.register('stats_focus', StatsFocusScene);
SceneFactory.register('alert_urgency', AlertUrgencyScene);

// Sprint 3
SceneFactory.register('legal_balance', LegalBalanceScene);
SceneFactory.register('office_admin', OfficeAdminScene);
SceneFactory.register('testimony_quote', TestimonyQuoteScene);

export { SceneFactory };
