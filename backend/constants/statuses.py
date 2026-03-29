"""
CONSOLIDATION_ARCHITECTURE — Constantes de statuts centralisées.
Source unique de vérité pour TOUS les statuts utilisés dans le système.
Toute modification de statut DOIT passer par ce fichier.
"""


# ========== SERVICES ==========
class Service:
    """Identifiants uniques des deux services. Utilisés dans premium_analyses.type, logs, emails."""
    STRATEGIIA = "strategiia"
    DOSSIER_EXPRESS = "dossier_express"

    ALL = (STRATEGIIA, DOSSIER_EXPRESS)


# ========== STATUTS DOSSIER EXPRESS (collection: dossier_express) ==========
class DossierStatus:
    """Statut principal du dossier (champ 'status')."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class DossierDelivery:
    """Statut de livraison (champ 'delivery_status')."""
    EN_ATTENTE = "en_attente_traitement"
    INCIDENT = "incident_technique"
    LIVRE = "livre_client"
    GENERE_SANS_EMAIL = "genere_sans_email"


class DossierStep:
    """Étape de traitement granulaire (champ 'processing_step')."""
    CHECKOUT_VALIDE = "checkout_valide"
    RELANCE_ADMIN = "relance_admin"
    DOCUMENTS_RECUS = "documents_recus"
    EXTRACTION = "extraction_en_cours"
    ANALYSE_IA = "analyse_ia"
    PDF_EN_COURS = "pdf_en_cours"
    STOCKAGE = "stockage_en_cours"
    EMAIL = "email_en_cours"
    TERMINE = "termine"
    ERREUR_IA = "erreur_ia"
    ERREUR_PDF = "erreur_pdf"
    ERREUR_STOCKAGE = "erreur_stockage"
    ERREUR_EMAIL = "erreur_email"


# ========== STATUTS PREMIUM ANALYSES (collection: premium_analyses) ==========
class PremiumStatus:
    """Statut de la file de relecture admin (champ 'status')."""
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    ENVOYE = "envoye"
    TERMINE = "termine"

    # Statuts qui apparaissent dans le badge admin "à relire"
    PENDING_REVIEW = (EN_ATTENTE, EN_COURS)
    # Statuts qui indiquent un workflow terminé
    COMPLETED = (VALIDE, ENVOYE, TERMINE)


# ========== STATUTS STRATEGIIA ASYNC JOBS (in-memory _jobs) ==========
class JobStatus:
    PENDING = "pending"
    DONE = "done"
    ERROR = "error"


# ========== MAPPING ÉTAPES CLIENT (Suivi Dossier Express) ==========
DOSSIER_STEP_CLIENT_MAP = {
    DossierStep.CHECKOUT_VALIDE:     {"order": 1, "label": "Dossier bien recu"},
    DossierStep.RELANCE_ADMIN:       {"order": 1, "label": "Dossier bien recu"},
    DossierStep.DOCUMENTS_RECUS:     {"order": 2, "label": "Documents en cours de preparation"},
    DossierStep.EXTRACTION:          {"order": 3, "label": "Lecture documentaire en cours"},
    DossierStep.ANALYSE_IA:          {"order": 4, "label": "Analyse en cours de finalisation"},
    DossierStep.PDF_EN_COURS:        {"order": 5, "label": "Rapport en cours de preparation"},
    DossierStep.STOCKAGE:            {"order": 6, "label": "Rapport en cours de preparation"},
    DossierStep.EMAIL:               {"order": 7, "label": "Envoi en cours"},
    DossierStep.TERMINE:             {"order": 8, "label": "Rapport disponible"},
    DossierStep.ERREUR_IA:           {"order": 4, "label": "Verification complementaire en cours"},
    DossierStep.ERREUR_PDF:          {"order": 5, "label": "Verification complementaire en cours"},
    DossierStep.ERREUR_STOCKAGE:     {"order": 6, "label": "Verification complementaire en cours"},
    DossierStep.ERREUR_EMAIL:        {"order": 7, "label": "Verification complementaire en cours"},
}

CLIENT_STEPS_DISPLAY = [
    {"key": "received",    "label": "Dossier bien recu"},
    {"key": "preparation", "label": "Documents en cours de preparation"},
    {"key": "reading",     "label": "Lecture documentaire en cours"},
    {"key": "analysis",    "label": "Analyse en cours de finalisation"},
    {"key": "report",      "label": "Rapport en cours de preparation"},
    {"key": "delivery",    "label": "Envoi en cours"},
    {"key": "available",   "label": "Rapport disponible"},
]
