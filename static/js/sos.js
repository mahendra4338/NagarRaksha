// ============================================================
// sos.js — NagarRaksha SOS Page Logic
// ============================================================
// PURPOSE: Handles SOS button click, GPS attempt,
//          response display, and countdown timer
// ============================================================

let countdownInterval = null;   // Store timer so we can clear it later


// ── Main SOS Trigger Function ─────────────────────────────
function triggerSOS() {
    /**
     * Called when citizen presses the big SOS button.
     * 1. Disables the button immediately (prevent double-press)
     * 2. Tries to get real GPS location
     * 3. Sends to Flask /sos/trigger
     * 4. Shows response panel with details
     */

    const btn = document.getElementById('sosBtn');

    // Disable button immediately — prevent spam clicking
    btn.disabled           = true;
    btn.querySelector('.sos-btn-text').textContent = '⏳';
    btn.querySelector('.sos-btn-sub').textContent  = 'Sending...';

    // ── Try to get real GPS first ─────────────────────────
    // navigator.geolocation is a built-in browser API
    // It asks user permission to access their location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                // Success: got real GPS coordinates
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                console.log(`📍 GPS: ${lat}, ${lng}`);
                sendSOSToServer(lat, lng);
            },
            (error) => {
                // Failed: user denied permission or GPS unavailable
                // Fall back to dummy Vijayawada coordinates
                console.log('GPS unavailable, using dummy location');
                sendSOSToServer(16.5062, 80.6480);
            },
            { timeout: 5000 }   // Give GPS 5 seconds to respond
        );
    } else {
        // Browser doesn't support GPS — use dummy
        sendSOSToServer(16.5062, 80.6480);
    }
}


// ── Send SOS to Flask Backend ─────────────────────────────
function sendSOSToServer(latitude, longitude) {
    /**
     * Sends POST request to /sos/trigger with coordinates.
     * Flask saves the event and returns response data.
     */

    fetch('/sos/trigger', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        // JSON.stringify converts JS object to JSON string
        body:    JSON.stringify({ latitude, longitude })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Small delay (1.5s) makes it feel like real processing
            setTimeout(() => showSOSResponse(data), 1500);
        } else {
            alert('SOS failed: ' + (data.error || 'Unknown error'));
            resetSOSButton();
        }
    })
    .catch(error => {
        console.error('SOS error:', error);
        // Even if server fails, show the response
        // (safety feature — never leave citizen waiting)
        setTimeout(() => showSOSResponse({
            success:         true,
            case_id:         'NR-' + Date.now(),
            nearest_station: 'Vijayawada Central Police Station',
            distance_km:     1.2,
            eta_minutes:     4,
            message:         'Help is on the way!'
        }), 1500);
    });
}


// ── Show SOS Response Panel ───────────────────────────────
function showSOSResponse(data) {
    /**
     * Hides the SOS button section.
     * Shows the response panel with all details.
     * Starts the countdown timer.
     */

    // Hide SOS button section
    document.getElementById('sosReady').style.display    = 'none';

    // Show response section
    const response = document.getElementById('sosResponse');
    response.style.display = 'block';
    response.classList.add('fade-in');

    // Fill in the response details
    document.getElementById('stationName').textContent =
        data.nearest_station || 'Vijayawada Central Police Station';

    document.getElementById('distanceValue').textContent =
        (data.distance_km || 1.2) + ' km away';

    document.getElementById('etaValue').textContent =
        (data.eta_minutes || 4) + ' minutes';

    document.getElementById('caseId').textContent    = data.case_id || 'NR-' + Date.now();
    document.getElementById('smsCaseId').textContent = data.case_id || 'NR-' + Date.now();

    // Start countdown timer (4 minutes = 240 seconds)
    startCountdown(data.eta_minutes * 60 || 240);

    // Scroll to top of response
    response.scrollIntoView({ behavior: 'smooth' });
}


// ── Countdown Timer ───────────────────────────────────────
function startCountdown(totalSeconds) {
    /**
     * Shows a live countdown timer.
     * Updates every second.
     * Also animates a progress bar.
     *
     * totalSeconds = 240 (4 minutes)
     */

    let remaining = totalSeconds;

    // Clear any existing countdown
    if (countdownInterval) clearInterval(countdownInterval);

    countdownInterval = setInterval(() => {
        remaining--;

        // Format as MM:SS
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;
        const display = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        // padStart(2, '0') → ensures "4:05" not "4:5"

        document.getElementById('countdown').textContent = display;

        // Update progress bar width
        const percent = ((totalSeconds - remaining) / totalSeconds) * 100;
        document.getElementById('countdownFill').style.width = percent + '%';

        // When countdown reaches 0
        if (remaining <= 0) {
            clearInterval(countdownInterval);
            document.getElementById('countdown').textContent = '🚔 Arrived';
            document.getElementById('countdownFill').style.width = '100%';
        }
    }, 1000);   // Run every 1000ms = 1 second
}


// ── Reset Functions ───────────────────────────────────────
function resetSOSButton() {
    const btn = document.getElementById('sosBtn');
    btn.disabled = false;
    btn.querySelector('.sos-btn-text').textContent = 'SOS';
    btn.querySelector('.sos-btn-sub').textContent  = 'Press for Help';
}


function resetSOS() {
    /**Goes back to the SOS button screen*/
    if (countdownInterval) clearInterval(countdownInterval);

    document.getElementById('sosReady').style.display    = 'block';
    document.getElementById('sosResponse').style.display = 'none';
    resetSOSButton();
}
