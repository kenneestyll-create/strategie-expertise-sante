#!/usr/bin/env python3
"""
Backend API Testing for Accompagn'Santé
Tests all endpoints using the public URL
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class AccompagnSanteAPITester:
    def __init__(self, base_url="https://secure-payment-flow-5.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.token = None
        self.admin_name = None
        self.forum_token = None
        self.forum_user_id = None
        self.forum_pseudo = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test_result(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results for tracking"""
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        self.tests_run += 1
        if success:
            self.tests_passed += 1

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict = None, headers: Dict = None) -> tuple:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            default_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            default_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=default_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers, timeout=30)
            else:
                print(f"❌ Unsupported method: {method}")
                self.log_test_result(name, False, f"Unsupported method: {method}")
                return False, {}

            success = response.status_code == expected_status
            
            try:
                response_json = response.json()
            except:
                response_json = {"raw_text": response.text}

            if success:
                print(f"✅ Passed - Status: {response.status_code}")
                self.log_test_result(name, True, f"Status: {response.status_code}", response_json)
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.log_test_result(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}", response_json)

            return success, response_json

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Request Error: {str(e)}")
            self.log_test_result(name, False, f"Request Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.log_test_result(name, False, f"Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_seed_data(self):
        """Test seeding initial data"""
        return self.run_test("Seed Data", "POST", "seed", 200)

    def test_get_faq_all(self):
        """Test getting all FAQ items"""
        return self.run_test("Get All FAQ", "GET", "faq", 200)

    def test_get_faq_by_category(self):
        """Test getting FAQ by category"""
        success, _ = self.run_test("Get FAQ by Category (AT/MP)", "GET", "faq/AT/MP", 200)
        return success

    def test_contact_creation(self):
        """Test creating a contact request"""
        contact_data = {
            "nom": "Test",
            "prenom": "User",
            "email": "test@example.com",
            "telephone": "0600000000",
            "sujet": "Test de l'API",
            "message": "Ceci est un message de test pour vérifier l'API",
            "type_accompagnement": "analyse_dossier"
        }
        
        success, response = self.run_test("Create Contact", "POST", "contact", 200, contact_data)
        if success and response.get("id"):
            self.test_contact_id = response.get("id")
            print(f"   Contact ID: {self.test_contact_id}")
        return success

    def test_admin_login(self):
        """Test admin login with correct credentials"""
        login_data = {
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        }
        
        success, response = self.run_test("Admin Login", "POST", "auth/login", 200, login_data)
        if success and response.get("access_token"):
            self.token = response.get("access_token")
            self.admin_name = response.get("admin_name")
            print(f"   Token obtained for: {self.admin_name}")
        return success

    def test_admin_login_invalid(self):
        """Test admin login with wrong credentials"""
        login_data = {
            "email": "admin@accompagn-sante.fr", 
            "password": "WrongPassword"
        }
        
        success, _ = self.run_test("Admin Login (Invalid)", "POST", "auth/login", 401, login_data)
        return success

    def test_auth_me(self):
        """Test getting current admin info"""
        if not self.token:
            print("❌ Skipped - No token available")
            self.log_test_result("Auth Me", False, "No token available")
            return False
        
        return self.run_test("Auth Me", "GET", "auth/me", 200)

    def test_admin_get_contacts(self):
        """Test getting all contacts (admin route)"""
        if not self.token:
            print("❌ Skipped - No token available")
            self.log_test_result("Get Admin Contacts", False, "No token available")
            return False
            
        return self.run_test("Get Admin Contacts", "GET", "admin/contacts", 200)

    def test_admin_get_stats(self):
        """Test getting admin stats"""
        if not self.token:
            print("❌ Skipped - No token available")
            self.log_test_result("Get Admin Stats", False, "No token available")
            return False
            
        return self.run_test("Get Admin Stats", "GET", "admin/stats", 200)

    def test_admin_get_contact_by_id(self):
        """Test getting a specific contact by ID"""
        if not self.token or not hasattr(self, 'test_contact_id'):
            print("❌ Skipped - No token or contact ID available")
            self.log_test_result("Get Contact by ID", False, "No token or contact ID available")
            return False
            
        return self.run_test("Get Contact by ID", "GET", f"admin/contacts/{self.test_contact_id}", 200)

    def test_admin_update_contact(self):
        """Test updating contact status"""
        if not self.token or not hasattr(self, 'test_contact_id'):
            print("❌ Skipped - No token or contact ID available")
            self.log_test_result("Update Contact", False, "No token or contact ID available")
            return False
            
        update_data = {
            "status": "en_cours",
            "notes_admin": "Test note from API testing"
        }
        
        return self.run_test("Update Contact", "PATCH", f"admin/contacts/{self.test_contact_id}", 200, update_data)

    # ==================== FORUM TESTS ====================

    def test_get_forum_categories(self):
        """Test getting forum categories"""
        success, response = self.run_test("Get Forum Categories", "GET", "forum/categories", 200)
        if success and isinstance(response, list) and len(response) == 6:
            categories = [cat.get('slug') for cat in response]
            expected_categories = ['accident-travail', 'maladie-professionnelle', 'expertise-medicale', 'invalidite', 'mdph', 'protection-juridique']
            if all(cat in categories for cat in expected_categories):
                print(f"   ✅ All 6 categories found: {categories}")
            else:
                print(f"   ⚠️ Category mismatch. Expected: {expected_categories}, Found: {categories}")
        return success

    def test_forum_register_email(self):
        """Test forum user registration with email"""
        timestamp = datetime.now().strftime("%H%M%S")
        register_data = {
            "email": f"testforum{timestamp}@example.com",
            "password": "TestPassword123!",
            "pseudo": f"TestUser{timestamp}",
            "is_anonymous": False
        }
        
        success, response = self.run_test("Forum Register Email", "POST", "forum/register", 200, register_data)
        if success and response.get("access_token"):
            self.forum_token = response.get("access_token")
            self.forum_user_id = response.get("user_id")
            self.forum_pseudo = response.get("pseudo")
            print(f"   Forum user registered: {self.forum_pseudo} (ID: {self.forum_user_id})")
        return success

    def test_forum_register_anonymous(self):
        """Test forum anonymous registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        register_data = {
            "pseudo": f"AnonUser{timestamp}",
            "is_anonymous": True
        }
        
        success, response = self.run_test("Forum Register Anonymous", "POST", "forum/register", 200, register_data)
        return success

    def test_forum_login(self):
        """Test forum login (skip if no email user registered)"""
        if not hasattr(self, 'forum_test_email'):
            print("❌ Skipped - No email user to test login")
            self.log_test_result("Forum Login", False, "No email user available")
            return False
            
        login_data = {
            "email": self.forum_test_email,
            "password": "TestPassword123!"
        }
        
        success, response = self.run_test("Forum Login", "POST", "forum/login", 200, login_data)
        return success

    def test_get_forum_topics(self):
        """Test getting forum topics"""
        success, response = self.run_test("Get Forum Topics", "GET", "forum/topics", 200)
        if success and 'topics' in response:
            print(f"   Found {len(response['topics'])} topics")
        return success

    def test_create_forum_topic(self):
        """Test creating a forum topic"""
        if not self.forum_token:
            print("❌ Skipped - No forum token available")
            self.log_test_result("Create Forum Topic", False, "No forum token available")
            return False
            
        topic_data = {
            "category_id": "accident-travail",
            "title": "Test Topic from API",
            "content": "This is a test topic created during API testing."
        }
        
        # Add forum token to headers
        headers = {'Authorization': f'Bearer {self.forum_token}'}
        success, response = self.run_test("Create Forum Topic", "POST", "forum/topics", 200, topic_data, headers)
        if success and response.get("topic_id"):
            self.test_topic_id = response.get("topic_id")
            print(f"   Topic created with ID: {self.test_topic_id}")
        return success

    def test_like_forum_topic(self):
        """Test liking a forum topic"""
        if not self.forum_token or not hasattr(self, 'test_topic_id'):
            print("❌ Skipped - No forum token or topic ID available")
            self.log_test_result("Like Forum Topic", False, "No forum token or topic ID available")
            return False
            
        headers = {'Authorization': f'Bearer {self.forum_token}'}
        success, response = self.run_test("Like Forum Topic", "POST", f"forum/topics/{self.test_topic_id}/like", 200, {}, headers)
        return success

    # ==================== CHATBOT TESTS ====================

    def test_chatbot_faq(self):
        """Test chatbot with FAQ keyword"""
        chat_data = {
            "message": "expertise médicale",
            "session_id": "test-session-123"
        }
        
        success, response = self.run_test("Chatbot FAQ", "POST", "chatbot", 200, chat_data)
        if success and response.get("is_faq") == True:
            print(f"   ✅ FAQ response detected")
        elif success:
            print(f"   ⚠️ Response received but not marked as FAQ: {response.get('is_faq')}")
        return success

    def test_chatbot_ai(self):
        """Test chatbot with non-FAQ question for AI response"""
        chat_data = {
            "message": "What is the weather today?",
            "session_id": "test-session-456"
        }
        
        success, response = self.run_test("Chatbot AI", "POST", "chatbot", 200, chat_data)
        if success and response.get("is_faq") == False:
            print(f"   ✅ AI response detected")
        elif success:
            print(f"   ⚠️ Response received but marked as FAQ: {response.get('is_faq')}")
        return success

    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 60)
        print("🚀 ACCOMPAGN'SANTÉ API TESTING SUITE")
        print("=" * 60)
        
        # Basic health checks
        print("\n📋 BASIC HEALTH CHECKS")
        self.test_health_check()
        self.test_root_endpoint()
        
        # Seed data (important for FAQ to work)
        print("\n🌱 SEEDING DATA")
        self.test_seed_data()
        
        # Public endpoints
        print("\n🌐 PUBLIC ENDPOINTS")
        self.test_get_faq_all()
        self.test_get_faq_by_category()
        self.test_contact_creation()
        
        # Authentication
        print("\n🔐 AUTHENTICATION")
        self.test_admin_login_invalid()  # Test invalid first
        self.test_admin_login()  # Then valid login to get token
        self.test_auth_me()
        
        # Admin endpoints (require authentication)
        print("\n👑 ADMIN ENDPOINTS")
        self.test_admin_get_stats()
        self.test_admin_get_contacts()
        self.test_admin_get_contact_by_id()
        self.test_admin_update_contact()
        
        # Forum endpoints
        print("\n💬 FORUM ENDPOINTS")
        self.test_get_forum_categories()
        self.test_forum_register_email()
        self.test_forum_register_anonymous()
        self.test_get_forum_topics()
        self.test_create_forum_topic()
        self.test_like_forum_topic()
        
        # Chatbot endpoints
        print("\n🤖 CHATBOT ENDPOINTS")
        self.test_chatbot_faq()
        self.test_chatbot_ai()
        
        # Final results
        print("\n" + "=" * 60)
        print(f"📊 FINAL RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        print("=" * 60)
        
        # Return success status
        return self.tests_passed == self.tests_run

    def save_results(self, filename: str = None):
        """Save test results to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/app/test_reports/backend_test_results_{timestamp}.json"
        
        results = {
            "test_summary": {
                "total_tests": self.tests_run,
                "passed_tests": self.tests_passed,
                "success_rate": f"{(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%"
            },
            "test_details": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {str(e)}")

def main():
    """Main test execution"""
    tester = AccompagnSanteAPITester()
    
    try:
        success = tester.run_all_tests()
        tester.save_results()
        return 0 if success else 1
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        tester.save_results()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)