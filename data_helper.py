# ============================================================
# data_helper.py — NagarRaksha Data Manager
# ============================================================
# PURPOSE: All reading and writing of JSON data happens HERE
#          app.py never touches JSON files directly
#          Think of these functions as your "SQL queries"
# ============================================================

import json
import uuid
import os
from datetime import datetime

# ── File paths ───────────────────────────────────────────────
REPORTS_FILE   = 'data/reports.json'
SOS_FILE       = 'data/sos_events.json'
USERS_FILE     = 'data/users.json'



# ════════════════════════════════════════════════════════════
# CORE HELPERS — Read and Write JSON safely
# ════════════════════════════════════════════════════════════

def read_json(filepath):
    """
    Reads a JSON file and returns its contents as a Python list.
    Equivalent to: SELECT * FROM table

    Returns empty list [] if file doesn't exist or is corrupted.
    This prevents crashes if the file is missing.
    """
    try:
        if not os.path.exists(filepath):
            return []                          # File missing → return empty list

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data if isinstance(data, list) else []

    except json.JSONDecodeError:
        print(f"⚠️  Warning: {filepath} is corrupted. Returning empty list.")
        return []

    except Exception as e:
        print(f"❌ Error reading {filepath}: {e}")
        return []


def write_json(filepath, data):
    """
    Writes a Python list to a JSON file.
    Equivalent to: INSERT / UPDATE in SQL

    indent=2 makes the JSON file human-readable (formatted nicely)
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True

    except Exception as e:
        print(f"❌ Error writing {filepath}: {e}")
        return False


def generate_id(prefix=''):
    """
    Generates a unique 8-character ID.
    Example outputs: "A3F9B2C1", "NR-1719045000000"

    uuid4() generates a random unique string.
    We take first 8 characters and make them UPPERCASE.
    """
    return prefix + str(uuid.uuid4())[:8].upper()


# ════════════════════════════════════════════════════════════
# REPORTS OPERATIONS
# ════════════════════════════════════════════════════════════

def save_report(user_id, incident_type, city, photo_path,
                ai_result, threat_level, reason,
                latitude=16.5062, longitude=80.6480):
    """
    Creates a new report and saves it to reports.json
    Equivalent to: INSERT INTO reports VALUES (...)

    Parameters:
        user_id       → email of the citizen who submitted
        incident_type → Suspicious Person / Vehicle / Object / Criminal Activity
        city          → city name entered by citizen
        photo_path    → where the uploaded photo is saved
        ai_result     → REAL or FAKE (from Gemini)
        threat_level  → LOW / MEDIUM / HIGH / CRITICAL (from Gemini)
        reason        → one sentence explanation (from Gemini)
        latitude      → GPS lat (dummy default = Vijayawada)
        longitude     → GPS lng (dummy default = Vijayawada)

    Returns: the saved report dict (so Flask can send it back to browser)
    """

    # Build the complete report object
    report = {
        "report_id":     generate_id(),          # e.g. "A3F9B2C1"
        "user_id":       user_id,                # citizen@nr.com
        "incident_type": incident_type,
        "city":          city,
        "photo_path":    photo_path,
        "ai_result":     ai_result,              # REAL or FAKE
        "threat_level":  threat_level,           # LOW/MEDIUM/HIGH/CRITICAL
        "reason":        reason,
        "status":        "PENDING",              # Default — authority will resolve later
        "latitude":      float(latitude),
        "longitude":     float(longitude),
        "timestamp":     datetime.now().isoformat(),   # "2026-06-22T10:30:00"
        "resolved_at":   None                    # Filled when authority resolves
    }

    # Load existing reports from file
    reports = read_json(REPORTS_FILE)

    # Add new report to the list
    reports.append(report)

    # Save the updated list back to file
    write_json(REPORTS_FILE, reports)

    print(f"✅ Report saved: {report['report_id']} | {threat_level} | {city}")

    return report   # Return so Flask can send result to browser


def get_all_reports():
    """
    Returns ALL reports, newest first.
    Equivalent to: SELECT * FROM reports ORDER BY timestamp DESC
    Used by: heatmap page, authority dashboard, API
    """
    reports = read_json(REPORTS_FILE)

    # Sort by timestamp — newest report appears first
    # key=lambda r: r['timestamp'] → sort based on timestamp field
    reports.sort(key=lambda r: r.get('timestamp', ''), reverse=True)

    return reports


def get_pending_reports():
    """
    Returns only PENDING reports.
    Equivalent to: SELECT * FROM reports WHERE status = 'PENDING'
    Used by: Authority dashboard
    """
    reports = read_json(REPORTS_FILE)

    # List comprehension — same as a WHERE clause in SQL
    pending = [r for r in reports if r.get('status') == 'PENDING']

    return pending


def get_resolved_reports():
    """
    Returns only RESOLVED reports.
    Equivalent to: SELECT * FROM reports WHERE status = 'RESOLVED'
    """
    reports = read_json(REPORTS_FILE)
    return [r for r in reports if r.get('status') == 'RESOLVED']


def get_report_by_id(report_id):
    """
    Returns a single report matching the given ID.
    Equivalent to: SELECT * FROM reports WHERE report_id = ?
    Returns None if not found.
    """
    reports = read_json(REPORTS_FILE)

    for report in reports:
        if report.get('report_id') == report_id:
            return report

    return None   # Not found


def resolve_report(report_id):
    """
    Changes a report's status from PENDING to RESOLVED.
    Equivalent to: UPDATE reports SET status='RESOLVED' WHERE report_id = ?
    Used by: Authority dashboard "Mark Resolved" button

    Returns: True if found and updated, False if not found
    """
    reports = read_json(REPORTS_FILE)
    found   = False

    for report in reports:
        if report.get('report_id') == report_id:
            report['status']      = 'RESOLVED'
            report['resolved_at'] = datetime.now().isoformat()
            found = True
            break   # Stop searching once found — saves time

    if found:
        write_json(REPORTS_FILE, reports)   # Save changes
        print(f"✅ Report resolved: {report_id}")
        return True

    print(f"⚠️  Report not found: {report_id}")
    return False


def get_user_reports(user_id):
    """
    Returns reports submitted by one specific citizen.
    Equivalent to: SELECT * FROM reports WHERE user_id = ?
    Used by: Citizen dashboard "My Reports" table
    """
    reports = read_json(REPORTS_FILE)
    return [r for r in reports if r.get('user_id') == user_id]


# ════════════════════════════════════════════════════════════
# STATISTICS — Used by Government Dashboard
# ════════════════════════════════════════════════════════════

def get_stats():
    """
    Returns summary numbers for the 4 stat cards.
    Equivalent to multiple COUNT() queries in SQL.
    """
    reports = read_json(REPORTS_FILE)

    return {
        "total":       len(reports),
        "resolved":    len([r for r in reports if r.get('status') == 'RESOLVED']),
        "pending":     len([r for r in reports if r.get('status') == 'PENDING']),
        "high_threat": len([r for r in reports
                            if r.get('threat_level') in ['HIGH', 'CRITICAL']])
    }


def get_city_stats():
    """
    Counts reports per city.
    Equivalent to: SELECT city, COUNT(*) FROM reports GROUP BY city
    Used by: Bar chart
    """
    reports    = read_json(REPORTS_FILE)
    city_count = {}

    for report in reports:
        city = report.get('city', 'Unknown')
        # dict.get(key, default) → returns 0 if city not in dict yet
        city_count[city] = city_count.get(city, 0) + 1

    # Chart.js needs two separate lists: labels and data values
    return {
        "cities": list(city_count.keys()),
        "counts": list(city_count.values())
    }


def get_type_stats():
    """
    Counts reports per incident type.
    Equivalent to: SELECT incident_type, COUNT(*) FROM reports GROUP BY incident_type
    Used by: Pie chart
    """
    reports    = read_json(REPORTS_FILE)
    type_count = {}

    for report in reports:
        itype = report.get('incident_type', 'Unknown')
        type_count[itype] = type_count.get(itype, 0) + 1

    return {
        "types":  list(type_count.keys()),
        "counts": list(type_count.values())
    }


def get_trend_stats():
    """
    Counts reports per day for the last 30 days.
    Equivalent to:
        SELECT DATE(timestamp), COUNT(*)
        FROM reports
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp) ASC
        LIMIT 30
    Used by: Line chart
    """
    reports    = read_json(REPORTS_FILE)
    date_count = {}

    for report in reports:
        timestamp = report.get('timestamp', '')
        if timestamp:
            # "2026-06-22T10:30:00" → "2026-06-22" (just the date part)
            date = timestamp[:10]
            date_count[date] = date_count.get(date, 0) + 1

    # Sort dates in chronological order
    sorted_dates = sorted(date_count.keys())

    # Keep only last 30 days
    sorted_dates = sorted_dates[-30:]

    return {
        "dates":  sorted_dates,
        "counts": [date_count[d] for d in sorted_dates]
    }


# ════════════════════════════════════════════════════════════
# SOS OPERATIONS
# ════════════════════════════════════════════════════════════

def save_sos_event(user_id, latitude=16.5062, longitude=80.6480):
    """
    Logs an SOS button press to sos_events.json.
    Equivalent to: INSERT INTO sos_events VALUES (...)

    Returns: the SOS event dict (Flask sends it back to browser)
    """
    import time

    sos_event = {
        "sos_id":          generate_id('SOS'),
        "user_id":         user_id,
        "latitude":        float(latitude),
        "longitude":       float(longitude),
        "nearest_station": "Vijayawada Central Police Station",
        "distance_km":     1.2,
        "eta_minutes":     4,
        "case_id":         f"NR-{int(time.time() * 1000)}",  # Unique timestamp-based ID
        "timestamp":       datetime.now().isoformat()
    }

    sos_events = read_json(SOS_FILE)
    sos_events.append(sos_event)
    write_json(SOS_FILE, sos_events)

    print(f"🆘 SOS logged: {sos_event['case_id']} by {user_id}")

    return sos_event


# ════════════════════════════════════════════════════════════
# USER OPERATIONS
# ════════════════════════════════════════════════════════════

DEFAULT_USERS = {
    'citizen@nr.com': {
        'user_id':  'USR001',
        'password': 'citizen123',
        'role':     'citizen',
        'name':     'Ravi Kumar'
    },
    'authority@nr.com': {
        'user_id':  'USR002',
        'password': 'authority123',
        'role':     'authority',
        'name':     'Inspector Sharma'
    },
    'government@nr.com': {
        'user_id':  'USR003',
        'password': 'government123',
        'role':     'government',
        'name':     'Commissioner Rao'
    }
}

def load_users():
    """
    Loads users from users.json.
    If the file doesn't exist, initializes it with DEFAULT_USERS.
    """
    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_USERS, f, indent=2, ensure_ascii=False)
            return DEFAULT_USERS
        
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return data if isinstance(data, dict) else DEFAULT_USERS
    except Exception as e:
        print(f"❌ Error loading users: {e}")
        return DEFAULT_USERS

def save_user(email, password, name, role):
    """
    Adds a new user to users.json.
    Returns the user dict if successful, or None if user already exists.
    """
    users = load_users()
    
    # Check if user already exists
    if email in users:
        return None
        
    # Generate unique user_id
    user_id = generate_id('USR')
    
    # Build user info
    new_user = {
        'user_id':  user_id,
        'password': password,
        'role':     role,
        'name':     name
    }
    
    users[email] = new_user
    
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return new_user
    except Exception as e:
        print(f"❌ Error saving user: {e}")
        return None

