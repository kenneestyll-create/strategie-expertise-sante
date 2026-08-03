"""Integration tests: end-to-end workflows spanning multiple modules."""
import pytest
import uuid

API = "/api"


class TestClientFullWorkflow:
    """Test complete client journey: register → login → upload doc → check progress → notifications."""

    def test_complete_client_journey(self, client):
        email = f"pytest-integ-{uuid.uuid4().hex[:8]}@test.com"

        # 1. Register
        resp = client.post(f"{API}/client/register", json={
            "email": email, "password": "IntegTest123!", "name": "Integ User",
            "notifications_email": True, "notifications_push": True
        })
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        client_id = resp.json()["client_id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get profile
        resp = client.get(f"{API}/client/profile", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == email

        # 3. Check initial progress (should show inscription completed)
        resp = client.get(f"{API}/client/progress", headers=headers)
        assert resp.status_code == 200
        progress = resp.json()
        assert progress["progress_pct"] > 0
        assert progress["steps"][0]["status"] == "completed"
        assert progress["steps"][0]["id"] == "inscription"

        # 4. Upload a document
        resp = client.post(f"{API}/client/documents", json={
            "filename": "attestation_at.pdf", "file_data": "base64data",
            "mime_type": "application/pdf", "size": 5000,
            "ocr_fields": {"dates": ["15/03/2025"], "type_dossier_detected": ["at"]},
            "tags": {"categorie": "at"}
        }, headers=headers)
        assert resp.status_code == 200
        doc_id = resp.json()["document"]["id"]
        doc_category = resp.json()["document"]["category"]
        assert doc_category == "at"

        # 5. List documents — should have 1
        resp = client.get(f"{API}/client/documents", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["by_category"]["at"] == 1

        # 6. Upload more documents
        for i, cat in enumerate(["mp", "expertise"]):
            resp = client.post(f"{API}/client/documents", json={
                "filename": f"doc_{cat}_{i}.pdf", "file_data": "base64data",
                "mime_type": "application/pdf", "size": 3000,
                "tags": {"categorie": cat}
            }, headers=headers)
            assert resp.status_code == 200

        # 7. Check progress again (documents step should advance)
        resp = client.get(f"{API}/client/progress", headers=headers)
        assert resp.status_code == 200
        progress2 = resp.json()
        doc_step = next(s for s in progress2["steps"] if s["id"] == "documents")
        assert doc_step["count"] == 3
        assert progress2["summary"]["total_documents"] == 3

        # 8. Filter documents by category
        resp = client.get(f"{API}/client/documents?category=at", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()["documents"]) >= 1

        # 9. Update document category
        resp = client.patch(f"{API}/client/documents/{doc_id}", json={
            "category": "mp", "tags": {"organisme": "CPAM"}
        }, headers=headers)
        assert resp.status_code == 200

        # 10. Check notifications
        resp = client.get(f"{API}/client/notifications", headers=headers)
        assert resp.status_code == 200

        # 11. Update notification settings
        resp = client.patch(f"{API}/client/settings/notifications", json={
            "notifications_email": False
        }, headers=headers)
        assert resp.status_code == 200

        resp = client.get(f"{API}/client/settings/notifications", headers=headers)
        assert resp.json()["notifications_email"] is False

        # 12. Delete documents and verify
        resp = client.get(f"{API}/client/documents", headers=headers)
        for doc in resp.json()["documents"]:
            client.delete(f"{API}/client/documents/{doc['id']}", headers=headers)

        resp = client.get(f"{API}/client/documents", headers=headers)
        assert resp.json()["total"] == 0

        # 13. Login again with same credentials
        resp = client.post(f"{API}/client/login", json={"email": email, "password": "IntegTest123!"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()


class TestAdminFullWorkflow:
    """Test admin journey: login → view stats → manage contacts → manage avis → analytics."""

    def test_admin_dashboard_workflow(self, client, admin_headers):
        # 1. View stats
        resp = client.get(f"{API}/admin/stats", headers=admin_headers)
        assert resp.status_code == 200
        initial_total = resp.json()["total"]

        # 2. Create a contact (public)
        resp = client.post(f"{API}/contact", json={
            "nom": "IntegTest", "prenom": "Admin", "email": "integ-admin@test.com",
            "sujet": "Test intégration", "message": "Message de test."
        })
        assert resp.status_code == 200
        contact_id = resp.json()["id"]

        # 3. View updated stats
        resp = client.get(f"{API}/admin/stats", headers=admin_headers)
        assert resp.json()["total"] >= initial_total + 1

        # 4. Get the contact
        resp = client.get(f"{API}/admin/contacts/{contact_id}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "nouveau"

        # 5. Update contact status
        resp = client.patch(f"{API}/admin/contacts/{contact_id}", json={"status": "en_cours"}, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "en_cours"

        # 6. View analytics
        resp = client.get(f"{API}/admin/analytics?period=7d", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["kpis"]["total_contacts"] > 0

        # 7. Create and manage an avis
        resp = client.post(f"{API}/avis", json={
            "nom": "IntegTest", "note": 5, "commentaire": "Excellent service.",
            "consent_publication": True, "consent_data_processing": True
        })
        assert resp.status_code == 200
        avis_id = resp.json()["id"]

        # Approve it
        resp = client.patch(f"{API}/admin/avis/{avis_id}", json={"status": "publie"}, headers=admin_headers)
        assert resp.status_code == 200

        # Verify it appears in public avis
        resp = client.get(f"{API}/avis")
        avis_list = resp.json()
        assert any(a["id"] == avis_id for a in avis_list)

        # 8. Create and delete FAQ
        resp = client.post(f"{API}/admin/faq", json={
            "question": "Integration test?", "reponse": "Answer.", "categorie": "Test"
        }, headers=admin_headers)
        faq_id = resp.json()["id"]
        resp = client.delete(f"{API}/admin/faq/{faq_id}", headers=admin_headers)
        assert resp.status_code == 200

        # Cleanup
        client.delete(f"{API}/admin/contacts/{contact_id}", headers=admin_headers)
        client.delete(f"{API}/admin/avis/{avis_id}", headers=admin_headers)


class TestForumFullWorkflow:
    """Test forum journey: register → create topic → reply → like → report."""

    def test_forum_conversation(self, client):
        # 1. Register two users
        user1_pseudo = f"integ-u1-{uuid.uuid4().hex[:4]}"
        resp = client.post(f"{API}/forum/register", json={
            "pseudo": user1_pseudo, "email": f"{user1_pseudo}@test.com",
            "password": "Pass123!", "is_anonymous": False
        })
        assert resp.status_code == 200
        u1_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        user2_pseudo = f"integ-u2-{uuid.uuid4().hex[:4]}"
        resp = client.post(f"{API}/forum/register", json={
            "pseudo": user2_pseudo, "email": f"{user2_pseudo}@test.com",
            "password": "Pass123!", "is_anonymous": False
        })
        u2_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        # 2. User1 creates a topic
        resp = client.post(f"{API}/forum/topics", json={
            "category_id": "accident-travail",
            "title": "Integration test topic",
            "content": "Content from integration test."
        }, headers=u1_headers)
        assert resp.status_code == 200
        topic_id = resp.json()["topic_id"]

        # 3. User2 replies
        resp = client.post(f"{API}/forum/topics/{topic_id}/replies", json={
            "content": "Reply from user 2."
        }, headers=u2_headers)
        assert resp.status_code == 200
        reply_id = resp.json()["reply_id"]

        # 4. User1 likes the reply
        resp = client.post(f"{API}/forum/replies/{reply_id}/like", headers=u1_headers)
        assert resp.status_code == 200
        assert resp.json()["liked"] is True

        # 5. User2 likes the topic
        resp = client.post(f"{API}/forum/topics/{topic_id}/like", headers=u2_headers)
        assert resp.status_code == 200
        assert resp.json()["liked"] is True

        # 6. Read the topic (should have 1 reply)
        resp = client.get(f"{API}/forum/topics/{topic_id}")
        assert resp.status_code == 200
        assert len(resp.json()["replies"]) >= 1

        # 7. User1 reports the reply
        resp = client.post(f"{API}/forum/report", json={
            "target_type": "reply", "target_id": reply_id, "reason": "Test report"
        }, headers=u1_headers)
        assert resp.status_code == 200

        # 8. Admin views reports
        admin_resp = client.post(f"{API}/auth/login", json={
            "email": "admin@accompagn-sante.fr", "password": "Admin2024!"
        })
        admin_h = {"Authorization": f"Bearer {admin_resp.json()['access_token']}"}

        resp = client.get(f"{API}/admin/forum/reports?status=pending", headers=admin_h)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

        # 9. List topics by category
        resp = client.get(f"{API}/forum/topics?category_id=accident-travail")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


class TestPaymentAndDiscountWorkflow:
    """Test discount calculation flow: create referral → validate → calculate discounted price."""

    def test_referral_discount_flow(self, client):
        # 1. Create a referral code
        owner_email = f"owner-{uuid.uuid4().hex[:6]}@test.com"
        resp = client.post(f"{API}/referral/create", json={"email": owner_email, "name": "Owner"})
        assert resp.status_code == 200
        code = resp.json()["code"]

        # 2. Validate it
        resp = client.get(f"{API}/referral/validate/{code}")
        assert resp.status_code == 200
        assert resp.json()["valid"] is True
        assert resp.json()["discount"] == 10

        # 3. Retrieve same code for same owner
        resp = client.post(f"{API}/referral/create", json={"email": owner_email})
        assert resp.json()["code"] == code

        # 4. Calculate PayPal amount with referral
        resp = client.post(f"{API}/paypal/calculate", json={
            "package_id": "analyse_dossier", "customer_email": "newclient@test.com",
            "referral_code": code
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["discount_percent"] == 10
        assert data["final_amount"] == 135.0  # 150 * 0.9

    def test_loyalty_discount(self, client):
        # 1. Record an order for a client
        email = f"loyal-{uuid.uuid4().hex[:6]}@test.com"
        resp = client.post(f"{API}/client/record-order?email={email}&name=Loyal")
        assert resp.status_code == 200

        # 2. Check discount
        resp = client.get(f"{API}/client/discount/{email}")
        assert resp.status_code == 200
        assert resp.json()["loyalty_discount"] == 15

        # 3. PayPal calculate should use loyalty
        resp = client.post(f"{API}/paypal/calculate", json={
            "package_id": "analyse_dossier", "customer_email": email
        })
        assert resp.status_code == 200
        assert resp.json()["discount_percent"] == 15
        assert resp.json()["final_amount"] == 127.5  # 150 * 0.85


class TestDocumentValidationAndOCR:
    """Test document validation + OCR field extraction pipeline."""

    def test_validation_and_extraction_pipeline(self, client):
        # 1. Validate a PDF
        resp = client.post(f"{API}/documents/validate", json={
            "filename": "rapport_cpam.pdf", "size": 500000, "mime_type": "application/pdf"
        })
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

        # 2. Validate rejected formats
        for ext, mime in [("exe", "application/octet-stream"), ("bat", "text/plain")]:
            resp = client.post(f"{API}/documents/validate", json={
                "filename": f"bad.{ext}", "size": 1000, "mime_type": mime
            })
            assert resp.json()["valid"] is False

        # 3. OCR field extraction — comprehensive text
        ocr_text = """
        CPAM de Paris
        Dossier N° AT-2025-98765
        Assuré: Jean DUPONT
        Numéro de sécurité sociale: 1 85 12 75 123 456 78
        Date de l'accident du travail: 15/03/2025
        Date de consolidation: 20/09/2025
        Taux IPP: 15%
        Indemnité: 2 500,00 €
        Remboursement: 750 €
        """
        resp = client.post(f"{API}/documents/extract-fields", json={"text": ocr_text})
        assert resp.status_code == 200
        fields = resp.json()["fields"]

        assert "dates" in fields
        assert len(fields["dates"]) >= 2
        assert "montants" in fields
        assert len(fields["montants"]) >= 1
        assert "references" in fields
        assert "numero_ss" in fields
        assert "noms" in fields
        assert "taux_ipp" in fields
        assert 15 in fields["taux_ipp"]
        assert "type_dossier_detected" in fields
        assert "at" in fields["type_dossier_detected"]

    def test_client_uploads_with_ocr_tags(self, client):
        # Register a client
        email = f"ocr-integ-{uuid.uuid4().hex[:6]}@test.com"
        resp = client.post(f"{API}/client/register", json={
            "email": email, "password": "OcrTest123!", "name": "OCR Tester"
        })
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        # Upload with OCR fields — category auto-detection
        resp = client.post(f"{API}/client/documents", json={
            "filename": "decision_mdph.pdf", "file_data": "base64data",
            "mime_type": "application/pdf", "size": 8000,
            "ocr_fields": {
                "dates": ["01/06/2025"],
                "type_dossier_detected": ["mdph"],
                "noms": ["Jean Dupont"],
                "references": ["MDPH-2025-001"]
            },
            "tags": {}
        }, headers=headers)
        assert resp.status_code == 200
        doc = resp.json()["document"]
        assert doc["category"] == "mdph"
        assert "MDPH-2025-001" in doc["tags"]["references"]


class TestCasAnonymisesAndScoring:
    """Test cas anonymisés import → scoring pipeline."""

    def test_import_and_score(self, client, admin_headers):
        # 1. Import cases
        resp = client.post(f"{API}/admin/cas-anonymises/import", json={
            "cases": [
                {"type_dossier": "pytest_integ", "regime": "general", "resultat": "favorable", "score_pertinence": 80, "strategie": "CRA"},
                {"type_dossier": "pytest_integ", "regime": "general", "resultat": "favorable", "score_pertinence": 90, "strategie": "CRA"},
                {"type_dossier": "pytest_integ", "regime": "general", "resultat": "défavorable", "score_pertinence": 40, "strategie": "Tribunal"},
                {"type_dossier": "pytest_integ", "regime": "general", "resultat": "favorable", "score_pertinence": 75, "strategie": "CRA"},
                {"type_dossier": "pytest_integ", "regime": "general", "resultat": "en cours", "score_pertinence": 60, "strategie": "Tribunal"},
            ]
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["imported"] == 5

        # 2. Get score
        resp = client.get(f"{API}/strategiia/score?type_dossier=pytest_integ&regime=general")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_cases"] >= 5
        assert data["score"] is not None
        assert data["confidence"] in ("low", "medium", "high")
        assert data["distribution"]["favorable"] >= 3
        assert data["distribution"]["defavorable"] >= 1
        assert len(data["top_strategies"]) >= 1
        assert data["top_strategies"][0]["strategie"] == "CRA"

        # 3. Stats
        resp = client.get(f"{API}/admin/cas-anonymises/stats", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 5


class TestBookingAndSimulatorWorkflow:
    """Test booking + simulator integration."""

    def test_booking_and_slots(self, client):
        import uuid
        # Use a unique far-future date to avoid collisions with other test runs
        import random
        from datetime import datetime, timedelta
        d = datetime.now() + timedelta(days=random.randint(400, 900))
        while d.weekday() >= 5:
            d += timedelta(days=1)
        unique_date = d.strftime("%Y-%m-%d")

        # 1. Check available slots for a future date
        resp = client.get(f"{API}/bookings/slots/{unique_date}")
        assert resp.status_code == 200
        slots = resp.json()["slots"]
        initial_count = len(slots)
        assert initial_count > 0  # At least some slots available

        # 2. Book a slot (pick the first available)
        slot_to_book = slots[0]
        unique_email = f"book-{uuid.uuid4().hex[:8]}@test.com"
        resp = client.post(f"{API}/bookings", json={
            "date": unique_date, "time_slot": slot_to_book,
            "name": "BookTest", "email": unique_email,
            "type_accompagnement": "AT"
        })
        assert resp.status_code == 200

        # 3. Check slots again — one less
        resp = client.get(f"{API}/bookings/slots/{unique_date}")
        assert slot_to_book not in resp.json()["slots"]
        assert len(resp.json()["slots"]) == initial_count - 1

    def test_simulator_and_calculator(self, client):
        # 1. Save simulator result
        resp = client.post(f"{API}/simulator/result", json={
            "answers": {"situation": "at", "anciennete": "5ans"},
            "profile": "AT confirmé",
            "recommendations": ["Analyse de dossier", "Expertise médicale"],
            "droits": ["Indemnités journalières", "Rente IPP"],
            "demarches": ["Déclaration CPAM", "Recours CRA"]
        })
        assert resp.status_code == 200

        # 2. Track calculator usage
        resp = client.post(f"{API}/calculator/track", json={"type": "ipp"})
        assert resp.status_code == 200

        resp = client.post(f"{API}/calculator/track", json={"type": "aah"})
        assert resp.status_code == 200

        # 3. Get weekly count
        resp = client.get(f"{API}/calculator/count")
        assert resp.status_code == 200
        assert resp.json()["count"] >= 2
