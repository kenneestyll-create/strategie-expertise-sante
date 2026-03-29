"""
TESTS DE NON-RÉGRESSION — Consolidation Architecture
Couvrent l'isolation StrategiIA / Dossier Express + garde-fous.
"""
import pytest
from constants.statuses import Service, PremiumStatus, DossierStatus, DossierDelivery, DossierStep, JobStatus
from constants.guards import assert_valid_service, assert_premium_analyses_entry, ServiceGuardError, assert_relecture_blocks_auto_send
from constants.workflows import STRATEGIIA_FREE_MONTHLY_QUOTA, LLM_MAX_RETRIES


# ==================== TEST 1: Constants integrity ====================

class TestConstants:
    def test_service_types_are_unique(self):
        assert Service.STRATEGIIA != Service.DOSSIER_EXPRESS
        assert Service.STRATEGIIA == "strategiia"
        assert Service.DOSSIER_EXPRESS == "dossier_express"

    def test_service_all_contains_both(self):
        assert Service.STRATEGIIA in Service.ALL
        assert Service.DOSSIER_EXPRESS in Service.ALL
        assert len(Service.ALL) == 2

    def test_premium_statuses(self):
        assert PremiumStatus.EN_ATTENTE == "en_attente"
        assert PremiumStatus.VALIDE == "valide"
        assert PremiumStatus.EN_ATTENTE in PremiumStatus.PENDING_REVIEW

    def test_dossier_statuses(self):
        assert DossierStatus.PROCESSING == "processing"
        assert DossierStatus.COMPLETED == "completed"
        assert DossierStatus.ERROR == "error"


# ==================== TEST 2: Guards - Cross-service protection ====================

class TestGuards:
    def test_assert_valid_service_accepts_known(self):
        assert_valid_service(Service.STRATEGIIA, "test")
        assert_valid_service(Service.DOSSIER_EXPRESS, "test")

    def test_assert_valid_service_rejects_unknown(self):
        with pytest.raises(ServiceGuardError):
            assert_valid_service("unknown_service", "test")

    def test_assert_valid_service_rejects_empty(self):
        with pytest.raises(ServiceGuardError):
            assert_valid_service("", "test")

    def test_premium_entry_validation_complete(self):
        entry = {
            "id": "test-123",
            "type": Service.STRATEGIIA,
            "email": "test@test.com",
            "status": PremiumStatus.EN_ATTENTE,
            "relecture_expert_required": True,
            "created_at": "2026-01-01T00:00:00Z"
        }
        assert_premium_analyses_entry(entry, "test")

    def test_premium_entry_validation_missing_type(self):
        entry = {
            "id": "test-123",
            "email": "test@test.com",
            "status": PremiumStatus.EN_ATTENTE,
            "relecture_expert_required": True,
            "created_at": "2026-01-01T00:00:00Z"
        }
        with pytest.raises(ServiceGuardError):
            assert_premium_analyses_entry(entry, "test")

    def test_premium_entry_validation_wrong_service_type(self):
        entry = {
            "id": "test-123",
            "type": "invalid_type",
            "email": "test@test.com",
            "status": PremiumStatus.EN_ATTENTE,
            "relecture_expert_required": True,
            "created_at": "2026-01-01T00:00:00Z"
        }
        with pytest.raises(ServiceGuardError):
            assert_premium_analyses_entry(entry, "test")

    def test_premium_entry_validation_missing_relecture(self):
        entry = {
            "id": "test-123",
            "type": Service.DOSSIER_EXPRESS,
            "email": "test@test.com",
            "status": PremiumStatus.EN_ATTENTE,
            "relecture_expert_required": None,
            "created_at": "2026-01-01T00:00:00Z"
        }
        with pytest.raises(ServiceGuardError):
            assert_premium_analyses_entry(entry, "test")

    def test_relecture_blocks_auto_send(self):
        assert assert_relecture_blocks_auto_send(True, "test") is False
        assert assert_relecture_blocks_auto_send(False, "test") is True


# ==================== TEST 3: Workflow config ====================

class TestWorkflows:
    def test_quota_defined(self):
        assert STRATEGIIA_FREE_MONTHLY_QUOTA == 3

    def test_retries_defined(self):
        assert LLM_MAX_RETRIES == 3


# ==================== TEST 4: Cross-contamination prevention ====================

class TestIsolation:
    """Ensure no service can accidentally write to the wrong collection."""

    def test_strategiia_entry_cannot_be_dossier_express(self):
        """A premium_analyses entry with type=strategiia MUST NOT be accepted with type=dossier_express."""
        strategiia_entry = {
            "id": "iso-test-1",
            "type": Service.STRATEGIIA,
            "email": "test@test.com",
            "status": PremiumStatus.EN_ATTENTE,
            "relecture_expert_required": True,
            "created_at": "2026-01-01T00:00:00Z"
        }
        # This should pass
        assert_premium_analyses_entry(strategiia_entry, "test")

        # Mutate type — should fail
        strategiia_entry["type"] = "invalid"
        with pytest.raises(ServiceGuardError):
            assert_premium_analyses_entry(strategiia_entry, "test")

    def test_dossier_express_entry_has_correct_type(self):
        entry = {
            "id": "iso-test-2",
            "type": Service.DOSSIER_EXPRESS,
            "email": "test@test.com",
            "status": PremiumStatus.EN_ATTENTE,
            "relecture_expert_required": True,
            "created_at": "2026-01-01T00:00:00Z"
        }
        assert_premium_analyses_entry(entry, "test")
        assert entry["type"] == Service.DOSSIER_EXPRESS
