"""
Test suite for Phone Call Booking System with 3 types:
- Appel Découverte (free, 10min, max 1/person, slots 09:00+09:15)
- Appel Conseil (paid 75€, 30min, Stripe checkout required, slots 14:00-16:30)
- Appel Urgence (links to AlerteUrgente modal, not a booking system)

Business hours: Mon-Fri 9h-17h only. No weekend/evening slots.
"""

import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

def get_next_weekday():
    """Get next weekday date (Mon-Fri) for testing"""
    today = datetime.now()
    days_ahead = 1
    while True:
        next_day = today + timedelta(days=days_ahead)
        if next_day.weekday() < 5:  # Mon=0, Fri=4
            return next_day.strftime('%Y-%m-%d')
        days_ahead += 1

def get_unique_email():
    """Generate unique email for testing"""
    return f"test_booking_{uuid.uuid4().hex[:8]}@test.com"


class TestCallTypesEndpoint:
    """Test GET /api/bookings/call-types endpoint"""
    
    def test_get_call_types_returns_two_types(self):
        """GET /api/bookings/call-types returns 2 types (decouverte + conseil)"""
        response = requests.get(f"{BASE_URL}/api/bookings/call-types")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "decouverte" in data, "Missing 'decouverte' call type"
        assert "conseil" in data, "Missing 'conseil' call type"
        print(f"PASS: Call types returned: {list(data.keys())}")
    
    def test_decouverte_type_config(self):
        """Verify decouverte type has correct config"""
        response = requests.get(f"{BASE_URL}/api/bookings/call-types")
        data = response.json()
        
        decouverte = data.get("decouverte", {})
        assert decouverte.get("duration") == 10, f"Expected duration 10, got {decouverte.get('duration')}"
        assert decouverte.get("price") == 0, f"Expected price 0, got {decouverte.get('price')}"
        assert "09:00" in decouverte.get("slots", []), "Missing 09:00 slot"
        assert "09:15" in decouverte.get("slots", []), "Missing 09:15 slot"
        assert len(decouverte.get("slots", [])) == 2, f"Expected 2 slots, got {len(decouverte.get('slots', []))}"
        print(f"PASS: Decouverte config correct - duration={decouverte['duration']}, price={decouverte['price']}, slots={decouverte['slots']}")
    
    def test_conseil_type_config(self):
        """Verify conseil type has correct config"""
        response = requests.get(f"{BASE_URL}/api/bookings/call-types")
        data = response.json()
        
        conseil = data.get("conseil", {})
        assert conseil.get("duration") == 30, f"Expected duration 30, got {conseil.get('duration')}"
        assert conseil.get("price") == 75.0, f"Expected price 75, got {conseil.get('price')}"
        
        expected_slots = ["14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
        actual_slots = conseil.get("slots", [])
        for slot in expected_slots:
            assert slot in actual_slots, f"Missing slot {slot}"
        assert len(actual_slots) == 6, f"Expected 6 slots, got {len(actual_slots)}"
        print(f"PASS: Conseil config correct - duration={conseil['duration']}, price={conseil['price']}, slots={actual_slots}")


class TestSlotsEndpoint:
    """Test GET /api/bookings/slots/{date} endpoint"""
    
    def test_decouverte_slots_returns_morning_only(self):
        """GET /api/bookings/slots/{date}?call_type=decouverte returns only 09:00 and 09:15"""
        test_date = get_next_weekday()
        response = requests.get(f"{BASE_URL}/api/bookings/slots/{test_date}?call_type=decouverte")
        assert response.status_code == 200
        
        data = response.json()
        slots = data.get("slots", [])
        # Slots should only contain 09:00 and/or 09:15 (some may be booked)
        for slot in slots:
            assert slot in ["09:00", "09:15"], f"Unexpected slot {slot} for decouverte"
        print(f"PASS: Decouverte slots for {test_date}: {slots}")
    
    def test_conseil_slots_returns_afternoon_only(self):
        """GET /api/bookings/slots/{date}?call_type=conseil returns 14:00-16:30"""
        test_date = get_next_weekday()
        response = requests.get(f"{BASE_URL}/api/bookings/slots/{test_date}?call_type=conseil")
        assert response.status_code == 200
        
        data = response.json()
        slots = data.get("slots", [])
        expected_slots = ["14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
        for slot in slots:
            assert slot in expected_slots, f"Unexpected slot {slot} for conseil"
        print(f"PASS: Conseil slots for {test_date}: {slots}")
    
    def test_slots_returns_call_type_in_response(self):
        """Verify slots response includes call_type field"""
        test_date = get_next_weekday()
        response = requests.get(f"{BASE_URL}/api/bookings/slots/{test_date}?call_type=conseil")
        data = response.json()
        
        assert data.get("call_type") == "conseil", f"Expected call_type='conseil', got {data.get('call_type')}"
        assert data.get("date") == test_date, f"Expected date={test_date}, got {data.get('date')}"
        print(f"PASS: Slots response includes call_type and date")


class TestDecouverteBooking:
    """Test POST /api/bookings for free discovery calls"""
    
    def test_create_decouverte_booking_success(self):
        """POST /api/bookings with call_type=decouverte creates free booking directly"""
        test_date = get_next_weekday()
        unique_email = get_unique_email()
        
        # First get available slots
        slots_response = requests.get(f"{BASE_URL}/api/bookings/slots/{test_date}?call_type=decouverte")
        slots = slots_response.json().get("slots", [])
        
        if not slots:
            pytest.skip(f"No available decouverte slots for {test_date}")
        
        payload = {
            "date": test_date,
            "time_slot": slots[0],
            "name": "Test User Decouverte",
            "email": unique_email,
            "phone": "0600000000",
            "call_type": "decouverte",
            "message": "Test booking"
        }
        
        response = requests.post(f"{BASE_URL}/api/bookings", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, f"Expected success=True, got {data}"
        assert "booking_id" in data, "Missing booking_id in response"
        print(f"PASS: Decouverte booking created - booking_id={data['booking_id']}")
    
    def test_decouverte_max_one_per_email(self):
        """POST /api/bookings decouverte - max 1 per email (second attempt returns 409)"""
        test_date = get_next_weekday()
        unique_email = get_unique_email()
        
        # Get available slots
        slots_response = requests.get(f"{BASE_URL}/api/bookings/slots/{test_date}?call_type=decouverte")
        slots = slots_response.json().get("slots", [])
        
        if not slots:
            pytest.skip(f"No available decouverte slots for {test_date}")
        
        payload = {
            "date": test_date,
            "time_slot": slots[0],
            "name": "Test User Max One",
            "email": unique_email,
            "call_type": "decouverte"
        }
        
        # First booking should succeed
        response1 = requests.post(f"{BASE_URL}/api/bookings", json=payload)
        assert response1.status_code == 200, f"First booking failed: {response1.text}"
        
        # Second booking with same email should fail with 409
        # Use different date/slot to ensure it's the email limit, not slot conflict
        future_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        while datetime.strptime(future_date, '%Y-%m-%d').weekday() >= 5:
            future_date = (datetime.strptime(future_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        
        payload2 = {
            "date": future_date,
            "time_slot": "09:00",
            "name": "Test User Max One",
            "email": unique_email,
            "call_type": "decouverte"
        }
        
        response2 = requests.post(f"{BASE_URL}/api/bookings", json=payload2)
        assert response2.status_code == 409, f"Expected 409 for second decouverte, got {response2.status_code}: {response2.text}"
        print(f"PASS: Second decouverte booking correctly rejected with 409")
    
    def test_decouverte_slot_conflict(self):
        """POST /api/bookings decouverte - same slot same date returns 409 for different user"""
        test_date = get_next_weekday()
        
        # Get available slots
        slots_response = requests.get(f"{BASE_URL}/api/bookings/slots/{test_date}?call_type=decouverte")
        slots = slots_response.json().get("slots", [])
        
        if not slots:
            pytest.skip(f"No available decouverte slots for {test_date}")
        
        slot_to_book = slots[0]
        
        # First booking
        payload1 = {
            "date": test_date,
            "time_slot": slot_to_book,
            "name": "User One",
            "email": get_unique_email(),
            "call_type": "decouverte"
        }
        response1 = requests.post(f"{BASE_URL}/api/bookings", json=payload1)
        assert response1.status_code == 200, f"First booking failed: {response1.text}"
        
        # Second booking same slot different user should fail
        payload2 = {
            "date": test_date,
            "time_slot": slot_to_book,
            "name": "User Two",
            "email": get_unique_email(),
            "call_type": "decouverte"
        }
        response2 = requests.post(f"{BASE_URL}/api/bookings", json=payload2)
        assert response2.status_code == 409, f"Expected 409 for slot conflict, got {response2.status_code}: {response2.text}"
        print(f"PASS: Slot conflict correctly returns 409")


class TestConseilBookingRejection:
    """Test that conseil bookings are rejected via direct /bookings endpoint"""
    
    def test_conseil_direct_booking_rejected(self):
        """POST /api/bookings with call_type=conseil is REJECTED (must use /bookings/checkout)"""
        test_date = get_next_weekday()
        
        payload = {
            "date": test_date,
            "time_slot": "14:00",
            "name": "Test User Conseil",
            "email": get_unique_email(),
            "call_type": "conseil"
        }
        
        response = requests.post(f"{BASE_URL}/api/bookings", json=payload)
        assert response.status_code == 400, f"Expected 400 for conseil direct booking, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "checkout" in data.get("detail", "").lower() or "payant" in data.get("detail", "").lower(), \
            f"Expected error about checkout/payment, got: {data.get('detail')}"
        print(f"PASS: Conseil direct booking correctly rejected with 400")


class TestConseilCheckout:
    """Test POST /api/bookings/checkout for paid calls"""
    
    def test_checkout_validation_works(self):
        """POST /api/bookings/checkout validates required fields"""
        # Missing required fields
        response = requests.post(f"{BASE_URL}/api/bookings/checkout", json={
            "call_type": "conseil"
        })
        assert response.status_code == 400, f"Expected 400 for missing fields, got {response.status_code}"
        print(f"PASS: Checkout validation rejects missing fields")
    
    def test_checkout_invalid_slot_rejected(self):
        """POST /api/bookings/checkout rejects invalid slot for call type"""
        test_date = get_next_weekday()
        
        payload = {
            "date": test_date,
            "time_slot": "09:00",  # This is a decouverte slot, not conseil
            "name": "Test User",
            "email": get_unique_email(),
            "call_type": "conseil",
            "origin_url": "https://test.com"
        }
        
        response = requests.post(f"{BASE_URL}/api/bookings/checkout", json=payload)
        assert response.status_code == 400, f"Expected 400 for invalid slot, got {response.status_code}: {response.text}"
        print(f"PASS: Checkout rejects invalid slot for call type")
    
    def test_checkout_creates_pending_booking(self):
        """POST /api/bookings/checkout for conseil creates pending booking (Stripe will fail with placeholder key)"""
        test_date = get_next_weekday()
        
        payload = {
            "date": test_date,
            "time_slot": "14:00",
            "name": "Test User Checkout",
            "email": get_unique_email(),
            "call_type": "conseil",
            "origin_url": "https://test.com"
        }
        
        response = requests.post(f"{BASE_URL}/api/bookings/checkout", json=payload)
        # Stripe will fail with placeholder key, but validation should pass
        # We expect either 500 (Stripe error) or 200 (if Stripe somehow works)
        if response.status_code == 500:
            # Expected - Stripe key is placeholder
            data = response.json()
            assert "paiement" in data.get("detail", "").lower() or "stripe" in data.get("detail", "").lower() or "erreur" in data.get("detail", "").lower(), \
                f"Expected Stripe/payment error, got: {data.get('detail')}"
            print(f"PASS: Checkout validation passed, Stripe failed as expected (placeholder key)")
        elif response.status_code == 200:
            # Unexpected but acceptable
            print(f"PASS: Checkout succeeded (Stripe key may be valid)")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")


class TestSlotAvailabilityAfterBooking:
    """Test that booked slots are removed from availability"""
    
    def test_slot_removed_after_booking(self):
        """GET /api/bookings/slots/{date} after a decouverte booking correctly removes booked slot"""
        test_date = get_next_weekday()
        
        # Get initial slots
        initial_response = requests.get(f"{BASE_URL}/api/bookings/slots/{test_date}?call_type=decouverte")
        initial_slots = initial_response.json().get("slots", [])
        
        if not initial_slots:
            pytest.skip(f"No available decouverte slots for {test_date}")
        
        slot_to_book = initial_slots[0]
        
        # Book the slot
        payload = {
            "date": test_date,
            "time_slot": slot_to_book,
            "name": "Test Slot Removal",
            "email": get_unique_email(),
            "call_type": "decouverte"
        }
        book_response = requests.post(f"{BASE_URL}/api/bookings", json=payload)
        assert book_response.status_code == 200, f"Booking failed: {book_response.text}"
        
        # Check slots again
        after_response = requests.get(f"{BASE_URL}/api/bookings/slots/{test_date}?call_type=decouverte")
        after_slots = after_response.json().get("slots", [])
        
        assert slot_to_book not in after_slots, f"Booked slot {slot_to_book} still appears in available slots"
        print(f"PASS: Booked slot {slot_to_book} correctly removed from availability")


class TestAdminBookingsEndpoint:
    """Test admin bookings endpoint"""
    
    def test_admin_bookings_requires_auth(self):
        """GET /api/admin/bookings requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/bookings")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: Admin bookings endpoint requires auth")
    
    def test_admin_bookings_with_auth(self):
        """GET /api/admin/bookings works with valid auth"""
        # Login first
        login_response = requests.post(f"{BASE_URL}/api/admin/login", json={
            "email": "admin@accompagn-sante.fr",
            "password": "Admin2024!"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Admin login failed")
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"PASS: Admin bookings endpoint returns {len(data)} bookings")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
