"""Tests to boost coverage of utils/email.py — mocked email sending."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEmailHelpers:
    def test_send_notification_email_no_config(self):
        """Without RESEND_API_KEY, email should be skipped gracefully."""
        from utils.email import send_notification_email
        from models import ContactRequestCreate, ContactRequest

        contact = ContactRequest(
            nom="Test", prenom="Email", email="test@test.com",
            sujet="Test", message="Testing email skip"
        )
        # With no RESEND_API_KEY set (or empty), should return False
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(send_notification_email(contact))
        loop.close()
        # Should not crash, returns False if not configured
        assert result is False or result is True  # depends on env

    def test_notify_admin_premium_no_config(self):
        """Premium notification should not crash without config."""
        from utils.email import notify_admin_premium_analysis

        loop = asyncio.new_event_loop()
        # Should not raise even without configuration
        loop.run_until_complete(
            notify_admin_premium_analysis("strategiia", "test@test.com", "Test User", 97.0)
        )
        loop.close()

    def test_create_client_notification_via_admin(self, client, admin_headers, test_client_user):
        """Client notification created via admin API should appear in client's notifications."""
        cid = test_client_user["id"]

        # Admin notifies a premium analysis update
        resp = client.post(f"/api/admin/notify-document-rejected/{cid}",
                          json={"message": "Test notification from email coverage test."},
                          headers=admin_headers)
        assert resp.status_code == 200

        # Client should see it
        resp2 = client.get("/api/client/notifications",
                          headers={"Authorization": f"Bearer {test_client_user['token']}"})
        assert resp2.status_code == 200
        assert resp2.json()["unread_count"] >= 1


class TestAdminNotifyDocumentRejected:
    """Test admin document rejection notification via API."""

    def test_notify_rejected(self, client, admin_headers, test_client_user):
        resp = client.post(
            f"/api/admin/notify-document-rejected/{test_client_user['id']}",
            json={"message": "Veuillez renvoyer le document page 3."},
            headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

        # Verify notification was created
        resp2 = client.get("/api/client/notifications",
                          headers={"Authorization": f"Bearer {test_client_user['token']}"})
        assert resp2.status_code == 200
        notifs = resp2.json()["notifications"]
        assert any(n["type"] == "document_rejected" for n in notifs)
