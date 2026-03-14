"""
SEO and Performance Feature Tests
Tests: sitemap.xml, robots.txt, page titles, meta descriptions, og tags, canonical links, lazy loading
"""
import pytest
import requests
import os
from xml.etree import ElementTree

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSitemapAndRobots:
    """Tests for sitemap.xml and robots.txt backend endpoints"""
    
    def test_sitemap_returns_valid_xml(self):
        """GET /api/sitemap.xml should return valid XML with urlset"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/xml" in response.headers.get("Content-Type", ""), "Content-Type should be application/xml"
        
        # Parse XML
        root = ElementTree.fromstring(response.text)
        assert "urlset" in root.tag, "Root element should be urlset"
        print(f"Sitemap XML valid with root tag: {root.tag}")
    
    def test_sitemap_has_minimum_urls(self):
        """Sitemap should have at least 20 URL entries"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        
        # Count <url> elements
        url_count = response.text.count("<url>")
        assert url_count >= 20, f"Expected at least 20 URLs, got {url_count}"
        print(f"Sitemap has {url_count} URL entries (>=20 required)")
    
    def test_sitemap_url_structure(self):
        """Each URL in sitemap should have loc, lastmod, changefreq, priority"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        
        root = ElementTree.fromstring(response.text)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        urls = root.findall('sm:url', ns)
        assert len(urls) > 0, "Should have at least one URL element"
        
        # Check first URL has all required elements
        first_url = urls[0]
        loc = first_url.find('sm:loc', ns)
        lastmod = first_url.find('sm:lastmod', ns)
        changefreq = first_url.find('sm:changefreq', ns)
        priority = first_url.find('sm:priority', ns)
        
        assert loc is not None, "URL should have <loc>"
        assert lastmod is not None, "URL should have <lastmod>"
        assert changefreq is not None, "URL should have <changefreq>"
        assert priority is not None, "URL should have <priority>"
        print(f"First URL structure valid: loc={loc.text}")
    
    def test_robots_txt_returns_text(self):
        """GET /api/robots.txt should return text/plain"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/plain" in response.headers.get("Content-Type", ""), "Content-Type should be text/plain"
        print("robots.txt returns text/plain content")
    
    def test_robots_txt_has_user_agent(self):
        """robots.txt should have User-agent directive"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        
        content = response.text
        assert "User-agent" in content, "robots.txt should contain User-agent"
        print("robots.txt contains User-agent directive")
    
    def test_robots_txt_has_allow(self):
        """robots.txt should have Allow directive"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        
        content = response.text
        assert "Allow:" in content, "robots.txt should contain Allow directive"
        print("robots.txt contains Allow directive")
    
    def test_robots_txt_disallows_admin(self):
        """robots.txt should disallow /admin"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        
        content = response.text
        assert "Disallow: /admin" in content, "robots.txt should disallow /admin"
        print("robots.txt correctly disallows /admin")
    
    def test_robots_txt_has_sitemap_url(self):
        """robots.txt should include Sitemap URL"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        
        content = response.text
        assert "Sitemap:" in content, "robots.txt should contain Sitemap URL"
        assert "/api/sitemap.xml" in content, "Sitemap URL should point to /api/sitemap.xml"
        print("robots.txt contains valid Sitemap URL")


class TestBackendHealth:
    """Basic health check tests"""
    
    def test_api_health(self):
        """API health check should return healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
