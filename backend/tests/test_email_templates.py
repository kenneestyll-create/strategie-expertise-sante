"""
Test suite for Email Template Editor feature
Tests all CRUD operations for email templates in admin panel
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEmailTemplates:
    """Email Templates CRUD tests for admin panel"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for all tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        self.token = login_response.json().get("access_token")
        assert self.token, "No token received from login"
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def test_seed_default_templates(self):
        """POST /api/admin/email-templates/seed - Seeds default templates"""
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/seed")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] == True
        # May create 0 if already seeded, or 3 if first time
        assert "created" in data
        print(f"Seed result: {data['created']} templates created")

    def test_list_email_templates(self):
        """GET /api/admin/email-templates - Returns list of templates"""
        response = self.session.get(f"{BASE_URL}/api/admin/email-templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)
        # Should have at least 3 default templates after seeding
        print(f"Found {len(data['templates'])} templates")
        
        # Verify template structure
        if len(data["templates"]) > 0:
            tpl = data["templates"][0]
            assert "id" in tpl
            assert "name" in tpl
            assert "label" in tpl
            assert "subject" in tpl
            assert "intro" in tpl
            assert "motivation" in tpl
            assert "cta_text" in tpl
            assert "status" in tpl

    def test_list_templates_has_defaults(self):
        """Verify 3 default templates exist: rassurant, incitatif, urgent"""
        # First seed to ensure defaults exist
        self.session.post(f"{BASE_URL}/api/admin/email-templates/seed")
        
        response = self.session.get(f"{BASE_URL}/api/admin/email-templates")
        assert response.status_code == 200
        templates = response.json().get("templates", [])
        
        names = [t["name"] for t in templates]
        assert "rassurant" in names, "Missing 'rassurant' template"
        assert "incitatif" in names, "Missing 'incitatif' template"
        assert "urgent" in names, "Missing 'urgent' template"
        
        # Verify they have 'active' status
        for tpl in templates:
            if tpl["name"] in ["rassurant", "incitatif", "urgent"]:
                assert tpl["status"] == "active", f"Template {tpl['name']} should be active"
                print(f"Template '{tpl['name']}' - label: '{tpl['label']}', status: {tpl['status']}")

    def test_create_new_template(self):
        """POST /api/admin/email-templates - Creates a new template"""
        new_template = {
            "name": "test_template_pytest",
            "label": "Test Template (Pytest)",
            "subject": "Test Subject from Pytest",
            "intro": "This is a test intro from pytest",
            "motivation": "This is test motivation from pytest",
            "cta_text": "Test CTA Button",
            "status": "draft"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates", json=new_template)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == new_template["name"]
        assert data["label"] == new_template["label"]
        assert data["subject"] == new_template["subject"]
        assert data["status"] == "draft"
        print(f"Created template with id: {data['id']}")
        
        # Store for cleanup
        self.created_template_id = data["id"]
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/email-templates/{data['id']}")

    def test_update_template(self):
        """PUT /api/admin/email-templates/{id} - Updates a template"""
        # First create a test template
        create_response = self.session.post(f"{BASE_URL}/api/admin/email-templates", json={
            "name": "test_update_pytest",
            "label": "Update Test",
            "subject": "Original Subject",
            "intro": "Original intro",
            "motivation": "Original motivation",
            "cta_text": "Original CTA",
            "status": "draft"
        })
        assert create_response.status_code == 200
        template_id = create_response.json()["id"]
        
        # Update the template
        update_data = {
            "subject": "Updated Subject by Pytest",
            "intro": "Updated intro by Pytest",
            "status": "active"
        }
        update_response = self.session.put(f"{BASE_URL}/api/admin/email-templates/{template_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["success"] == True
        
        # Verify update persisted
        list_response = self.session.get(f"{BASE_URL}/api/admin/email-templates")
        templates = list_response.json().get("templates", [])
        updated_tpl = next((t for t in templates if t["id"] == template_id), None)
        assert updated_tpl is not None
        assert updated_tpl["subject"] == "Updated Subject by Pytest"
        assert updated_tpl["intro"] == "Updated intro by Pytest"
        assert updated_tpl["status"] == "active"
        print(f"Successfully updated template {template_id}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/email-templates/{template_id}")

    def test_duplicate_template(self):
        """POST /api/admin/email-templates/{id}/duplicate - Duplicates a template"""
        # First ensure we have rassurant template
        self.session.post(f"{BASE_URL}/api/admin/email-templates/seed")
        
        # Get rassurant template id
        list_response = self.session.get(f"{BASE_URL}/api/admin/email-templates")
        templates = list_response.json().get("templates", [])
        rassurant = next((t for t in templates if t["name"] == "rassurant"), None)
        assert rassurant is not None, "rassurant template not found"
        
        # Duplicate it
        dup_response = self.session.post(f"{BASE_URL}/api/admin/email-templates/{rassurant['id']}/duplicate")
        assert dup_response.status_code == 200
        dup_data = dup_response.json()
        assert dup_data["name"] == "rassurant_copy"
        assert dup_data["label"] == "Ton rassurant (copie)"
        assert dup_data["status"] == "draft"
        assert dup_data["id"] != rassurant["id"]
        print(f"Duplicated template: {dup_data['name']} with id {dup_data['id']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/admin/email-templates/{dup_data['id']}")

    def test_delete_template(self):
        """DELETE /api/admin/email-templates/{id} - Deletes a template"""
        # Create a template to delete
        create_response = self.session.post(f"{BASE_URL}/api/admin/email-templates", json={
            "name": "test_delete_pytest",
            "label": "Delete Test",
            "subject": "To be deleted",
            "intro": "This will be deleted",
            "motivation": "Delete me",
            "cta_text": "Delete",
            "status": "draft"
        })
        assert create_response.status_code == 200
        template_id = create_response.json()["id"]
        
        # Delete it
        delete_response = self.session.delete(f"{BASE_URL}/api/admin/email-templates/{template_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] == True
        
        # Verify deletion
        list_response = self.session.get(f"{BASE_URL}/api/admin/email-templates")
        templates = list_response.json().get("templates", [])
        deleted_tpl = next((t for t in templates if t["id"] == template_id), None)
        assert deleted_tpl is None, "Template should have been deleted"
        print(f"Successfully deleted template {template_id}")

    def test_preview_template(self):
        """POST /api/admin/email-templates/preview - Returns HTML preview"""
        preview_data = {
            "subject": "Test Preview Subject",
            "intro": "This is a preview intro text.",
            "motivation": "This is preview motivation text.",
            "cta_text": "Preview CTA Button",
            "prenom": "Marie",
            "completeness_pct": 42
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        assert "html" in data
        assert "subject" in data
        
        # Verify HTML contains expected content
        html = data["html"]
        assert "Marie" in html, "Preview HTML should contain placeholder name 'Marie'"
        assert "42%" in html, "Preview HTML should contain completeness percentage"
        assert "Preview CTA Button" in html, "Preview HTML should contain CTA text"
        assert "This is a preview intro text" in html, "Preview HTML should contain intro"
        assert "This is preview motivation text" in html, "Preview HTML should contain motivation"
        print("Preview HTML generated successfully with all placeholders")

    def test_update_nonexistent_template(self):
        """PUT /api/admin/email-templates/{id} - Returns 404 for non-existent template"""
        response = self.session.put(f"{BASE_URL}/api/admin/email-templates/nonexistent-id-12345", json={
            "subject": "This should fail"
        })
        assert response.status_code == 404

    def test_delete_nonexistent_template(self):
        """DELETE /api/admin/email-templates/{id} - Returns 404 for non-existent template"""
        response = self.session.delete(f"{BASE_URL}/api/admin/email-templates/nonexistent-id-12345")
        assert response.status_code == 404

    def test_duplicate_nonexistent_template(self):
        """POST /api/admin/email-templates/{id}/duplicate - Returns 404 for non-existent template"""
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/nonexistent-id-12345/duplicate")
        assert response.status_code == 404


class TestDynamicTemplateVariables:
    """
    Tests for dynamic template variables feature (Iteration 53)
    - Variables endpoint: GET /api/admin/email-templates/variables
    - Preview endpoint with variable resolution: POST /api/admin/email-templates/preview
    - Variables: {prenom}, {nom}, {completeness}, {documents_missing}, {date_inscription}
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Get admin token for all tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
        self.token = login_response.json().get("access_token")
        assert self.token, "No token received from login"
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def test_get_template_variables_endpoint(self):
        """GET /api/admin/email-templates/variables - Returns list of 5 available variables"""
        response = self.session.get(f"{BASE_URL}/api/admin/email-templates/variables")
        assert response.status_code == 200
        data = response.json()
        assert "variables" in data
        variables = data["variables"]
        assert len(variables) == 5, f"Expected 5 variables, got {len(variables)}"
        
        # Verify each variable has required fields
        for var in variables:
            assert "key" in var, f"Variable missing 'key': {var}"
            assert "label" in var, f"Variable missing 'label': {var}"
            assert "sample" in var, f"Variable missing 'sample': {var}"
        
        # Verify specific variables exist
        keys = [v["key"] for v in variables]
        expected_keys = ["prenom", "nom", "completeness", "documents_missing", "date_inscription"]
        for k in expected_keys:
            assert k in keys, f"Missing variable key: {k}"
        
        print(f"Variables endpoint returned {len(variables)} variables: {keys}")

    def test_variables_have_correct_samples(self):
        """Verify variables have correct sample values"""
        response = self.session.get(f"{BASE_URL}/api/admin/email-templates/variables")
        assert response.status_code == 200
        variables = response.json()["variables"]
        
        expected_samples = {
            "prenom": "Marie",
            "nom": "Dupont",
            "completeness": "42",
            "documents_missing": "Attestation employeur, Certificat médical initial",
            "date_inscription": "15/01/2026"
        }
        
        for var in variables:
            expected = expected_samples.get(var["key"])
            assert var["sample"] == expected, f"Variable {var['key']}: expected sample '{expected}', got '{var['sample']}'"
        
        print("All variable samples verified correctly")

    def test_preview_resolves_prenom_variable(self):
        """POST /api/admin/email-templates/preview - Resolves {{prenom}} to 'Marie'"""
        preview_data = {
            "subject": "Bonjour {{prenom}}, votre dossier vous attend",
            "intro": "Cher {{prenom}}, votre dossier est en attente.",
            "motivation": "Complétez votre dossier rapidement.",
            "cta_text": "Compléter maintenant"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check subject is resolved
        assert "Marie" in data["subject"], f"Subject should contain 'Marie', got: {data['subject']}"
        assert "{{prenom}}" not in data["subject"], "Subject should not contain unresolved {{prenom}}"
        
        # Check HTML is resolved
        assert "Marie" in data["html"], "HTML should contain resolved 'Marie'"
        assert "{{prenom}}" not in data["html"], "HTML should not contain unresolved {{prenom}}"
        
        print(f"Resolved subject: {data['subject']}")

    def test_preview_resolves_completeness_variable(self):
        """POST /api/admin/email-templates/preview - Resolves {{completeness}} to '42'"""
        preview_data = {
            "subject": "Votre dossier est à {{completeness}}% de complétude",
            "intro": "Vous avez atteint {{completeness}}% de complétude.",
            "motivation": "Continuez pour arriver à 100%!",
            "cta_text": "Compléter"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check subject is resolved with 42
        assert "42" in data["subject"], f"Subject should contain '42', got: {data['subject']}"
        assert "{{completeness}}" not in data["subject"], "Subject should not contain unresolved {{completeness}}"
        
        print(f"Resolved subject: {data['subject']}")

    def test_preview_resolves_nom_variable(self):
        """POST /api/admin/email-templates/preview - Resolves {{nom}} to 'Dupont'"""
        preview_data = {
            "subject": "M. ou Mme {{nom}}, votre dossier vous attend",
            "intro": "Bonjour {{prenom}} {{nom}},",
            "motivation": "Votre dossier est prêt.",
            "cta_text": "Voir"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check HTML contains resolved nom
        assert "Dupont" in data["html"], "HTML should contain resolved 'Dupont'"
        assert "{{nom}}" not in data["html"], "HTML should not contain unresolved {{nom}}"
        
        print("nom variable resolved correctly to 'Dupont'")

    def test_preview_resolves_documents_missing_variable(self):
        """POST /api/admin/email-templates/preview - Resolves {{documents_missing}}"""
        preview_data = {
            "subject": "Documents manquants dans votre dossier",
            "intro": "Il vous manque: {{documents_missing}}",
            "motivation": "Ajoutez ces documents pour compléter votre dossier.",
            "cta_text": "Ajouter documents"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check HTML contains resolved documents_missing
        assert "Attestation employeur" in data["html"] or "Certificat médical" in data["html"], \
            "HTML should contain resolved documents_missing sample"
        assert "{{documents_missing}}" not in data["html"], "HTML should not contain unresolved {{documents_missing}}"
        
        print("documents_missing variable resolved correctly")

    def test_preview_resolves_date_inscription_variable(self):
        """POST /api/admin/email-templates/preview - Resolves {{date_inscription}} to '15/01/2026'"""
        preview_data = {
            "subject": "Rappel de votre inscription du {{date_inscription}}",
            "intro": "Depuis votre inscription le {{date_inscription}}, votre dossier attend.",
            "motivation": "Finalisez votre dossier.",
            "cta_text": "Finaliser"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check HTML contains resolved date_inscription
        assert "15/01/2026" in data["html"], "HTML should contain resolved date '15/01/2026'"
        assert "{{date_inscription}}" not in data["html"], "HTML should not contain unresolved {{date_inscription}}"
        
        print("date_inscription variable resolved correctly to '15/01/2026'")

    def test_preview_resolves_multiple_variables_in_subject(self):
        """POST /api/admin/email-templates/preview - Resolves multiple variables in same field"""
        preview_data = {
            "subject": "{{prenom}} {{nom}} - dossier à {{completeness}}%",
            "intro": "Bonjour",
            "motivation": "Test",
            "cta_text": "CTA"
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        
        # Subject should be resolved like: "Marie Dupont - dossier à 42%"
        subject = data["subject"]
        assert "Marie" in subject, f"Subject should contain 'Marie', got: {subject}"
        assert "Dupont" in subject, f"Subject should contain 'Dupont', got: {subject}"
        assert "42" in subject, f"Subject should contain '42', got: {subject}"
        assert "{{" not in subject, f"Subject should not contain unresolved variables, got: {subject}"
        
        print(f"Multiple variables resolved in subject: {subject}")

    def test_preview_custom_prenom_overrides_sample(self):
        """POST /api/admin/email-templates/preview - Custom prenom overrides sample value"""
        preview_data = {
            "subject": "Bonjour {{prenom}}",
            "intro": "Cher {{prenom}},",
            "motivation": "Test",
            "cta_text": "CTA",
            "prenom": "Jean"  # Custom override
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        
        # Should use custom prenom "Jean" instead of sample "Marie"
        assert "Jean" in data["html"], "HTML should contain custom prenom 'Jean'"
        print("Custom prenom override works correctly")

    def test_preview_custom_completeness_overrides_sample(self):
        """POST /api/admin/email-templates/preview - Custom completeness_pct overrides sample"""
        preview_data = {
            "subject": "Dossier à {{completeness}}%",
            "intro": "Complétude: {{completeness}}%",
            "motivation": "Test",
            "cta_text": "CTA",
            "completeness_pct": 75  # Custom override
        }
        response = self.session.post(f"{BASE_URL}/api/admin/email-templates/preview", json=preview_data)
        assert response.status_code == 200
        data = response.json()
        
        # Should use custom completeness "75" instead of sample "42"
        assert "75" in data["html"], "HTML should contain custom completeness '75'"
        print("Custom completeness_pct override works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
