"""
Test Suite for StratégiIA Phase 3 Relevance Scoring Feature

Tests:
- GET /api/strategiia/score endpoint (public, no auth required)
- Score calculation based on anonymized cases
- Confidence levels (high/medium/low/insufficient_data)
- Distribution breakdown (favorable/defavorable/en_cours)
- Top strategies extraction
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestStrategiIAScore:
    """Test the public relevance score endpoint"""
    
    def test_score_endpoint_exists(self):
        """TEST 1: Score endpoint responds"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={"type_dossier": "at"})
        # Should return 200 regardless of data
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("TEST 1 PASSED: Score endpoint exists and responds")
    
    def test_score_at_general_returns_data(self):
        """TEST 2: GET /api/strategiia/score?type_dossier=at&regime=general returns score data"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={
            "type_dossier": "at",
            "regime": "general"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "score" in data, "Response missing 'score' field"
        assert "confidence" in data, "Response missing 'confidence' field"
        assert "total_cases" in data, "Response missing 'total_cases' field"
        assert "distribution" in data, "Response missing 'distribution' field"
        assert "message" in data, "Response missing 'message' field"
        
        print(f"TEST 2: AT general score data: score={data.get('score')}, confidence={data.get('confidence')}, total_cases={data.get('total_cases')}")
        
        # If data exists, verify score is valid
        if data.get("score") is not None:
            assert 0 <= data["score"] <= 100, f"Score {data['score']} not in valid range 0-100"
            assert data["confidence"] in ["high", "medium", "low"], f"Unexpected confidence: {data['confidence']}"
            assert data["total_cases"] > 0
            print(f"TEST 2 PASSED: Score={data['score']}, confidence={data['confidence']}, cases={data['total_cases']}")
        else:
            assert data["confidence"] == "insufficient_data"
            print("TEST 2 PASSED: No cases found (insufficient_data)")
    
    def test_score_mp_returns_data(self):
        """TEST 3: GET /api/strategiia/score?type_dossier=mp returns score data for MP dossiers"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={
            "type_dossier": "mp"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "score" in data
        assert "confidence" in data
        assert "total_cases" in data
        
        print(f"TEST 3: MP score data: score={data.get('score')}, confidence={data.get('confidence')}, total_cases={data.get('total_cases')}")
        
        if data.get("score") is not None:
            assert 0 <= data["score"] <= 100
            print(f"TEST 3 PASSED: MP Score={data['score']}")
        else:
            print("TEST 3 PASSED: MP has insufficient data")
    
    def test_score_nonexistent_type_returns_null(self):
        """TEST 4: GET /api/strategiia/score?type_dossier=nonexistent returns score=null with insufficient_data"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={
            "type_dossier": "nonexistent_xyz_12345"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Should return null score with insufficient_data message
        assert data.get("score") is None, f"Expected null score, got {data.get('score')}"
        assert data.get("confidence") == "insufficient_data", f"Expected 'insufficient_data', got {data.get('confidence')}"
        assert data.get("total_cases") == 0, f"Expected 0 cases, got {data.get('total_cases')}"
        assert "Pas assez de cas" in data.get("message", ""), f"Expected insufficient data message, got {data.get('message')}"
        
        print(f"TEST 4 PASSED: Nonexistent type returns null score with message: {data.get('message')}")
    
    def test_score_distribution_structure(self):
        """TEST 5: Score distribution contains correct fields"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={
            "type_dossier": "at",
            "regime": "general"
        })
        assert response.status_code == 200
        data = response.json()
        
        if data.get("score") is not None and data.get("distribution"):
            dist = data["distribution"]
            # Check distribution has expected keys
            expected_keys = ["favorable", "defavorable", "en_cours", "autre"]
            for key in expected_keys:
                assert key in dist, f"Distribution missing '{key}' field"
                assert isinstance(dist[key], int), f"Distribution {key} should be int, got {type(dist[key])}"
            
            # Verify sum equals total_cases
            total_from_dist = dist["favorable"] + dist["defavorable"] + dist["en_cours"] + dist["autre"]
            assert total_from_dist == data["total_cases"], f"Distribution sum {total_from_dist} != total_cases {data['total_cases']}"
            
            print(f"TEST 5 PASSED: Distribution: favorable={dist['favorable']}, defavorable={dist['defavorable']}, en_cours={dist['en_cours']}, autre={dist['autre']}")
        else:
            print("TEST 5 PASSED: No distribution data (insufficient cases)")
    
    def test_score_top_strategies(self):
        """TEST 6: Top strategies are returned when available"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={
            "type_dossier": "at",
            "regime": "general"
        })
        assert response.status_code == 200
        data = response.json()
        
        if data.get("score") is not None:
            assert "top_strategies" in data, "Response missing 'top_strategies' field"
            strategies = data["top_strategies"]
            assert isinstance(strategies, list), f"top_strategies should be list, got {type(strategies)}"
            
            # Verify strategy structure if any exist
            for s in strategies:
                assert "strategie" in s, "Strategy missing 'strategie' field"
                assert "count" in s, "Strategy missing 'count' field"
                assert isinstance(s["count"], int) and s["count"] > 0
            
            if strategies:
                print(f"TEST 6 PASSED: Found {len(strategies)} top strategies: {[s['strategie'] for s in strategies]}")
            else:
                print("TEST 6 PASSED: No strategies recorded in favorable cases")
        else:
            print("TEST 6 PASSED: No score data (insufficient cases)")
    
    def test_score_success_rate_and_avg_admin_score(self):
        """TEST 7: Success rate and avg_admin_score returned"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={
            "type_dossier": "at",
            "regime": "general"
        })
        assert response.status_code == 200
        data = response.json()
        
        # These fields should always be present
        assert "success_rate" in data, "Response missing 'success_rate' field"
        assert "avg_admin_score" in data, "Response missing 'avg_admin_score' field"
        
        if data.get("success_rate") is not None:
            assert 0 <= data["success_rate"] <= 100, f"Success rate {data['success_rate']} out of range"
            print(f"TEST 7: Success rate = {data['success_rate']}%")
        
        if data.get("avg_admin_score") is not None:
            assert 0 <= data["avg_admin_score"] <= 100, f"Avg admin score {data['avg_admin_score']} out of range"
            print(f"TEST 7: Avg admin score = {data['avg_admin_score']}")
        
        print("TEST 7 PASSED: Success rate and avg_admin_score fields present")
    
    def test_score_confidence_levels(self):
        """TEST 8: Confidence levels are correctly assigned"""
        # Test with different type_dossier to get various case counts
        types_to_test = ["at", "mp", "mdph"]
        
        for t in types_to_test:
            response = requests.get(f"{BASE_URL}/api/strategiia/score", params={"type_dossier": t})
            assert response.status_code == 200
            data = response.json()
            
            confidence = data.get("confidence")
            total = data.get("total_cases", 0)
            
            # Verify confidence aligns with case count
            if total >= 20:
                assert confidence == "high", f"Expected 'high' confidence for {total} cases, got {confidence}"
            elif total >= 5:
                assert confidence == "medium", f"Expected 'medium' confidence for {total} cases, got {confidence}"
            elif total > 0:
                assert confidence == "low", f"Expected 'low' confidence for {total} cases, got {confidence}"
            else:
                assert confidence == "insufficient_data", f"Expected 'insufficient_data' for 0 cases, got {confidence}"
            
            print(f"  {t}: {total} cases -> {confidence} confidence")
        
        print("TEST 8 PASSED: Confidence levels correctly assigned based on case count")


class TestStrategiIAScoreEdgeCases:
    """Edge case tests for score endpoint"""
    
    def test_score_without_regime(self):
        """TEST 9: Score endpoint works without regime parameter"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={
            "type_dossier": "at"
        })
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        print(f"TEST 9 PASSED: Score without regime returns total_cases={data.get('total_cases')}")
    
    def test_score_with_empty_regime(self):
        """TEST 10: Score endpoint works with empty regime parameter"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score", params={
            "type_dossier": "at",
            "regime": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        print(f"TEST 10 PASSED: Score with empty regime returns total_cases={data.get('total_cases')}")
    
    def test_score_missing_type_dossier(self):
        """TEST 11: Score endpoint requires type_dossier parameter"""
        response = requests.get(f"{BASE_URL}/api/strategiia/score")
        # FastAPI should return 422 for missing required query param
        assert response.status_code == 422, f"Expected 422 for missing type_dossier, got {response.status_code}"
        print("TEST 11 PASSED: Missing type_dossier returns 422 validation error")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
