// ============================================================
// report.js — NagarRaksha Report Page Logic
// ============================================================
// PURPOSE: Handles photo preview, form validation,
//          AI submission, and result display
// ============================================================


// ── Photo Preview ─────────────────────────────────────────
function previewPhoto(input) {
    /**
     * Called when user selects a photo file.
     * Shows a preview of the image before uploading.
     *
     * FileReader reads the file as a data URL (base64 image)
     * which we set as the src of an <img> tag.
     */
    const file = input.files[0];   // Get the selected file

    if (!file) return;   // No file selected — do nothing

    // Check if it's actually an image
    if (!file.type.startsWith('image/')) {
        showError('Please select an image file (JPG, PNG, WEBP).');
        return;
    }

    // Check file size (16MB max)
    if (file.size > 16 * 1024 * 1024) {
        showError('File too large. Maximum size is 16MB.');
        return;
    }

    // Read the file and show preview
    const reader = new FileReader();

    reader.onload = function(e) {
        // Hide the placeholder text
        document.getElementById('uploadPlaceholder').style.display = 'none';

        // Show the preview image
        const preview = document.getElementById('photoPreview');
        preview.src   = e.target.result;   // e.target.result = base64 image data
        preview.style.display = 'block';
    };

    reader.readAsDataURL(file);   // Read file as data URL
}


// ── Submit Report ─────────────────────────────────────────
// ── Default City Coordinates Lookup ────────────────────────
const CITY_FALLBACKS = {
    'vijayawada': { lat: 16.5062, lng: 80.6480 },
    'hyderabad':  { lat: 17.3850, lng: 78.4867 },
    'guntur':     { lat: 16.3067, lng: 80.4365 },
    'vizag':      { lat: 17.6868, lng: 83.2185 },
    'visakhapatnam': { lat: 17.6868, lng: 83.2185 },
    'nellore':    { lat: 14.4426, lng: 79.9865 },
    'tirupati':   { lat: 13.6288, lng: 79.4192 }
};

function getFallbackCoordinates(cityName) {
    const key = cityName.toLowerCase().trim();
    return CITY_FALLBACKS[key] || { lat: 16.5062, lng: 80.6480 }; // Default to Vijayawada
}

// ── Submit Report ─────────────────────────────────────────
function submitReport() {
    /**
     * Called when user clicks "Analyze with AI" button.
     * Retrieves GPS location first, then sends data to Flask.
     */

    // ── Validate inputs first ──────────────────────────────
    const photoInput   = document.getElementById('photoInput');
    const photo        = photoInput.files[0];
    const incidentType = document.getElementById('incidentType').value;
    const city         = document.getElementById('city').value.trim();

    if (!photo) {
        showError('Please select a photo to upload.');
        return;
    }

    if (!incidentType) {
        showError('Please select an incident type.');
        return;
    }

    if (!city) {
        showError('Please enter the city name.');
        return;
    }

    // ── Show loading state ────────────────────────────────
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled    = true;
    submitBtn.innerHTML   = '📍 Querying GPS Location...';
    
    document.getElementById('resultPanel').style.display  = 'block';
    document.getElementById('loadingCard').style.display   = 'block';
    document.getElementById('resultCard').style.display    = 'none';

    const loadingTextEl = document.querySelector('.loading-text');
    if (loadingTextEl) {
        loadingTextEl.textContent = '📍 Fetching your current GPS coordinates...';
    }

    // Smooth scroll to result panel
    document.getElementById('resultPanel').scrollIntoView({ behavior: 'smooth' });

    // ── Get Geolocation ───────────────────────────────────
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            // Success callback
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                console.log(`📍 GPS Location acquired: ${lat}, ${lng}`);
                sendReportToServer(photo, incidentType, city, lat, lng);
            },
            // Error callback
            (error) => {
                console.warn(`⚠️ Geolocation error (${error.code}): ${error.message}`);
                const fallback = getFallbackCoordinates(city);
                console.log(`📍 Falling back to coordinates for ${city}: ${fallback.lat}, ${fallback.lng}`);
                sendReportToServer(photo, incidentType, city, fallback.lat, fallback.lng);
            },
            // Options
            { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
        );
    } else {
        console.warn('⚠️ Geolocation is not supported by this browser.');
        const fallback = getFallbackCoordinates(city);
        sendReportToServer(photo, incidentType, city, fallback.lat, fallback.lng);
    }
}

// ── Send Report to Server Helper ──────────────────────────
function sendReportToServer(photo, incidentType, city, latitude, longitude) {
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.innerHTML = '🤖 Analyzing with AI...';

    const loadingTextEl = document.querySelector('.loading-text');
    if (loadingTextEl) {
        loadingTextEl.textContent = '🤖 AI is analyzing your photo...';
    }

    // ── Build FormData (can include files) ─────────────────
    const formData = new FormData();
    formData.append('photo',         photo);          // File object
    formData.append('incident_type', incidentType);   // String
    formData.append('city',          city);           // String
    formData.append('latitude',      latitude);       // Float
    formData.append('longitude',     longitude);      // Float

    // ── Send to Flask via fetch() ──────────────────────────
    fetch('/report', {
        method: 'POST',
        body:   formData    // FormData auto-sets correct Content-Type
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();   // Parse JSON response body
    })
    .then(data => {
        document.getElementById('loadingCard').style.display = 'none';

        if (data.success) {
            displayResult(data);   // Show AI result
        } else {
            showError(data.error || 'Analysis failed. Please try again.');
            resetSubmitButton();
        }
    })
    .catch(error => {
        document.getElementById('loadingCard').style.display = 'none';
        showError('Connection error. Please check your internet and try again.');
        console.error('Fetch error:', error);
        resetSubmitButton();
    });
}


// ── Display AI Result ─────────────────────────────────────
function displayResult(data) {
    /**
     * Shows the AI analysis result in the result card.
     * Colors and badges change based on threat level.
     *
     * data = {report_id, result, threat_level, reason}
     */

    // Show result card
    document.getElementById('resultCard').style.display = 'block';
    document.getElementById('resultCard').classList.add('fade-in');

    // Report ID
    document.getElementById('resultReportId').textContent = '#' + data.report_id;

    // REAL/FAKE badge
    const badge = document.getElementById('resultBadge');
    badge.textContent  = data.result === 'REAL' ? '🚨 REAL THREAT' : '✅ NOT A THREAT';
    badge.className    = 'badge ' + (data.result === 'REAL' ? 'badge-real' : 'badge-fake');

    // Threat level bars (like signal strength indicator)
    const levels    = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
    const colors    = ['#0f9b58', '#f5a623', '#ff6b35', '#ff2d55'];
    const levelIdx  = levels.indexOf(data.threat_level);

    // Color each bar based on threat level
    for (let i = 1; i <= 4; i++) {
        const bar = document.getElementById('bar' + i);
        if (i <= levelIdx + 1) {
            bar.style.backgroundColor = colors[levelIdx];
            bar.style.opacity         = '1';
        } else {
            bar.style.backgroundColor = 'var(--border)';
            bar.style.opacity         = '0.3';
        }
    }

    // Threat level label
    const threatLabel     = document.getElementById('threatLabel');
    threatLabel.textContent = data.threat_level;
    threatLabel.className   = 'threat-text badge badge-' + data.threat_level.toLowerCase();

    // Reason text
    document.getElementById('reasonText').textContent = data.reason;

    // Scroll to result
    document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth' });
}


// ── Helper Functions ──────────────────────────────────────
function showError(message) {
    /**Shows a temporary error alert above the form*/
    const existing = document.getElementById('errorAlert');
    if (existing) existing.remove();

    const alert       = document.createElement('div');
    alert.id          = 'errorAlert';
    alert.className   = 'alert alert-error fade-in';
    alert.textContent = '⚠️ ' + message;

    // Insert before the submit button
    const btn = document.getElementById('submitBtn');
    btn.parentNode.insertBefore(alert, btn);

    // Auto-remove after 5 seconds
    setTimeout(() => alert.remove(), 5000);
}


function resetSubmitButton() {
    const btn     = document.getElementById('submitBtn');
    btn.disabled  = false;
    btn.innerHTML = '🔍 Analyze with AI';
}


function submitAnother() {
    /**Resets the form so citizen can submit a new report*/
    document.getElementById('photoInput').value   = '';
    document.getElementById('incidentType').value = '';
    document.getElementById('city').value         = '';
    document.getElementById('uploadPlaceholder').style.display = 'block';
    document.getElementById('photoPreview').style.display      = 'none';
    document.getElementById('resultPanel').style.display       = 'none';
    resetSubmitButton();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
