# ============================================================
# gemini_helper.py — NagarRaksha AI Module
# ============================================================
# PURPOSE: All communication with Google Gemini API
#          Only this file talks to Gemini.
#          app.py calls this file's functions.
# ============================================================

import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import os

# Load .env file so we can use GEMINI_API_KEY
load_dotenv()

# Configure Gemini with our API key
# os.getenv() reads from .env file — key never hardcoded in code
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))


def analyze_image(image_path, incident_type):
    """
    Sends an image to Gemini 1.5 Flash and returns structured analysis.

    Parameters:
        image_path    → path to the saved photo file
                        e.g. "static/uploads/abc123_photo.jpg"
        incident_type → what the citizen selected
                        e.g. "Suspicious Person"

    Returns dict:
        {
            'success':      True or False,
            'result':       'REAL' or 'FAKE',
            'threat_level': 'LOW' / 'MEDIUM' / 'HIGH' / 'CRITICAL',
            'reason':       'One sentence explanation',
            'raw':          raw Gemini response text (for debugging)
        }
    """
    try:
        # ── Step 1: Open image using Pillow ──────────────────
        # Pillow (PIL) is a Python image library
        # It can open jpg, png, webp, and most other formats
        img = Image.open(image_path)

        # ── Step 2: Write the AI prompt ──────────────────────
        # This prompt FORCES Gemini to respond in exact format
        # Very specific prompt = very predictable output = easy to parse
        prompt = f"""
You are a security analysis AI for NagarRaksha, an Indian citizen safety reporting system.
A citizen has reported a "{incident_type}" incident and uploaded this photo as evidence.

Analyze the image carefully and respond in EXACTLY this format with NO extra text:

RESULT: [write only REAL or FAKE]
THREAT: [write only LOW or MEDIUM or HIGH or CRITICAL]
REASON: [write exactly one clear sentence explaining your decision]

Definitions:
- REAL  = the photo genuinely shows suspicious activity worth investigating
- FAKE  = the photo does not show actual suspicious activity
- LOW      = minor concern, no immediate danger
- MEDIUM   = moderate concern, should be monitored
- HIGH     = serious threat, requires prompt attention
- CRITICAL = immediate danger, urgent response needed

Important:
- Base your analysis ONLY on what is visually present in the image
- Consider Indian urban context (streets, markets, stations, etc.)
- Do not add any text outside the three lines above
        """

        # ── Step 3: Load Gemini model ─────────────────────────
        # gemini-1.5-flash = free tier, fast, handles images
        # Do NOT use gemini-pro-vision (deprecated)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # ── Step 4: Send image + prompt to Gemini ────────────
        # We pass a list: [text_prompt, image]
        # Gemini reads both together
        response = model.generate_content([prompt, img])

        # Get the text response
        response_text = response.text.strip()
        print(f"🤖 Gemini raw response:\n{response_text}")

        # ── Step 5: Parse the response ────────────────────────
        result, threat, reason = parse_gemini_response(response_text)

        return {
            'success':      True,
            'result':       result,        # REAL or FAKE
            'threat_level': threat,        # LOW/MEDIUM/HIGH/CRITICAL
            'reason':       reason,        # One sentence
            'raw':          response_text  # Full response for debugging
        }

    except FileNotFoundError:
        # Image file doesn't exist at given path
        return {
            'success':      False,
            'result':       'UNKNOWN',
            'threat_level': 'LOW',
            'reason':       'Image file not found. Please try uploading again.',
            'error':        'FileNotFoundError'
        }

    except Exception as e:
        # Any other error (API timeout, quota exceeded, etc.)
        print(f"❌ Gemini error: {e}")
        return {
            'success':      False,
            'result':       'UNKNOWN',
            'threat_level': 'LOW',
            'reason':       'AI analysis temporarily unavailable. Report saved manually.',
            'error':        str(e)
        }


def parse_gemini_response(text):
    """
    Extracts RESULT, THREAT, REASON from Gemini's text.

    Why we need this:
        Even with a very specific prompt, Gemini sometimes adds
        extra spaces or slightly different formatting.
        This function handles all those cases safely.

    Example input:
        "RESULT: REAL\nTHREAT: HIGH\nREASON: Person looks suspicious."

    Example output:
        ('REAL', 'HIGH', 'Person looks suspicious.')
    """
    # Default values — used if parsing fails
    result = 'UNKNOWN'
    threat = 'LOW'
    reason = 'Analysis completed. Please review the report manually.'

    # Split response into individual lines
    lines = text.split('\n')

    for line in lines:
        line = line.strip()   # Remove extra spaces

        # ── Parse RESULT line ─────────────────────────────────
        if line.upper().startswith('RESULT:'):
            val = line.split(':', 1)[1].strip().upper()
            # split(':', 1) splits only at first colon
            # [1] gets the part after the colon
            if 'REAL' in val:
                result = 'REAL'
            elif 'FAKE' in val:
                result = 'FAKE'

        # ── Parse THREAT line ─────────────────────────────────
        elif line.upper().startswith('THREAT:'):
            val = line.split(':', 1)[1].strip().upper()
            # Check CRITICAL first (contains HIGH) — order matters!
            if 'CRITICAL' in val:
                threat = 'CRITICAL'
            elif 'HIGH' in val:
                threat = 'HIGH'
            elif 'MEDIUM' in val:
                threat = 'MEDIUM'
            elif 'LOW' in val:
                threat = 'LOW'

        # ── Parse REASON line ─────────────────────────────────
        elif line.upper().startswith('REASON:'):
            reason = line.split(':', 1)[1].strip()
            # Capitalize first letter if needed
            if reason:
                reason = reason[0].upper() + reason[1:]

    return result, threat, reason


def get_mock_analysis(incident_type):
    """
    Returns a fake but realistic AI response.
    Use this during development to save Gemini API credits.

    To use mock mode: set USE_MOCK_AI=true in .env file
    To use real mode: set USE_MOCK_AI=false in .env file

    This is called a "feature flag" — professional development pattern.
    Great to mention in interviews!
    """
    import random

    mock_responses = {
        'Suspicious Person': {
            'result': 'REAL',
            'threat_level': random.choice(['MEDIUM', 'HIGH']),
            'reason': 'Image shows an individual displaying unusual behavior patterns near a public space.'
        },
        'Abandoned Object': {
            'result': 'REAL',
            'threat_level': random.choice(['HIGH', 'CRITICAL']),
            'reason': 'Unattended bag or object detected in a public area requiring immediate inspection.'
        },
        'Suspicious Vehicle': {
            'result': random.choice(['REAL', 'FAKE']),
            'threat_level': random.choice(['LOW', 'MEDIUM']),
            'reason': 'Vehicle parked in restricted zone with no visible occupants for extended period.'
        },
        'Criminal Activity': {
            'result': 'REAL',
            'threat_level': random.choice(['HIGH', 'CRITICAL']),
            'reason': 'Image appears to capture ongoing criminal activity requiring immediate law enforcement response.'
        }
    }

    response = mock_responses.get(incident_type, {
        'result': 'UNKNOWN',
        'threat_level': 'LOW',
        'reason': 'Image analyzed. Manual review recommended.'
    })

    return {
        'success':      True,
        'result':       response['result'],
        'threat_level': response['threat_level'],
        'reason':       response['reason'],
        'raw':          '[MOCK RESPONSE - No API call made]'
    }
