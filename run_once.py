# ============================================================
# run_once.py — NagarRaksha Project Initializer
# ============================================================
# PURPOSE: Creates all necessary folders and empty data files
# RUN:     python run_once.py   (only ONE time at project start)
# WARNING: Running again will ERASE all existing report data!
# ============================================================

import json
import os

print("🚀 Setting up NagarRaksha project...")

# ── Step 1: Create all required folders ──────────────────────
folders = [
    'data',
    'static/uploads',
    'static/css',
    'static/js',
    'static/images',
    'templates',
    'tests',
    'docs'
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)   # exist_ok=True → no error if already exists
    print(f"  ✅ Created folder: {folder}/")

# ── Step 2: Create empty reports.json ────────────────────────
# This is where ALL citizen reports will be saved
with open('data/reports.json', 'w') as f:
    json.dump([], f)                      # Start with empty array []
print("  ✅ Created: data/reports.json")

# ── Step 3: Create empty sos_events.json ─────────────────────
# This is where ALL SOS button presses will be logged
with open('data/sos_events.json', 'w') as f:
    json.dump([], f)
print("  ✅ Created: data/sos_events.json")

# ── Step 4: Create .gitkeep so uploads/ folder stays in Git ──
with open('static/uploads/.gitkeep', 'w') as f:
    f.write('')
print("  ✅ Created: static/uploads/.gitkeep")

# ── Step 5: Create users.json with default demo credentials ──
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
with open('data/users.json', 'w') as f:
    json.dump(DEFAULT_USERS, f, indent=2)
print("  ✅ Created: data/users.json (with default demo users)")

print("\n✅ Setup complete! You can now run: python app.py")
print("⚠️  Remember to add your GEMINI_API_KEY to .env file first!")
