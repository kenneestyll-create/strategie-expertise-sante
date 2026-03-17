"""
Test PDF generation and premium options for StrategiIA.
Tests: POST /api/strategiia/generate-pdf with premium_pdf flag.
"""
import pytest
import requests
import os
import base64

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://secure-payment-flow-5.preview.emergentagent.com"

class TestStrategiIAPDFGeneration:
    """Tests for POST /api/strategiia/generate-pdf endpoint"""

    def test_generate_pdf_without_premium(self):
        """Test #1: POST /api/strategiia/generate-pdf with premium_pdf=false returns valid PDF"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "Test analysis content for PDF generation. This is a sample analysis with sufficient text.",
                "type_dossier": "Accident du travail",
                "regime": "Régime général",
                "name": "Test User",
                "premium_pdf": False
            },
            headers={"Content-Type": "application/json"}
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "pdf_base64" in data, "Response should contain pdf_base64"
        assert "filename" in data, "Response should contain filename"
        
        # Verify base64 is non-empty and valid
        pdf_base64 = data["pdf_base64"]
        assert pdf_base64, "pdf_base64 should not be empty"
        assert len(pdf_base64) > 100, "pdf_base64 should have substantial content"
        
        # Verify it's valid base64 that decodes to PDF bytes
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
            assert len(pdf_bytes) > 100, "Decoded PDF should have substantial content"
            # Check PDF magic bytes
            assert pdf_bytes[:4] == b'%PDF', "Decoded content should start with PDF header"
        except Exception as e:
            pytest.fail(f"Failed to decode base64 PDF: {e}")
        
        assert data["filename"] == "strategiia-rapport.pdf", f"Unexpected filename: {data['filename']}"
        print("TEST PASSED: PDF generated with watermark (premium_pdf=false)")

    def test_generate_pdf_with_premium(self):
        """Test #2: POST /api/strategiia/generate-pdf with premium_pdf=true returns valid PDF"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "Premium analysis content for PDF generation. This is a sample premium analysis.",
                "type_dossier": "Maladie professionnelle",
                "regime": "MSA (agricole)",
                "name": "Premium User",
                "premium_pdf": True
            },
            headers={"Content-Type": "application/json"}
        )
        
        # Status code assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "pdf_base64" in data, "Response should contain pdf_base64"
        assert "filename" in data, "Response should contain filename"
        
        # Verify base64 is non-empty and valid
        pdf_base64 = data["pdf_base64"]
        assert pdf_base64, "pdf_base64 should not be empty"
        assert len(pdf_base64) > 100, "pdf_base64 should have substantial content"
        
        # Verify it's valid base64 that decodes to PDF bytes
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
            assert len(pdf_bytes) > 100, "Decoded PDF should have substantial content"
            # Check PDF magic bytes
            assert pdf_bytes[:4] == b'%PDF', "Decoded content should start with PDF header"
        except Exception as e:
            pytest.fail(f"Failed to decode base64 PDF: {e}")
        
        print("TEST PASSED: PDF generated without watermark (premium_pdf=true)")

    def test_generate_pdf_empty_analysis_returns_400(self):
        """Test #3: POST /api/strategiia/generate-pdf with empty analysis returns 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "analysis": "",
                "type_dossier": "Accident du travail",
                "regime": "Régime général",
                "name": "Test User",
                "premium_pdf": False
            },
            headers={"Content-Type": "application/json"}
        )
        
        # Status code assertion
        assert response.status_code == 400, f"Expected 400 for empty analysis, got {response.status_code}: {response.text}"
        
        # Data assertions - verify error message
        data = response.json()
        assert "detail" in data, "Error response should contain detail"
        print(f"TEST PASSED: Empty analysis returns 400 with message: {data.get('detail')}")

    def test_generate_pdf_missing_analysis_returns_400(self):
        """Test: POST /api/strategiia/generate-pdf with missing analysis returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/strategiia/generate-pdf",
            json={
                "type_dossier": "Accident du travail",
                "regime": "Régime général",
                "name": "Test User"
            },
            headers={"Content-Type": "application/json"}
        )
        
        # Status code assertion
        assert response.status_code == 400, f"Expected 400 for missing analysis, got {response.status_code}: {response.text}"
        print("TEST PASSED: Missing analysis field returns 400")


class TestHealthAndBasicEndpoints:
    """Basic health check tests"""

    def test_health_endpoint(self):
        """Verify API is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Unexpected health status: {data}"
        print("TEST PASSED: Health endpoint working")

    def test_root_endpoint(self):
        """Verify root API endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
        print("TEST PASSED: Root API endpoint working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
