"""Tests for routes/payments.py — Stripe + PayPal endpoints."""
import pytest

API = "/api"


class TestPaymentPackages:
    def test_list_packages(self, client):
        resp = client.get(f"{API}/payments/packages")
        assert resp.status_code == 200
        pkgs = resp.json()
        assert len(pkgs) == 10
        for pkg in pkgs:
            assert "id" in pkg
            assert "name" in pkg
            assert "amount" in pkg
            assert pkg["amount"] > 0

    def test_package_names_in_french(self, client):
        resp = client.get(f"{API}/payments/packages")
        names = [p["name"] for p in resp.json()]
        assert any("Analyse" in n for n in names)
        assert any("MDPH" in n for n in names)


class TestPayPal:
    def test_calculate_amount(self, client):
        resp = client.post(f"{API}/paypal/calculate", json={
            "package_id": "analyse_dossier", "customer_email": "new@test.com"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["final_amount"] == 150.0
        assert data["discount_percent"] == 0

    def test_calculate_invalid_package(self, client):
        resp = client.post(f"{API}/paypal/calculate", json={"package_id": "nonexistent"})
        assert resp.status_code == 400


class TestCheckoutValidation:
    def test_checkout_invalid_package(self, client):
        resp = client.post(f"{API}/payments/checkout", json={
            "package_id": "nonexistent", "origin_url": "https://test.com"
        })
        assert resp.status_code == 400
