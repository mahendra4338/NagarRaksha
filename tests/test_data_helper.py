# ============================================================
# tests/test_data_helper.py — Unit Tests for data_helper.py
# ============================================================
# PURPOSE: Test every function in data_helper.py independently
# RUN:     python tests/test_data_helper.py
# No extra libraries needed — uses Python's built-in unittest
# ============================================================

import unittest
import json
import os
import sys
import shutil
import tempfile

# Add parent folder to path so we can import data_helper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDataHelper(unittest.TestCase):
    """
    Test class for all data_helper.py functions.
    setUp() runs BEFORE each test — creates a clean test environment.
    tearDown() runs AFTER each test — cleans up temp files.
    """

    def setUp(self):
        """
        Create a temporary folder with empty JSON files.
        This ensures tests don't mess with your real data.
        """
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create test data files
        self.reports_file = os.path.join(self.test_dir, 'reports.json')
        self.sos_file     = os.path.join(self.test_dir, 'sos_events.json')
        self.users_file   = os.path.join(self.test_dir, 'users.json')

        with open(self.reports_file, 'w') as f:
            json.dump([], f)
        with open(self.sos_file, 'w') as f:
            json.dump([], f)

        # Patch the file paths in data_helper
        import data_helper
        data_helper.REPORTS_FILE = self.reports_file
        data_helper.SOS_FILE     = self.sos_file
        data_helper.USERS_FILE   = self.users_file

        # Now import the functions
        from data_helper import (
            save_report, get_all_reports, get_pending_reports,
            get_report_by_id, resolve_report, get_user_reports,
            get_stats, get_city_stats, get_type_stats,
            get_trend_stats, save_sos_event, read_json, write_json,
            load_users, save_user
        )
        self.save_report       = save_report
        self.get_all_reports   = get_all_reports
        self.get_pending        = get_pending_reports
        self.get_by_id          = get_report_by_id
        self.resolve            = resolve_report
        self.get_user_reports  = get_user_reports
        self.get_stats          = get_stats
        self.get_city_stats    = get_city_stats
        self.get_type_stats    = get_type_stats
        self.get_trend_stats   = get_trend_stats
        self.save_sos           = save_sos_event
        self.read_json          = read_json
        self.write_json         = write_json
        self.load_users         = load_users
        self.save_user          = save_user

    def tearDown(self):
        """Remove temporary directory after each test"""
        shutil.rmtree(self.test_dir)


    # ── Test 1: read_json on empty file ──────────────────────
    def test_01_read_empty_json(self):
        """Reading empty JSON file should return empty list"""
        result = self.read_json(self.reports_file)
        self.assertEqual(result, [])
        print("✅ Test 1 passed: read empty JSON returns []")

    # ── Test 2: read_json on missing file ────────────────────
    def test_02_read_missing_file(self):
        """Reading non-existent file should return [] not crash"""
        result = self.read_json('/nonexistent/path/file.json')
        self.assertEqual(result, [])
        print("✅ Test 2 passed: missing file returns [] safely")

    # ── Test 3: save_report creates a report ─────────────────
    def test_03_save_report(self):
        """save_report should create a report with correct fields"""
        report = self.save_report(
            user_id       = 'citizen@nr.com',
            incident_type = 'Suspicious Person',
            city          = 'Vijayawada',
            photo_path    = 'static/uploads/test.jpg',
            ai_result     = 'REAL',
            threat_level  = 'HIGH',
            reason        = 'Test reason'
        )

        # Check all required fields exist
        self.assertIn('report_id',     report)
        self.assertIn('user_id',       report)
        self.assertIn('incident_type', report)
        self.assertIn('city',          report)
        self.assertIn('threat_level',  report)
        self.assertIn('status',        report)
        self.assertIn('timestamp',     report)

        # Check values are correct
        self.assertEqual(report['user_id'],       'citizen@nr.com')
        self.assertEqual(report['incident_type'], 'Suspicious Person')
        self.assertEqual(report['city'],          'Vijayawada')
        self.assertEqual(report['ai_result'],     'REAL')
        self.assertEqual(report['threat_level'],  'HIGH')
        self.assertEqual(report['status'],        'PENDING')   # Default!

        print("✅ Test 3 passed: save_report creates correct report")

    # ── Test 4: report_id is unique ──────────────────────────
    def test_04_unique_report_ids(self):
        """Each report should get a unique ID"""
        r1 = self.save_report('u1', 'Suspicious Person', 'City1', 'p1.jpg', 'REAL', 'HIGH', 'r1')
        r2 = self.save_report('u2', 'Abandoned Object',  'City2', 'p2.jpg', 'FAKE', 'LOW',  'r2')

        self.assertNotEqual(r1['report_id'], r2['report_id'])
        print("✅ Test 4 passed: report IDs are unique")

    # ── Test 5: get_all_reports returns correct count ────────
    def test_05_get_all_reports(self):
        """get_all_reports should return all saved reports"""
        self.save_report('u1', 'Suspicious Person', 'Hyderabad', 'p1.jpg', 'REAL', 'HIGH',   'r1')
        self.save_report('u2', 'Abandoned Object',  'Guntur',    'p2.jpg', 'REAL', 'MEDIUM', 'r2')
        self.save_report('u3', 'Criminal Activity', 'Nellore',   'p3.jpg', 'FAKE', 'LOW',    'r3')

        reports = self.get_all_reports()
        self.assertEqual(len(reports), 3)
        print("✅ Test 5 passed: get_all_reports returns correct count")

    # ── Test 6: get_pending_reports ──────────────────────────
    def test_06_pending_reports(self):
        """get_pending_reports should only return PENDING reports"""
        r1 = self.save_report('u1', 'Suspicious Person', 'City1', 'p1.jpg', 'REAL', 'HIGH', 'r1')
        r2 = self.save_report('u2', 'Abandoned Object',  'City2', 'p2.jpg', 'REAL', 'LOW',  'r2')

        # Resolve one report manually
        self.resolve(r1['report_id'])

        pending = self.get_pending()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['report_id'], r2['report_id'])
        print("✅ Test 6 passed: get_pending_reports filters correctly")

    # ── Test 7: get_report_by_id ─────────────────────────────
    def test_07_get_by_id(self):
        """get_report_by_id should return correct report"""
        saved = self.save_report('u1', 'Suspicious Person', 'City1', 'p.jpg', 'REAL', 'HIGH', 'r')
        report_id = saved['report_id']

        found = self.get_by_id(report_id)
        self.assertIsNotNone(found)
        self.assertEqual(found['report_id'], report_id)

        # Test with non-existent ID
        not_found = self.get_by_id('XXXXXXXX')
        self.assertIsNone(not_found)
        print("✅ Test 7 passed: get_report_by_id works correctly")

    # ── Test 8: resolve_report ───────────────────────────────
    def test_08_resolve_report(self):
        """resolve_report should change status to RESOLVED"""
        saved = self.save_report('u1', 'Criminal Activity', 'City', 'p.jpg', 'REAL', 'CRITICAL', 'r')
        report_id = saved['report_id']

        # Should return True on success
        success = self.resolve(report_id)
        self.assertTrue(success)

        # Check status actually changed
        updated = self.get_by_id(report_id)
        self.assertEqual(updated['status'], 'RESOLVED')
        self.assertIsNotNone(updated['resolved_at'])

        # Should return False for non-existent ID
        fail = self.resolve('XXXXXXXX')
        self.assertFalse(fail)
        print("✅ Test 8 passed: resolve_report updates status correctly")

    # ── Test 9: get_user_reports ─────────────────────────────
    def test_09_user_reports(self):
        """get_user_reports should only return that user's reports"""
        self.save_report('user_A@nr.com', 'Suspicious Person', 'City1', 'p1.jpg', 'REAL', 'HIGH',   'r1')
        self.save_report('user_A@nr.com', 'Abandoned Object',  'City2', 'p2.jpg', 'REAL', 'MEDIUM', 'r2')
        self.save_report('user_B@nr.com', 'Criminal Activity', 'City3', 'p3.jpg', 'FAKE', 'LOW',    'r3')

        user_a_reports = self.get_user_reports('user_A@nr.com')
        user_b_reports = self.get_user_reports('user_B@nr.com')

        self.assertEqual(len(user_a_reports), 2)
        self.assertEqual(len(user_b_reports), 1)
        print("✅ Test 9 passed: get_user_reports filters by user correctly")

    # ── Test 10: get_stats ───────────────────────────────────
    def test_10_get_stats(self):
        """get_stats should return correct counts"""
        r1 = self.save_report('u1', 'Suspicious Person', 'City1', 'p1.jpg', 'REAL', 'HIGH',     'r1')
        r2 = self.save_report('u2', 'Abandoned Object',  'City2', 'p2.jpg', 'REAL', 'CRITICAL', 'r2')
        r3 = self.save_report('u3', 'Criminal Activity', 'City3', 'p3.jpg', 'FAKE', 'LOW',      'r3')

        # Resolve one
        self.resolve(r1['report_id'])

        stats = self.get_stats()
        self.assertEqual(stats['total'],       3)
        self.assertEqual(stats['resolved'],    1)
        self.assertEqual(stats['pending'],     2)
        self.assertEqual(stats['high_threat'], 2)   # HIGH + CRITICAL
        print("✅ Test 10 passed: get_stats returns correct numbers")

    # ── Test 11: get_city_stats ──────────────────────────────
    def test_11_city_stats(self):
        """get_city_stats should count reports per city"""
        self.save_report('u1', 'Suspicious Person', 'Vijayawada', 'p1.jpg', 'REAL', 'HIGH', 'r1')
        self.save_report('u2', 'Abandoned Object',  'Vijayawada', 'p2.jpg', 'REAL', 'LOW',  'r2')
        self.save_report('u3', 'Criminal Activity', 'Hyderabad',  'p3.jpg', 'FAKE', 'LOW',  'r3')

        stats  = self.get_city_stats()
        cities = stats['cities']
        counts = stats['counts']

        # Vijayawada should have 2, Hyderabad should have 1
        vij_idx = cities.index('Vijayawada')
        hyd_idx = cities.index('Hyderabad')
        self.assertEqual(counts[vij_idx], 2)
        self.assertEqual(counts[hyd_idx], 1)
        print("✅ Test 11 passed: get_city_stats groups by city correctly")

    # ── Test 12: save_sos_event ──────────────────────────────
    def test_12_save_sos(self):
        """save_sos_event should save and return SOS data"""
        sos = self.save_sos(
            user_id   = 'citizen@nr.com',
            latitude  = 16.5062,
            longitude = 80.6480
        )

        self.assertIn('sos_id',          sos)
        self.assertIn('case_id',         sos)
        self.assertIn('nearest_station', sos)
        self.assertIn('timestamp',       sos)
        self.assertTrue(sos['case_id'].startswith('NR-'))
        print("✅ Test 12 passed: save_sos_event works correctly")

    # ── Test 13: Edge case — empty city filter ────────────────
    def test_13_empty_reports(self):
        """Stats should work on empty database without crashing"""
        stats = self.get_stats()
        self.assertEqual(stats['total'],    0)
        self.assertEqual(stats['resolved'], 0)
        self.assertEqual(stats['pending'],  0)
        print("✅ Test 13 passed: empty database handled safely")

    # ── Test 14: load_users loads default users ────────────────
    def test_14_load_default_users(self):
        """load_users should write and return default user list if file missing"""
        users = self.load_users()
        self.assertIn('citizen@nr.com', users)
        self.assertIn('authority@nr.com', users)
        self.assertEqual(users['citizen@nr.com']['name'], 'Ravi Kumar')
        print("✅ Test 14 passed: load_users loads defaults correctly")

    # ── Test 15: register_new_user ─────────────────────────────
    def test_15_register_new_user(self):
        """save_user should register and return a new user"""
        user = self.save_user('new@nr.com', 'pass123', 'New User', 'citizen')
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'New User')
        self.assertIn('user_id', user)

        # Verify persistence
        users = self.load_users()
        self.assertIn('new@nr.com', users)
        self.assertEqual(users['new@nr.com']['password'], 'pass123')
        print("✅ Test 15 passed: save_user registers new user correctly")

    # ── Test 16: register_duplicate_user ───────────────────────
    def test_16_register_duplicate_user(self):
        """save_user should return None for duplicate email registration"""
        self.save_user('dup@nr.com', 'pass123', 'First', 'citizen')
        duplicate = self.save_user('dup@nr.com', 'otherpass', 'Second', 'citizen')
        self.assertIsNone(duplicate)
        print("✅ Test 16 passed: save_user blocks duplicate email registration")


# ── Run all tests ─────────────────────────────────────────
if __name__ == '__main__':
    print("\n🧪 Running NagarRaksha Unit Tests...\n")
    print("=" * 55)

    # Run tests and capture results
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromTestCase(TestDataHelper)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)

    print("=" * 55)
    print(f"\n📊 Results: {result.testsRun} tests run")
    print(f"   ✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Failed: {len(result.failures)}")
    print(f"   💥 Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 All tests passed! data_helper.py is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
