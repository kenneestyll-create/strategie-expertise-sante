"""
Test SEO Guide Pages Phase 2 - 15 comprehensive guide pages with 6 structural content blocks
Tests: GET /api/guides, GET /api/guide/{slug}, POST /api/guide/{slug}/cta-click, GET /api/sitemap.xml
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# All 15 slugs from the seed script
ALL_SLUGS = [
    "refus-mdph-aah-que-faire",
    "taux-ipp-5-pourcent-contester",
    "expertise-medicale-defavorable-recours",
    "accident-travail-non-declare-employeur",
    "refus-maladie-professionnelle-cpam-recours",
    "faute-inexcusable-employeur",
    "inaptitude-travail-droits-recours",
    "rente-accident-travail-calcul-contestation",
    "recours-tribunal-judiciaire-pole-social",
    "delai-prescription-maladie-professionnelle",
    "comment-preparer-expertise-medicale",
    "comment-demander-rqth-strategic",
    "comment-faire-reconnaitre-maladie-professionnelle",
    "maladie-professionnelle-definition-droits",
    "ptia-definition-droits-strategie",
]

# Required content blocks for each guide page
REQUIRED_CONTENT_BLOCKS = ["contexte", "limites", "blocages", "erreurs", "strategie", "orientation"]
ADDITIONAL_BLOCKS = ["reassurance", "maillage", "faq"]


class TestGuidesListEndpoint:
    """Test GET /api/guides - returns all active guides"""
    
    def test_guides_list_returns_200(self):
        """GET /api/guides should return 200"""
        response = requests.get(f"{BASE_URL}/api/guides")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/guides returns 200")
    
    def test_guides_list_returns_exactly_15_guides(self):
        """GET /api/guides should return exactly 15 active guides"""
        response = requests.get(f"{BASE_URL}/api/guides")
        assert response.status_code == 200
        guides = response.json()
        assert isinstance(guides, list), "Response should be a list"
        assert len(guides) == 15, f"Expected 15 guides, got {len(guides)}"
        print(f"✓ GET /api/guides returns exactly 15 guides")
    
    def test_guides_list_contains_all_expected_slugs(self):
        """All 15 expected slugs should be present in the guides list"""
        response = requests.get(f"{BASE_URL}/api/guides")
        assert response.status_code == 200
        guides = response.json()
        returned_slugs = [g['slug'] for g in guides]
        
        missing_slugs = [s for s in ALL_SLUGS if s not in returned_slugs]
        assert len(missing_slugs) == 0, f"Missing slugs: {missing_slugs}"
        print(f"✓ All 15 expected slugs are present in the guides list")
    
    def test_guides_list_has_required_fields(self):
        """Each guide in the list should have slug, title, meta_description, category"""
        response = requests.get(f"{BASE_URL}/api/guides")
        assert response.status_code == 200
        guides = response.json()
        
        required_fields = ['slug', 'title', 'meta_description', 'category']
        for guide in guides:
            for field in required_fields:
                assert field in guide, f"Guide missing field '{field}': {guide.get('slug', 'unknown')}"
        print(f"✓ All guides have required fields: {required_fields}")


class TestGuideDetailEndpoint:
    """Test GET /api/guide/{slug} - returns full content for each guide"""
    
    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_guide_detail_returns_200(self, slug):
        """Each guide slug should return 200"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200, f"GET /api/guide/{slug} returned {response.status_code}"
        print(f"✓ GET /api/guide/{slug} returns 200")
    
    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_guide_has_all_6_content_blocks(self, slug):
        """Each guide should have all 6 required content blocks"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        guide = response.json()
        
        content = guide.get('content', {})
        missing_blocks = [b for b in REQUIRED_CONTENT_BLOCKS if b not in content or not content[b]]
        
        assert len(missing_blocks) == 0, f"Guide '{slug}' missing content blocks: {missing_blocks}"
        print(f"✓ Guide '{slug}' has all 6 required content blocks")
    
    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_guide_has_additional_blocks(self, slug):
        """Each guide should have reassurance, maillage, and faq blocks"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        guide = response.json()
        
        content = guide.get('content', {})
        for block in ADDITIONAL_BLOCKS:
            assert block in content, f"Guide '{slug}' missing '{block}' block"
        print(f"✓ Guide '{slug}' has additional blocks: {ADDITIONAL_BLOCKS}")
    
    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_guide_blocages_is_array(self, slug):
        """blocages should be an array"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        guide = response.json()
        
        blocages = guide.get('content', {}).get('blocages', [])
        assert isinstance(blocages, list), f"Guide '{slug}' blocages should be array, got {type(blocages)}"
        assert len(blocages) >= 3, f"Guide '{slug}' should have at least 3 blocages, got {len(blocages)}"
        print(f"✓ Guide '{slug}' has {len(blocages)} blocages (array)")
    
    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_guide_erreurs_is_array(self, slug):
        """erreurs should be an array"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        guide = response.json()
        
        erreurs = guide.get('content', {}).get('erreurs', [])
        assert isinstance(erreurs, list), f"Guide '{slug}' erreurs should be array, got {type(erreurs)}"
        assert len(erreurs) >= 3, f"Guide '{slug}' should have at least 3 erreurs, got {len(erreurs)}"
        print(f"✓ Guide '{slug}' has {len(erreurs)} erreurs (array)")
    
    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_guide_orientation_is_array(self, slug):
        """orientation should be an array"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        guide = response.json()
        
        orientation = guide.get('content', {}).get('orientation', [])
        assert isinstance(orientation, list), f"Guide '{slug}' orientation should be array, got {type(orientation)}"
        assert len(orientation) >= 3, f"Guide '{slug}' should have at least 3 orientation steps, got {len(orientation)}"
        print(f"✓ Guide '{slug}' has {len(orientation)} orientation steps (array)")
    
    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_guide_maillage_is_array_with_correct_structure(self, slug):
        """maillage should be an array of {slug, text} objects"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        guide = response.json()
        
        maillage = guide.get('content', {}).get('maillage', [])
        assert isinstance(maillage, list), f"Guide '{slug}' maillage should be array"
        assert len(maillage) >= 2, f"Guide '{slug}' should have at least 2 maillage links, got {len(maillage)}"
        
        for link in maillage:
            assert 'slug' in link, f"Maillage link missing 'slug' in guide '{slug}'"
            assert 'text' in link, f"Maillage link missing 'text' in guide '{slug}'"
        print(f"✓ Guide '{slug}' has {len(maillage)} maillage links with correct structure")
    
    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_guide_faq_is_array_with_correct_structure(self, slug):
        """faq should be an array of {question, answer} objects"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        guide = response.json()
        
        faq = guide.get('content', {}).get('faq', [])
        assert isinstance(faq, list), f"Guide '{slug}' faq should be array"
        assert len(faq) >= 2, f"Guide '{slug}' should have at least 2 FAQ items, got {len(faq)}"
        
        for item in faq:
            assert 'question' in item, f"FAQ item missing 'question' in guide '{slug}'"
            assert 'answer' in item, f"FAQ item missing 'answer' in guide '{slug}'"
        print(f"✓ Guide '{slug}' has {len(faq)} FAQ items with correct structure")
    
    def test_guide_not_found_returns_404(self):
        """Non-existent slug should return 404"""
        response = requests.get(f"{BASE_URL}/api/guide/does-not-exist-slug-xyz")
        assert response.status_code == 404, f"Expected 404 for non-existent slug, got {response.status_code}"
        print("✓ Non-existent slug returns 404")


class TestGuideWordCount:
    """Test that guide pages have sufficient word count (800+ words)"""
    
    def count_words(self, content):
        """Count total words in all content blocks"""
        total = 0
        if isinstance(content, str):
            return len(content.split())
        if isinstance(content, dict):
            for key, value in content.items():
                total += self.count_words(value)
        if isinstance(content, list):
            for item in content:
                total += self.count_words(item)
        return total
    
    @pytest.mark.parametrize("slug", ALL_SLUGS[:5])  # Test first 5 pages for word count
    def test_guide_has_800_plus_words(self, slug):
        """Guide content should have at least 800 words"""
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        guide = response.json()
        
        content = guide.get('content', {})
        word_count = self.count_words(content)
        
        assert word_count >= 800, f"Guide '{slug}' has only {word_count} words, expected 800+"
        print(f"✓ Guide '{slug}' has {word_count} words (800+ required)")


class TestCtaClickTracking:
    """Test POST /api/guide/{slug}/cta-click - tracks CTA clicks"""
    
    def test_cta_click_increments_counter(self):
        """POST /api/guide/{slug}/cta-click should increment cta_clicks"""
        slug = "faute-inexcusable-employeur"
        
        # Get initial cta_clicks count
        response = requests.get(f"{BASE_URL}/api/guide/{slug}")
        assert response.status_code == 200
        initial_clicks = response.json().get('cta_clicks', 0)
        
        # Click CTA
        click_response = requests.post(f"{BASE_URL}/api/guide/{slug}/cta-click")
        assert click_response.status_code == 200, f"CTA click returned {click_response.status_code}"
        assert click_response.json().get('success') == True
        
        # Verify increment
        response2 = requests.get(f"{BASE_URL}/api/guide/{slug}")
        new_clicks = response2.json().get('cta_clicks', 0)
        
        assert new_clicks == initial_clicks + 1, f"Expected {initial_clicks + 1} clicks, got {new_clicks}"
        print(f"✓ CTA click incremented counter from {initial_clicks} to {new_clicks}")
    
    def test_cta_click_nonexistent_slug_returns_404(self):
        """POST /api/guide/{slug}/cta-click for non-existent slug should return 404"""
        response = requests.post(f"{BASE_URL}/api/guide/nonexistent-slug-xyz/cta-click")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ CTA click for non-existent slug returns 404")


class TestSitemapXml:
    """Test GET /api/sitemap.xml includes all 15 guide URLs"""
    
    def test_sitemap_returns_200(self):
        """GET /api/sitemap.xml should return 200"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ GET /api/sitemap.xml returns 200")
    
    def test_sitemap_is_valid_xml(self):
        """Sitemap should be valid XML"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        assert '<?xml version="1.0"' in content, "Missing XML declaration"
        assert '<urlset' in content, "Missing urlset element"
        assert '</urlset>' in content, "Missing closing urlset element"
        print("✓ Sitemap is valid XML structure")
    
    def test_sitemap_contains_all_15_guide_urls(self):
        """Sitemap should contain URLs for all 15 guide pages"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        missing_slugs = []
        for slug in ALL_SLUGS:
            expected_url = f"/guide/{slug}"
            if expected_url not in content:
                missing_slugs.append(slug)
        
        assert len(missing_slugs) == 0, f"Sitemap missing guide URLs: {missing_slugs}"
        print(f"✓ Sitemap contains all 15 guide URLs")
    
    def test_sitemap_contains_guides_pratiques_hub(self):
        """Sitemap should contain /guides-pratiques hub URL"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        assert "/guides-pratiques" in content, "Sitemap missing /guides-pratiques hub URL"
        print("✓ Sitemap contains /guides-pratiques hub URL")


class TestGuideCategories:
    """Test that guides are properly categorized"""
    
    def test_guides_have_valid_categories(self):
        """All guides should have valid category values"""
        response = requests.get(f"{BASE_URL}/api/guides")
        assert response.status_code == 200
        guides = response.json()
        
        valid_categories = ['mdph', 'accident_travail', 'expertise', 'indemnisation', 'emploi']
        
        for guide in guides:
            category = guide.get('category', '')
            assert category in valid_categories, f"Guide '{guide['slug']}' has invalid category: {category}"
        
        print(f"✓ All guides have valid categories from: {valid_categories}")
    
    def test_guides_grouped_by_category(self):
        """Verify guides are distributed across categories"""
        response = requests.get(f"{BASE_URL}/api/guides")
        assert response.status_code == 200
        guides = response.json()
        
        categories = {}
        for guide in guides:
            cat = guide.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"✓ Guide distribution by category: {categories}")
        assert len(categories) >= 3, f"Expected at least 3 categories, got {len(categories)}"


class TestGuideCtaTypes:
    """Test that guides have proper CTA types"""
    
    def test_guides_have_valid_cta_types(self):
        """All guides should have valid cta_type values"""
        response = requests.get(f"{BASE_URL}/api/guides")
        assert response.status_code == 200
        guides = response.json()
        
        valid_cta_types = ['dossier_express', 'accompagnement']
        
        for guide in guides:
            cta_type = guide.get('cta_type', '')
            assert cta_type in valid_cta_types, f"Guide '{guide['slug']}' has invalid cta_type: {cta_type}"
        
        print(f"✓ All guides have valid cta_types from: {valid_cta_types}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
