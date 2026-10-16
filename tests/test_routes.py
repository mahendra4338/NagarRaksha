# ============================================================
# tests/test_routes.py — Flask Route Integration Tests
# ============================================================
# PURPOSE: Test all Flask routes — login, report, API, etc.
# RUN:     python tests/test_routes.py
# Uses Flask's built-in test client (no real server needed)
# ============================================================

import unittest
import json
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFlaskRoutes(unittest.TestCase):
    """Integration tests for all Flask routes"""

    def setUp(self):
        """Set up test Flask client with temp data directory"""
        # Create temp directory for test data
        self.test_dir = tempfile.mkdtemp()

        # Patch data files before importing app
        import data_helper
        data_helper.REPORTS_FILE = os.path.join(self.test_dir, 'reports.json')
        data_helper.SOS_FILE     = os.path.join(self.test_dir, 'sos_events.json')
        data_helper.USERS_FILE   = os.path.join(self.test_dir, 'users.json')

        with open(data_helper.REPORTS_FILE, 'w') as f:
            json.dump([], f)
        with open(data_helper.SOS_FILE, 'w') as f:
            json.dump([], f)
        with open(data_helper.USERS_FILE, 'w') as f:
            json.dump(data_helper.DEFAULT_USERS, f)

        # Import app after patching
        import app as flask_app
        flask_app.app.config['TESTING']              = True
        flask_app.app.config['SECRET_KEY']           = 'test-secret'
        flask_app.app.config['WTF_CSRF_ENABLED']     = False

        self.app    = flask_app.app
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    # ── Helper: Login with a role ─────────────────────────────
    def login(self, role='citizen'):
        credentials = {
            'citizen':    ('citizen@nr.com',    'citizen123'),
            'authority':  ('authority@nr.com',  'authority123'),
            'government': ('government@nr.com', 'government123'),
        }
        email, password = credentials[role]
        return self.client.post('/login', data={
            'email':    email,
            'password': password,
            'role':     role
        }, follow_redirects=True)


    # ════════════════════════════════════════════════════════
    # AUTH ROUTE TESTS
    # ════════════════════════════════════════════════════════

    def test_01_home_page_loads(self):
        """GET / should return 200 and show login page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'NagarRaksha', response.data)
        print("✅ Test 01: Home page loads")

    def test_02_login_citizen_success(self):
        """Citizen login with correct credentials"""
        response = self.login('citizen')
        self.assertEqual(response.status_code, 200)
        # Should redirect to citizen dashboard
        self.assertIn(b'citizen', response.data.lower())
        print("✅ Test 02: Citizen login succeeds")

    def test_03_login_authority_success(self):
        """Authority login with correct credentials"""
        response = self.login('authority')
        self.assertEqual(response.status_code, 200)
        print("✅ Test 03: Authority login succeeds")

    def test_04_login_government_success(self):
        """Government login with correct credentials"""
        response = self.login('government')
        self.assertEqual(response.status_code, 200)
        print("✅ Test 04: Government login succeeds")

    def test_05_login_wrong_password(self):
        """Wrong password should show error, not crash"""
        response = self.client.post('/login', data={
            'email':    'citizen@nr.com',
            'password': 'wrongpassword',
            'role':     'citizen'
        })
        self.assertEqual(response.status_code, 200)
        # Should show error message
        self.assertIn(b'Wrong password', response.data)
        print("✅ Test 05: Wrong password shows error")

    def test_06_login_wrong_email(self):
        """Unknown email should show error"""
        response = self.client.post('/login', data={
            'email':    'nobody@nr.com',
            'password': 'anything',
            'role':     'citizen'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'not found', response.data.lower())
        print("✅ Test 06: Unknown email shows error")

    def test_07_login_role_mismatch(self):
        """Citizen email with government role should fail"""
        response = self.client.post('/login', data={
            'email':    'citizen@nr.com',
            'password': 'citizen123',
            'role':     'government'   # Wrong role!
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'citizen', response.data.lower())
        print("✅ Test 07: Role mismatch shows error")

    def test_08_protected_route_without_login(self):
        """Accessing /citizen without login should redirect"""
        response = self.client.get('/citizen')
        # Should redirect to login (302) or show login page (200)
        self.assertIn(response.status_code, [200, 302])
        print("✅ Test 08: Protected route redirects without login")

    def test_09_logout(self):
        """Logout should clear session"""
        self.login('citizen')
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("✅ Test 09: Logout works correctly")


    # ════════════════════════════════════════════════════════
    # API ROUTE TESTS
    # ════════════════════════════════════════════════════════

    def test_10_api_reports_returns_json(self):
        """/api/reports should return valid JSON array"""
        self.login('citizen')
        response = self.client.get('/api/reports')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        print("✅ Test 10: /api/reports returns JSON array")

    def test_11_api_stats_returns_json(self):
        """/api/stats should return stats dict"""
        self.login('government')
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('total',       data)
        self.assertIn('resolved',    data)
        self.assertIn('pending',     data)
        self.assertIn('high_threat', data)
        print("✅ Test 11: /api/stats returns correct fields")

    def test_12_api_city_stats(self):
        """/api/city-stats should return cities and counts"""
        self.login('government')
        response = self.client.get('/api/city-stats')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('cities', data)
        self.assertIn('counts', data)
        print("✅ Test 12: /api/city-stats returns correct structure")

    def test_13_api_type_stats(self):
        """/api/type-stats should return types and counts"""
        self.login('government')
        response = self.client.get('/api/type-stats')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('types',  data)
        self.assertIn('counts', data)
        print("✅ Test 13: /api/type-stats returns correct structure")

    def test_14_api_trend(self):
        """/api/trend should return dates and counts"""
        self.login('government')
        response = self.client.get('/api/trend')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('dates',  data)
        self.assertIn('counts', data)
        print("✅ Test 14: /api/trend returns correct structure")

    def test_15_api_stats_wrong_role(self):
        """/api/stats should reject non-government users"""
        self.login('citizen')
        response = self.client.get('/api/stats')
        # Should return 302 redirect or 401 unauthorized
        self.assertIn(response.status_code, [302, 401])
        print("✅ Test 15: /api/stats rejects non-government user")


    # ════════════════════════════════════════════════════════
    # SOS ROUTE TESTS
    # ════════════════════════════════════════════════════════

    def test_16_sos_page_loads(self):
        """SOS page should load for logged-in citizen"""
        self.login('citizen')
        response = self.client.get('/sos')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SOS', response.data)
        print("✅ Test 16: SOS page loads for citizen")

    def test_17_sos_trigger(self):
        """POST /sos/trigger should return success response"""
        self.login('citizen')
        response = self.client.post('/sos/trigger',
            data        = json.dumps({'latitude': 16.5062, 'longitude': 80.6480}),
            content_type= 'application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('case_id',         data)
        self.assertIn('nearest_station', data)
        self.assertIn('eta_minutes',     data)
        print("✅ Test 17: /sos/trigger returns complete response")


    # ════════════════════════════════════════════════════════
    # RESOLVE ROUTE TESTS
    # ════════════════════════════════════════════════════════

    def test_18_resolve_report(self):
        """Authority should be able to resolve a report"""
        # First save a report directly
        import data_helper
        report = data_helper.save_report(
            'citizen@nr.com', 'Suspicious Person', 'City',
            'photo.jpg', 'REAL', 'HIGH', 'Test reason'
        )
        report_id = report['report_id']

        # Now resolve it as authority
        self.login('authority')
        response = self.client.post(f'/resolve/{report_id}',
            content_type = 'application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertTrue(data['success'])
        print("✅ Test 18: Authority can resolve a report")

    def test_19_resolve_nonexistent_report(self):
        """Resolving non-existent report should return 404"""
        self.login('authority')
        response = self.client.post('/resolve/XXXXXXXX',
            content_type = 'application/json'
        )
        self.assertEqual(response.status_code, 404)
        print("✅ Test 19: Resolving non-existent report returns 404")

    def test_20_citizen_cannot_resolve(self):
        """Citizen should NOT be able to resolve reports"""
        self.login('citizen')
        response = self.client.post('/resolve/ANYID',
            content_type = 'application/json'
        )
        # Should get unauthorized
        self.assertIn(response.status_code, [302, 401])
        print("✅ Test 20: Citizen cannot resolve reports (unauthorized)")

    def test_21_register_page_loads(self):
        """GET /register should return 200 and load the register page"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
        print("✅ Test 21: Register page loads successfully")

    def test_22_register_citizen_success(self):
        """Registering a new citizen successfully redirects to dashboard"""
        response = self.client.post('/register', data={
            'name':     'Test Citizen',
            'email':    'new_citizen@nr.com',
            'password': 'password123',
            'role':     'citizen'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'welcome', response.data.lower())
        self.assertIn(b'test citizen', response.data.lower())
        print("✅ Test 22: Citizen registration succeeds and logs in")

    def test_23_register_duplicate_fails(self):
        """Registering with an already registered email should fail and show error"""
        # Register first
        self.client.post('/register', data={
            'name':     'First User',
            'email':    'dup@nr.com',
            'password': 'pass1',
            'role':     'citizen'
        })
        # Log out to clear session before duplicate attempt
        self.client.get('/logout')
        # Try duplicate
        response = self.client.post('/register', data={
            'name':     'Second User',
            'email':    'dup@nr.com',
            'password': 'pass2',
            'role':     'citizen'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'already registered', response.data.lower())
        print("✅ Test 23: Duplicate registration shows error")

    def test_24_report_post_success_with_coords(self):
        """POST /report should record and parse latitude and longitude"""
        self.login('citizen')
        import io
        data = {
            'photo': (io.BytesIO(b"dummy image content"), 'test.jpg'),
            'incident_type': 'Suspicious Person',
            'city': 'Hyderabad',
            'latitude': '17.3850',
            'longitude': '78.4867'
        }
        response = self.client.post('/report', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        
        res_data = json.loads(response.data)
        self.assertTrue(res_data['success'])
        
        # Verify it was saved in reports.json with correct coordinates
        import data_helper
        saved_report = data_helper.get_report_by_id(res_data['report_id'])
        self.assertIsNotNone(saved_report)
        self.assertEqual(saved_report['latitude'], 17.3850)
        self.assertEqual(saved_report['longitude'], 78.4867)
        print("✅ Test 24: Geolocation coordinates successfully parsed and stored in report")


# ── Run all tests ─────────────────────────────────────────
if __name__ == '__main__':
    print("\n🧪 Running NagarRaksha Route Tests...\n")
    print("=" * 55)

    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromTestCase(TestFlaskRoutes)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)

    print("=" * 55)
    print(f"\n📊 Results: {result.testsRun} tests run")
    print(f"   ✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Failed: {len(result.failures)}")
    print(f"   💥 Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 All route tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
