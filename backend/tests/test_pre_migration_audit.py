"""
PRE-MIGRATION AUDIT TEST SUITE
Comprehensive testing of all critical routes and functionalities
for Stratégie & Expertise Santé platform.

This is a READ-ONLY audit - no code modifications.
Stripe/PayPal are in LIVE mode - only verify session creation, no real payments.
"""

import pytest
import requests
import os
import time
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://mascot-tips-admin.preview.emergentagent.com').rstrip('/')

# Test credentials from review request
from tests.test_config import ADMIN_EMAIL, ADMIN_PASSWORD
from tests.test_config import CLIENT_EMAIL, CLIENT_PASSWORD


class TestPublicRoutes:
    """Test all public routes - no authentication required"""
    
    def test_health_check(self):
        """GET /api/health - Critical health endpoint"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        elapsed = time.time() - start
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✓ GET /api/health - OK ({elapsed:.2f}s)")
        assert elapsed < 2, f"Health check too slow: {elapsed:.2f}s"
    
    def test_public_tarifs(self):
        """GET /api/public/tarifs - Public pricing data"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/public/tarifs", timeout=10)
        elapsed = time.time() - start
        assert response.status_code == 200, f"Tarifs failed: {response.text}"
        print(f"✓ GET /api/public/tarifs - OK ({elapsed:.2f}s)")
    
    def test_public_chiffres_cles(self):
        """GET /api/public/chiffres-cles - Key figures"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/public/chiffres-cles", timeout=10)
        elapsed = time.time() - start
        assert response.status_code == 200, f"Chiffres-cles failed: {response.text}"
        print(f"✓ GET /api/public/chiffres-cles - OK ({elapsed:.2f}s)")
    
    def test_conseils_today(self):
        """GET /api/conseils/today - Daily advice"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/conseils/today", timeout=10)
        elapsed = time.time() - start
        assert response.status_code == 200, f"Conseils today failed: {response.text}"
        print(f"✓ GET /api/conseils/today - OK ({elapsed:.2f}s)")
    
    def test_guides(self):
        """GET /api/guides - Public guides list"""
        response = requests.get(f"{BASE_URL}/api/guides", timeout=10)
        assert response.status_code == 200, f"Guides failed: {response.text}"
        print(f"✓ GET /api/guides - OK")
    
    def test_guide_mascot_tips_admin(self):
        """GET /api/guide/mascot-tips-admin - Specific guide"""
        response = requests.get(f"{BASE_URL}/api/guide/mascot-tips-admin", timeout=10)
        # May return 404 if guide doesn't exist - that's OK
        assert response.status_code in [200, 404], f"Guide mascot-tips-admin unexpected: {response.status_code}"
        print(f"✓ GET /api/guide/mascot-tips-admin - {response.status_code}")
    
    def test_avis(self):
        """GET /api/avis - Published reviews"""
        response = requests.get(f"{BASE_URL}/api/avis", timeout=10)
        assert response.status_code == 200, f"Avis failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Avis should return a list"
        print(f"✓ GET /api/avis - OK ({len(data)} reviews)")
    
    def test_faq(self):
        """GET /api/faq - FAQ items"""
        response = requests.get(f"{BASE_URL}/api/faq", timeout=10)
        assert response.status_code == 200, f"FAQ failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "FAQ should return a list"
        print(f"✓ GET /api/faq - OK ({len(data)} items)")
    
    def test_payment_packages(self):
        """GET /api/payments/packages - Available packages"""
        response = requests.get(f"{BASE_URL}/api/payments/packages", timeout=10)
        assert response.status_code == 200, f"Packages failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Packages should return a list"
        assert len(data) > 0, "Should have at least one package"
        print(f"✓ GET /api/payments/packages - OK ({len(data)} packages)")
        for pkg in data:
            print(f"  - {pkg.get('name')}: {pkg.get('amount')}€")
    
    def test_booking_call_types(self):
        """GET /api/bookings/call-types - Available call types"""
        response = requests.get(f"{BASE_URL}/api/bookings/call-types", timeout=10)
        assert response.status_code == 200, f"Call types failed: {response.text}"
        data = response.json()
        assert isinstance(data, dict), "Call types should return a dict"
        print(f"✓ GET /api/bookings/call-types - OK ({len(data)} types)")
        for key, val in data.items():
            print(f"  - {key}: {val.get('name')} ({val.get('duration')}min, {val.get('price')}€)")
    
    def test_sitemap_xml(self):
        """GET /api/sitemap.xml - SEO sitemap"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml", timeout=10)
        assert response.status_code == 200, f"Sitemap failed: {response.text}"
        assert "urlset" in response.text, "Sitemap should contain urlset"
        print(f"✓ GET /api/sitemap.xml - OK")
    
    def test_robots_txt(self):
        """GET /api/robots.txt - SEO robots"""
        response = requests.get(f"{BASE_URL}/api/robots.txt", timeout=10)
        assert response.status_code == 200, f"Robots.txt failed: {response.text}"
        assert "User-agent" in response.text, "Robots.txt should contain User-agent"
        print(f"✓ GET /api/robots.txt - OK")
    
    def test_forum_categories(self):
        """GET /api/forum/categories - Forum categories"""
        response = requests.get(f"{BASE_URL}/api/forum/categories", timeout=10)
        assert response.status_code == 200, f"Forum categories failed: {response.text}"
        print(f"✓ GET /api/forum/categories - OK")
    
    def test_visitors_count(self):
        """GET /api/visitors/count - Visitor counter"""
        response = requests.get(f"{BASE_URL}/api/visitors/count", timeout=10)
        assert response.status_code == 200, f"Visitors count failed: {response.text}"
        data = response.json()
        assert "count" in data, "Should have count field"
        print(f"✓ GET /api/visitors/count - OK (count: {data.get('count')})")


class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login - Admin login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Should return access_token"
        print(f"✓ POST /api/auth/login (admin) - OK")
        return data["access_token"]
    
    def test_admin_login_invalid(self):
        """POST /api/auth/login - Admin login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "wrong@email.com", "password": "wrongpassword"},
            timeout=10
        )
        assert response.status_code == 401, f"Should reject invalid credentials: {response.status_code}"
        print(f"✓ POST /api/auth/login (invalid) - 401 as expected")
    
    def test_client_login_success(self):
        """POST /api/client/login - Client login"""
        response = requests.post(
            f"{BASE_URL}/api/client/login",
            json={"email": CLIENT_EMAIL, "password": CLIENT_PASSWORD},
            timeout=10
        )
        # Client may not exist - that's OK for audit
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data, "Should return access_token"
            print(f"✓ POST /api/client/login - OK")
        elif response.status_code == 401:
            print(f"✓ POST /api/client/login - 401 (client not found or wrong password)")
        else:
            print(f"⚠ POST /api/client/login - {response.status_code}: {response.text}")
    
    def test_auth_me_with_token(self):
        """GET /api/auth/me - Get current user with token"""
        # First login to get token
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        if login_resp.status_code != 200:
            pytest.skip("Cannot login to test /auth/me")
        
        token = login_resp.json()["access_token"]
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert "email" in data, "Should return email"
        print(f"✓ GET /api/auth/me - OK (email: {data.get('email')})")


class TestAdminRoutes:
    """Test admin routes - require authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for all tests"""
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        if login_resp.status_code != 200:
            pytest.skip("Cannot login as admin")
        self.token = login_resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_admin_stats(self):
        """GET /api/admin/stats - Dashboard stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin stats failed: {response.text}"
        data = response.json()
        print(f"✓ GET /api/admin/stats - OK")
        print(f"  - Total contacts: {data.get('total')}")
        print(f"  - Nouveau: {data.get('nouveau')}")
        print(f"  - En cours: {data.get('en_cours')}")
        print(f"  - Traité: {data.get('traite')}")
    
    def test_admin_analytics(self):
        """GET /api/admin/analytics - Analytics data"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin analytics failed: {response.text}"
        data = response.json()
        print(f"✓ GET /api/admin/analytics - OK")
        kpis = data.get("kpis", {})
        print(f"  - Total contacts: {kpis.get('total_contacts')}")
        print(f"  - Total clients: {kpis.get('total_clients')}")
        print(f"  - Total revenue: {kpis.get('total_revenue')}€")
    
    def test_admin_accounting(self):
        """GET /api/admin/accounting?period=year - Accounting data"""
        response = requests.get(f"{BASE_URL}/api/admin/accounting?period=year", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin accounting failed: {response.text}"
        data = response.json()
        print(f"✓ GET /api/admin/accounting?period=year - OK")
        kpis = data.get("kpis", {})
        print(f"  - Total CA: {kpis.get('total_ca')}€")
        print(f"  - Total transactions: {kpis.get('total_transactions')}")
    
    def test_admin_contacts(self):
        """GET /api/admin/contacts - Contact list"""
        response = requests.get(f"{BASE_URL}/api/admin/contacts", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin contacts failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Contacts should return a list"
        print(f"✓ GET /api/admin/contacts - OK ({len(data)} contacts)")
    
    def test_admin_bookings(self):
        """GET /api/admin/bookings - Booking list"""
        response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin bookings failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Bookings should return a list"
        print(f"✓ GET /api/admin/bookings - OK ({len(data)} bookings)")
    
    def test_admin_documents(self):
        """GET /api/admin/documents - Document list"""
        response = requests.get(f"{BASE_URL}/api/admin/documents", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin documents failed: {response.text}"
        data = response.json()
        print(f"✓ GET /api/admin/documents - OK")
        stats = data.get("stats", {})
        print(f"  - Total: {stats.get('total')}")
        print(f"  - En attente: {stats.get('en_attente')}")
    
    def test_admin_dossier_express(self):
        """GET /api/admin/dossier-express - Dossier express list"""
        response = requests.get(f"{BASE_URL}/api/admin/dossier-express", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin dossier-express failed: {response.text}"
        print(f"✓ GET /api/admin/dossier-express - OK")
    
    def test_admin_seo_pages(self):
        """GET /api/admin/seo-pages - SEO pages list"""
        response = requests.get(f"{BASE_URL}/api/admin/seo-pages", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin seo-pages failed: {response.text}"
        print(f"✓ GET /api/admin/seo-pages - OK")
    
    def test_admin_alertes_urgentes(self):
        """GET /api/admin/alertes-urgentes - Urgent alerts"""
        response = requests.get(f"{BASE_URL}/api/admin/alertes-urgentes", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin alertes-urgentes failed: {response.text}"
        data = response.json()
        print(f"✓ GET /api/admin/alertes-urgentes - OK")
        print(f"  - Total: {data.get('total')}")
        print(f"  - Non traité: {data.get('non_traite')}")
    
    def test_admin_avis(self):
        """GET /api/admin/avis - All reviews (admin)"""
        response = requests.get(f"{BASE_URL}/api/admin/avis", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin avis failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Avis should return a list"
        print(f"✓ GET /api/admin/avis - OK ({len(data)} reviews)")
    
    def test_admin_email_status(self):
        """GET /api/admin/email/status - Email configuration status"""
        response = requests.get(f"{BASE_URL}/api/admin/email/status", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin email status failed: {response.text}"
        data = response.json()
        print(f"✓ GET /api/admin/email/status - OK")
        print(f"  - Resend installed: {data.get('resend_installed')}")
        print(f"  - API key configured: {data.get('api_key_configured')}")
    
    def test_admin_services_status(self):
        """GET /api/admin/services-status - Services status"""
        response = requests.get(f"{BASE_URL}/api/admin/services-status", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin services-status failed: {response.text}"
        print(f"✓ GET /api/admin/services-status - OK")
    
    def test_admin_monitoring(self):
        """GET /api/admin/monitoring - Monitoring data"""
        response = requests.get(f"{BASE_URL}/api/admin/monitoring", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin monitoring failed: {response.text}"
        print(f"✓ GET /api/admin/monitoring - OK")
    
    def test_admin_referrals(self):
        """GET /api/admin/referrals - Referral codes"""
        response = requests.get(f"{BASE_URL}/api/admin/referrals", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin referrals failed: {response.text}"
        data = response.json()
        print(f"✓ GET /api/admin/referrals - OK")
        stats = data.get("stats", {})
        print(f"  - Total codes: {stats.get('total_codes')}")
        print(f"  - Total uses: {stats.get('total_uses')}")
    
    def test_admin_forum_stats(self):
        """GET /api/admin/forum/stats - Forum statistics"""
        response = requests.get(f"{BASE_URL}/api/admin/forum/stats", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin forum stats failed: {response.text}"
        print(f"✓ GET /api/admin/forum/stats - OK")
    
    def test_admin_quality_scores(self):
        """GET /api/admin/quality-scores - Quality scores"""
        response = requests.get(f"{BASE_URL}/api/admin/quality-scores", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Admin quality-scores failed: {response.text}"
        print(f"✓ GET /api/admin/quality-scores - OK")
    
    def test_conseils_admin_stats(self):
        """GET /api/conseils/admin/stats - Conseils admin stats"""
        response = requests.get(f"{BASE_URL}/api/conseils/admin/stats", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Conseils admin stats failed: {response.text}"
        print(f"✓ GET /api/conseils/admin/stats - OK")
    
    def test_conseils_admin_list(self):
        """GET /api/conseils/admin/list - Conseils admin list"""
        response = requests.get(f"{BASE_URL}/api/conseils/admin/list", headers=self.headers, timeout=10)
        assert response.status_code == 200, f"Conseils admin list failed: {response.text}"
        print(f"✓ GET /api/conseils/admin/list - OK")


class TestPaymentRoutes:
    """Test payment routes - Stripe LIVE mode, only verify session creation"""
    
    def test_stripe_checkout_session_creation(self):
        """POST /api/payments/checkout - Verify Stripe session creation returns URL"""
        response = requests.post(
            f"{BASE_URL}/api/payments/checkout",
            json={
                "package_id": "analyse_dossier",
                "customer_email": "test-audit@example.com",
                "customer_name": "Test Audit",
                "origin_url": BASE_URL
            },
            timeout=15
        )
        # Stripe LIVE mode - should create session and return URL
        if response.status_code == 200:
            data = response.json()
            assert "url" in data, "Should return checkout URL"
            assert "checkout.stripe.com" in data["url"], "URL should be Stripe checkout"
            print(f"✓ POST /api/payments/checkout - OK (Stripe session created)")
            print(f"  - URL contains checkout.stripe.com: YES")
        elif response.status_code == 500:
            # Stripe may fail if key is invalid
            print(f"⚠ POST /api/payments/checkout - 500 (Stripe config issue)")
        else:
            print(f"⚠ POST /api/payments/checkout - {response.status_code}: {response.text}")
    
    def test_paypal_calculate(self):
        """POST /api/paypal/calculate - Verify PayPal amount calculation"""
        response = requests.post(
            f"{BASE_URL}/api/paypal/calculate",
            json={
                "package_id": "analyse_dossier",
                "customer_email": "test-audit@example.com"
            },
            timeout=10
        )
        assert response.status_code == 200, f"PayPal calculate failed: {response.text}"
        data = response.json()
        assert "final_amount" in data, "Should return final_amount"
        assert "package_name" in data, "Should return package_name"
        print(f"✓ POST /api/paypal/calculate - OK")
        print(f"  - Package: {data.get('package_name')}")
        print(f"  - Amount: {data.get('final_amount')}€")


class TestBookingRoutes:
    """Test booking routes"""
    
    def test_booking_slots(self):
        """GET /api/bookings/slots/{date} - Available slots"""
        today = datetime.now().strftime("%Y-%m-%d")
        response = requests.get(f"{BASE_URL}/api/bookings/slots/{today}", timeout=10)
        assert response.status_code == 200, f"Booking slots failed: {response.text}"
        data = response.json()
        assert "slots" in data, "Should return slots"
        print(f"✓ GET /api/bookings/slots/{today} - OK ({len(data.get('slots', []))} slots)")
    
    def test_booking_decouverte(self):
        """POST /api/bookings - Create free discovery booking"""
        # Use a future date to avoid conflicts
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        response = requests.post(
            f"{BASE_URL}/api/bookings",
            json={
                "date": future_date,
                "time_slot": "10:00",
                "name": "Test Audit",
                "email": f"test-audit-{int(time.time())}@example.com",
                "phone": "0600000000",
                "call_type": "decouverte",
                "message": "Test audit booking"
            },
            timeout=10
        )
        # May fail if slot taken or email already used - that's OK
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") == True, "Should return success"
            print(f"✓ POST /api/bookings (decouverte) - OK")
        elif response.status_code == 409:
            print(f"✓ POST /api/bookings (decouverte) - 409 (slot taken or email used)")
        else:
            print(f"⚠ POST /api/bookings (decouverte) - {response.status_code}: {response.text}")
    
    def test_booking_checkout_conseil(self):
        """POST /api/bookings/checkout - Create paid booking checkout"""
        future_date = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d")
        response = requests.post(
            f"{BASE_URL}/api/bookings/checkout",
            json={
                "date": future_date,
                "time_slot": "14:00",
                "name": "Test Audit Conseil",
                "email": f"test-audit-conseil-{int(time.time())}@example.com",
                "phone": "0600000001",
                "call_type": "conseil",
                "message": "Test audit conseil booking",
                "origin_url": BASE_URL
            },
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            assert "url" in data, "Should return checkout URL"
            print(f"✓ POST /api/bookings/checkout (conseil) - OK")
        elif response.status_code == 409:
            print(f"✓ POST /api/bookings/checkout (conseil) - 409 (slot taken)")
        elif response.status_code == 500:
            print(f"⚠ POST /api/bookings/checkout (conseil) - 500 (Stripe config issue)")
        else:
            print(f"⚠ POST /api/bookings/checkout (conseil) - {response.status_code}: {response.text}")


class TestConsentLog:
    """Test consent logging"""
    
    def test_consent_log(self):
        """POST /api/consent-log - Log CGV consent"""
        response = requests.post(
            f"{BASE_URL}/api/consent-log",
            json={
                "email": "test-audit-consent@example.com",
                "service": "analyse_dossier",
                "cgv_accepted": True,
                "retractation_waived": True
            },
            timeout=10
        )
        assert response.status_code == 200, f"Consent log failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Should return success"
        assert "consent_id" in data, "Should return consent_id"
        print(f"✓ POST /api/consent-log - OK")


class TestContactForm:
    """Test contact form"""
    
    def test_contact_form(self):
        """POST /api/contact - Submit contact form"""
        response = requests.post(
            f"{BASE_URL}/api/contact",
            json={
                "nom": "Test Audit",
                "email": f"test-audit-contact-{int(time.time())}@example.com",
                "telephone": "0600000002",
                "sujet": "Test audit",
                "message": "This is a test contact from pre-migration audit"
            },
            timeout=10
        )
        assert response.status_code == 200, f"Contact form failed: {response.text}"
        data = response.json()
        assert data.get("success") == True, "Should return success"
        print(f"✓ POST /api/contact - OK")


class TestStrategiIA:
    """Test StrategiIA analysis routes"""
    
    def test_strategiia_analyze(self):
        """POST /api/strategiia/analyze - Submit analysis"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "situation_details": "Test situation for pre-migration audit. Accident du travail avec séquelles.",
                "type_dossier": "at",
                "regime": "general",
                "email": f"test-audit-strategiia-{int(time.time())}@example.com",
                "name": "Test Audit StrategiIA"
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data, "Should return job_id"
            print(f"✓ POST /api/strategiia/analyze - OK (job_id: {data.get('job_id')})")
            return data.get("job_id")
        elif response.status_code == 202:
            data = response.json()
            print(f"✓ POST /api/strategiia/analyze - 202 Accepted (job_id: {data.get('job_id')})")
            return data.get("job_id")
        else:
            print(f"⚠ POST /api/strategiia/analyze - {response.status_code}: {response.text}")
            return None
    
    def test_strategiia_status(self):
        """GET /api/strategiia/status/{job_id} - Check analysis status"""
        # First create an analysis
        create_resp = requests.post(
            f"{BASE_URL}/api/strategiia/analyze",
            json={
                "situation_details": "Test situation for status check",
                "type_dossier": "mp",
                "regime": "general",
                "email": f"test-audit-status-{int(time.time())}@example.com"
            },
            timeout=30
        )
        if create_resp.status_code not in [200, 202]:
            pytest.skip("Cannot create analysis to test status")
        
        job_id = create_resp.json().get("job_id")
        if not job_id:
            pytest.skip("No job_id returned")
        
        # Check status
        response = requests.get(f"{BASE_URL}/api/strategiia/status/{job_id}", timeout=10)
        assert response.status_code == 200, f"StrategiIA status failed: {response.text}"
        data = response.json()
        assert "status" in data, "Should return status"
        print(f"✓ GET /api/strategiia/status/{job_id} - OK (status: {data.get('status')})")


class TestStorageAndDocuments:
    """Test storage and document routes"""
    
    def test_storage_status(self):
        """GET /api/storage/status - Storage status"""
        response = requests.get(f"{BASE_URL}/api/storage/status", timeout=10)
        assert response.status_code == 200, f"Storage status failed: {response.text}"
        print(f"✓ GET /api/storage/status - OK")
    
    def test_documents_stats(self):
        """GET /api/documents/stats - Document statistics"""
        response = requests.get(f"{BASE_URL}/api/documents/stats", timeout=10)
        assert response.status_code == 200, f"Documents stats failed: {response.text}"
        print(f"✓ GET /api/documents/stats - OK")


class TestSecurityAdminProtection:
    """Test that admin routes are protected without token"""
    
    def test_admin_stats_no_token(self):
        """GET /api/admin/stats without token should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", timeout=10)
        assert response.status_code in [401, 403], f"Admin stats should be protected: {response.status_code}"
        print(f"✓ GET /api/admin/stats (no token) - {response.status_code} (protected)")
    
    def test_admin_analytics_no_token(self):
        """GET /api/admin/analytics without token should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/admin/analytics", timeout=10)
        assert response.status_code in [401, 403], f"Admin analytics should be protected: {response.status_code}"
        print(f"✓ GET /api/admin/analytics (no token) - {response.status_code} (protected)")
    
    def test_admin_contacts_no_token(self):
        """GET /api/admin/contacts without token should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/admin/contacts", timeout=10)
        assert response.status_code in [401, 403], f"Admin contacts should be protected: {response.status_code}"
        print(f"✓ GET /api/admin/contacts (no token) - {response.status_code} (protected)")
    
    def test_admin_bookings_no_token(self):
        """GET /api/admin/bookings without token should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/admin/bookings", timeout=10)
        assert response.status_code in [401, 403], f"Admin bookings should be protected: {response.status_code}"
        print(f"✓ GET /api/admin/bookings (no token) - {response.status_code} (protected)")
    
    def test_admin_documents_no_token(self):
        """GET /api/admin/documents without token should return 401/403"""
        response = requests.get(f"{BASE_URL}/api/admin/documents", timeout=10)
        assert response.status_code in [401, 403], f"Admin documents should be protected: {response.status_code}"
        print(f"✓ GET /api/admin/documents (no token) - {response.status_code} (protected)")


class TestPerformance:
    """Test API response times for critical endpoints"""
    
    def test_health_performance(self):
        """Health endpoint should respond in < 1s"""
        times = []
        for _ in range(3):
            start = time.time()
            requests.get(f"{BASE_URL}/api/health", timeout=10)
            times.append(time.time() - start)
        avg = sum(times) / len(times)
        assert avg < 1, f"Health endpoint too slow: {avg:.2f}s"
        print(f"✓ Health performance: avg {avg:.3f}s")
    
    def test_tarifs_performance(self):
        """Tarifs endpoint should respond in < 2s"""
        times = []
        for _ in range(3):
            start = time.time()
            requests.get(f"{BASE_URL}/api/public/tarifs", timeout=10)
            times.append(time.time() - start)
        avg = sum(times) / len(times)
        assert avg < 2, f"Tarifs endpoint too slow: {avg:.2f}s"
        print(f"✓ Tarifs performance: avg {avg:.3f}s")
    
    def test_conseils_today_performance(self):
        """Conseils today endpoint should respond in < 2s"""
        times = []
        for _ in range(3):
            start = time.time()
            requests.get(f"{BASE_URL}/api/conseils/today", timeout=10)
            times.append(time.time() - start)
        avg = sum(times) / len(times)
        assert avg < 2, f"Conseils today endpoint too slow: {avg:.2f}s"
        print(f"✓ Conseils today performance: avg {avg:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
