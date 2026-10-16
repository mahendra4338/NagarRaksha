# ============================================================
# app.py — NagarRaksha Main Application
# ============================================================
# PURPOSE: The heart of the project.
#          Starts Flask, defines all routes (URLs),
#          connects frontend pages to backend logic.
# RUN:     python app.py
# ============================================================

from flask import (Flask, render_template, session,
                   redirect, url_for, request, jsonify)
from dotenv import load_dotenv
import os
import uuid

# Import our helper modules
from data_helper  import (save_report, get_all_reports, get_pending_reports,
                           get_report_by_id, resolve_report, get_user_reports,
                           get_stats, get_city_stats, get_type_stats,
                           get_trend_stats, save_sos_event, load_users, save_user)
from gemini_helper import analyze_image, get_mock_analysis

# ── Load environment variables from .env file ────────────────
load_dotenv()

# ── Auto-create data folders and files if missing ────────────
# This runs on Render where local data/ folder doesn't exist yet
import json as _json
os.makedirs('data', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
for _f in ['data/reports.json', 'data/sos_events.json']:
    if not os.path.exists(_f):
        with open(_f, 'w') as _fp:
            _json.dump([], _fp)
        print(f"✅ Created: {_f}")

# ── Initialize Flask app ─────────────────────────────────────
app = Flask(__name__)

# Secret key is required for Flask sessions to work
# Sessions store login info between page requests
app.secret_key = os.getenv('SECRET_KEY', 'nagarraksha-dev-key-2026')

# Limit uploaded file size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Feature flag: set USE_MOCK_AI=true in .env to skip real Gemini calls
# Useful during development to save API credits
USE_MOCK_AI = os.getenv('USE_MOCK_AI', 'false').lower() == 'true'


# ════════════════════════════════════════════════════════════
# DUMMY USER ACCOUNTS
# In a real system, these would be in a database
# ════════════════════════════════════════════════════════════
# Users are loaded and saved dynamically via data_helper (load_users, save_user)


# ════════════════════════════════════════════════════════════
# HELPER: Session Protection
# ════════════════════════════════════════════════════════════
def require_login(role=None):
    """
    Checks if user is logged in. Optionally checks role.
    Returns redirect if not authorized, None if OK.

    Usage:
        check = require_login('citizen')
        if check: return check
    """
    if 'user' not in session:
        return redirect(url_for('home'))

    if role and session.get('role') != role:
        # User is logged in but wrong role
        return redirect(url_for('home'))

    return None   # None = authorized, continue normally


# ════════════════════════════════════════════════════════════
# AUTH ROUTES — Login, Logout
# ════════════════════════════════════════════════════════════

@app.route('/')
def home():
    """Landing page — shows login form"""
    # If already logged in, redirect to their dashboard
    if 'user' in session:
        return redirect_by_role()
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """
    Handles login form submission.
    Reads email, password, role from form.
    Sets session if valid.
    Redirects to appropriate dashboard.
    """
    email    = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    role     = request.form.get('role', 'citizen')

    users = load_users()

    # Check 1: Email exists?
    if email not in users:
        return render_template('login.html',
                               error='❌ Email not found. Please check your email.')

    user = users[email]

    # Check 2: Password correct?
    if user['password'] != password:
        return render_template('login.html',
                               error='❌ Wrong password. Please try again.')

    # Check 3: Role matches?
    if user['role'] != role:
        return render_template('login.html',
                               error=f'❌ This account is registered as {user["role"]}, not {role}.')

    # All checks passed — save user info to session
    session['user']    = email
    session['role']    = user['role']
    session['name']    = user['name']
    session['user_id'] = user['user_id']

    return redirect_by_role()


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    GET  → Show user registration page
    POST → Process registration form submission
    """
    # If already logged in, redirect to their dashboard
    if 'user' in session:
        return redirect_by_role()

    if request.method == 'GET':
        return render_template('register.html')

    name     = request.form.get('name', '').strip()
    email    = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    role     = request.form.get('role', 'citizen').strip()

    # Validations
    if not name or not email or not password or not role:
        return render_template('register.html', error='❌ All fields are required.')

    if '@' not in email or '.' not in email:
        return render_template('register.html', error='❌ Invalid email format.')

    # Try registering user
    user = save_user(email, password, name, role)
    if not user:
        return render_template('register.html', error='❌ Email already registered. Try logging in.')

    # Successfully registered -> log user in automatically
    session['user']    = email
    session['role']    = user['role']
    session['name']    = user['name']
    session['user_id'] = user['user_id']

    return redirect_by_role()


def redirect_by_role():
    """Sends user to correct dashboard based on their role"""
    role = session.get('role')
    if role == 'citizen':
        return redirect(url_for('citizen_dashboard'))
    elif role == 'authority':
        return redirect(url_for('authority_dashboard'))
    elif role == 'government':
        return redirect(url_for('government_dashboard'))
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    """Clears session and sends user back to login page"""
    session.clear()
    return redirect(url_for('home'))


# ════════════════════════════════════════════════════════════
# CITIZEN ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/citizen')
def citizen_dashboard():
    """Citizen's home page — shows their reports"""
    check = require_login('citizen')
    if check: return check

    # Get only this citizen's reports
    my_reports = get_user_reports(session['user'])

    return render_template('citizen.html',
                           name=session['name'],
                           reports=my_reports,
                           total=len(my_reports),
                           pending=len([r for r in my_reports if r['status'] == 'PENDING']))


@app.route('/report', methods=['GET', 'POST'])
def report_page():
    """
    GET  → Show the report submission form
    POST → Handle form submission, call Gemini, save report
    """
    check = require_login('citizen')
    if check: return check

    if request.method == 'GET':
        return render_template('report.html', name=session['name'])

    # ── Handle POST (form submission) ─────────────────────────
    try:
        photo         = request.files.get('photo')
        incident_type = request.form.get('incident_type', '').strip()
        city          = request.form.get('city', 'Unknown').strip()
        latitude      = request.form.get('latitude')
        longitude     = request.form.get('longitude')

        # Validate inputs
        if not photo or photo.filename == '':
            return jsonify({'success': False,
                            'error': 'Please select a photo to upload.'}), 400

        if not incident_type:
            return jsonify({'success': False,
                            'error': 'Please select an incident type.'}), 400

        # Parse GPS coordinates
        try:
            lat_val = float(latitude) if latitude else 16.5062
            lng_val = float(longitude) if longitude else 80.6480
        except (ValueError, TypeError):
            lat_val = 16.5062
            lng_val = 80.6480

        # ── Save uploaded photo to disk ───────────────────────
        # Generate unique filename to avoid overwriting
        file_ext  = os.path.splitext(photo.filename)[1].lower()  # .jpg .png etc
        filename  = f"{uuid.uuid4().hex[:8]}_{incident_type.replace(' ', '_')}{file_ext}"
        photo_path = os.path.join('static', 'uploads', filename)
        photo.save(photo_path)
        print(f"📸 Photo saved: {photo_path} at location {lat_val}, {lng_val}")

        # ── Analyze with AI ───────────────────────────────────
        if USE_MOCK_AI:
            # Development mode: no real API call
            print("🔧 Using mock AI (USE_MOCK_AI=true)")
            ai_result = get_mock_analysis(incident_type)
        else:
            # Production mode: real Gemini API call
            print("🤖 Calling Gemini API...")
            ai_result = analyze_image(photo_path, incident_type)

        # ── Save report to JSON ───────────────────────────────
        report = save_report(
            user_id       = session['user'],
            incident_type = incident_type,
            city          = city,
            photo_path    = photo_path,
            ai_result     = ai_result['result'],
            threat_level  = ai_result['threat_level'],
            reason        = ai_result['reason'],
            latitude      = lat_val,
            longitude     = lng_val
        )

        # ── Return result to browser (JavaScript reads this) ──
        return jsonify({
            'success':      True,
            'report_id':    report['report_id'],
            'result':       ai_result['result'],
            'threat_level': ai_result['threat_level'],
            'reason':       ai_result['reason']
        })

    except Exception as e:
        print(f"❌ Report submission error: {e}")
        return jsonify({'success': False,
                        'error': f'Server error: {str(e)}'}), 500


@app.route('/sos')
def sos_page():
    """SOS emergency page"""
    check = require_login('citizen')
    if check: return check
    return render_template('sos.html', name=session['name'])


@app.route('/sos/trigger', methods=['POST'])
def sos_trigger():
    """
    Called when citizen presses the SOS button.
    Logs the event and returns dummy response data.
    """
    check = require_login('citizen')
    if check: return jsonify({'error': 'Not logged in'}), 401

    # Get GPS coordinates if sent from browser
    # Otherwise use Vijayawada as dummy location
    data      = request.get_json() or {}
    latitude  = data.get('latitude',  16.5062)
    longitude = data.get('longitude', 80.6480)

    # Save SOS event to JSON
    sos = save_sos_event(
        user_id   = session['user'],
        latitude  = latitude,
        longitude = longitude
    )

    return jsonify({
        'success':         True,
        'case_id':         sos['case_id'],
        'nearest_station': sos['nearest_station'],
        'distance_km':     sos['distance_km'],
        'eta_minutes':     sos['eta_minutes'],
        'timestamp':       sos['timestamp'],
        'message':         f"Help is on the way! ETA: {sos['eta_minutes']} minutes."
    })


# ════════════════════════════════════════════════════════════
# HEATMAP ROUTE (All roles can view)
# ════════════════════════════════════════════════════════════

@app.route('/heatmap')
def heatmap_page():
    """Crime heatmap — visible to all logged-in users"""
    check = require_login()
    if check: return check
    return render_template('heatmap.html',
                           name=session['name'],
                           role=session['role'])


# ════════════════════════════════════════════════════════════
# AUTHORITY ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/authority')
def authority_dashboard():
    """Authority dashboard — shows pending reports to resolve"""
    check = require_login('authority')
    if check: return check

    pending_reports  = get_pending_reports()
    resolved_reports = []

    all_reports = get_all_reports()
    resolved_reports = [r for r in all_reports if r['status'] == 'RESOLVED']

    return render_template('authority.html',
                           name=session['name'],
                           pending=pending_reports,
                           resolved=resolved_reports,
                           pending_count=len(pending_reports),
                           resolved_count=len(resolved_reports))


@app.route('/resolve/<report_id>', methods=['POST'])
def resolve_case(report_id):
    """
    Authority clicks "Mark Resolved" button.
    Updates report status in JSON.
    """
    check = require_login('authority')
    if check: return jsonify({'error': 'Not authorized'}), 401

    success = resolve_report(report_id)

    if success:
        return jsonify({'success': True,
                        'message': f'Case {report_id} marked as resolved.'})
    else:
        return jsonify({'success': False,
                        'error': 'Report not found.'}), 404


# ════════════════════════════════════════════════════════════
# GOVERNMENT ROUTES
# ════════════════════════════════════════════════════════════

@app.route('/dashboard')
def government_dashboard():
    """Government analytics dashboard"""
    check = require_login('government')
    if check: return check
    return render_template('dashboard.html', name=session['name'])


# ════════════════════════════════════════════════════════════
# API ROUTES — Return JSON data for JavaScript
# ════════════════════════════════════════════════════════════

@app.route('/api/reports')
def api_reports():
    """
    Returns all reports as JSON array.
    Used by: Leaflet.js heatmap to plot markers
    Example: fetch('/api/reports').then(r => r.json())
    """
    check = require_login()
    if check: return jsonify({'error': 'Not logged in'}), 401

    return jsonify(get_all_reports())


@app.route('/api/stats')
def api_stats():
    """
    Returns summary numbers for stat cards.
    Used by: Government dashboard
    Returns: {total, resolved, pending, high_threat}
    """
    check = require_login('government')
    if check: return jsonify({'error': 'Not authorized'}), 401

    return jsonify(get_stats())


@app.route('/api/city-stats')
def api_city_stats():
    """
    Returns crime counts per city.
    Used by: Bar chart
    Returns: {cities: [...], counts: [...]}
    """
    check = require_login('government')
    if check: return jsonify({'error': 'Not authorized'}), 401

    return jsonify(get_city_stats())


@app.route('/api/type-stats')
def api_type_stats():
    """
    Returns crime counts per incident type.
    Used by: Pie chart
    Returns: {types: [...], counts: [...]}
    """
    check = require_login('government')
    if check: return jsonify({'error': 'Not authorized'}), 401

    return jsonify(get_type_stats())


@app.route('/api/trend')
def api_trend():
    """
    Returns 30-day report trend data.
    Used by: Line chart
    Returns: {dates: [...], counts: [...]}
    """
    check = require_login('government')
    if check: return jsonify({'error': 'Not authorized'}), 401

    return jsonify(get_trend_stats())


# ════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ════════════════════════════════════════════════════════════

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page"""
    return render_template('login.html',
                           error='Page not found. Please login.'), 404


@app.errorhandler(413)
def file_too_large(e):
    """File size exceeded 16MB limit"""
    return jsonify({'success': False,
                    'error': 'File too large. Maximum size is 16MB.'}), 413


# ════════════════════════════════════════════════════════════
# START THE SERVER
# ════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # ── Development vs Production ─────────────────────────
    # debug=True  → ONLY for local development (auto-reload, error pages)
    # debug=False → ALWAYS for production (Render sets this automatically)
    #
    # On Render, gunicorn starts the app — this block doesn't run.
    # This block only runs when you do: python app.py (local dev)

    is_production = os.getenv('RENDER', False)   # Render sets RENDER=true automatically

    print("🛡️  Starting NagarRaksha Server...")
    print("📍 Visit: http://127.0.0.1:5000")
    print(f"🤖 AI Mode: {'MOCK (no API calls)' if USE_MOCK_AI else 'REAL (Gemini API)'}")
    print(f"🌍 Environment: {'PRODUCTION' if is_production else 'DEVELOPMENT'}")

    app.run(
        debug = not is_production,   # debug=True locally, debug=False on Render
        host  = '0.0.0.0',
        port  = int(os.getenv('PORT', 5000))  # Render sets PORT automatically
    )
