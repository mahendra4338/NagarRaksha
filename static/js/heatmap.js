// ============================================================
// heatmap.js — NagarRaksha Crime Heatmap
// ============================================================
// PURPOSE: Loads reports from API, plots colored markers on
//          Leaflet.js map, handles filters, auto-refreshes
// ============================================================

// Global variables
let map          = null;    // Leaflet map instance
let allReports   = [];      // All reports fetched from API
let markers      = [];      // All map markers currently shown
let refreshTimer = null;    // Auto-refresh interval


// ── Color mapping for threat levels ──────────────────────
const THREAT_COLORS = {
    'CRITICAL': '#ff2d55',   // Red
    'HIGH':     '#ff6b35',   // Orange-Red
    'MEDIUM':   '#f5a623',   // Orange
    'LOW':      '#0f9b58'    // Green
};

// ── Radius mapping (bigger = more severe) ─────────────────
const THREAT_RADIUS = {
    'CRITICAL': 14,
    'HIGH':     11,
    'MEDIUM':   8,
    'LOW':      6
};


// ── Initialize map when page loads ───────────────────────
window.addEventListener('load', function() {
    initMap();
    loadReports();
    startAutoRefresh();
});


function initMap() {
    /**
     * Creates the Leaflet map centered on India.
     *
     * L.map('map') → creates map inside the div with id="map"
     * setView([lat, lng], zoom) → centers on India, zoom level 5
     * L.tileLayer → adds the actual map background (OpenStreetMap tiles)
     * {s} = subdomain, {z} = zoom, {x}{y} = tile coordinates
     */
    map = L.map('map').setView([20.5937, 78.9629], 5);

    // Add OpenStreetMap tiles — completely FREE, no API key
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/">OpenStreetMap</a>',
        maxZoom:     18
    }).addTo(map);

    console.log('🗺️ Map initialized');
}


function loadReports() {
    /**
     * Fetches all reports from Flask API.
     * Plots markers on the map.
     * Updates report count display.
     */
    fetch('/api/reports')
        .then(response => {
            if (!response.ok) throw new Error('Failed to fetch reports');
            return response.json();
        })
        .then(reports => {
            allReports = reports;   // Store globally for filtering
            plotMarkers(reports);
            updateReportCount(reports.length);
            console.log(`📍 Loaded ${reports.length} reports`);
        })
        .catch(error => {
            console.error('Error loading reports:', error);
            document.getElementById('reportCount').textContent =
                '⚠️ Failed to load reports';
        });
}


function plotMarkers(reports) {
    /**
     * Removes all existing markers and plots new ones.
     * Called on initial load and after filtering.
     *
     * L.circleMarker → draws a circle at given coordinates
     * .bindPopup()   → adds info popup when marker is clicked
     * .addTo(map)    → adds the marker to the map
     */

    // ── Clear existing markers ────────────────────────────
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    if (reports.length === 0) {
        document.getElementById('reportCount').textContent = 'No reports match filters';
        return;
    }

    // ── Plot each report as a colored circle ──────────────
    reports.forEach(report => {
        const threat = report.threat_level || 'LOW';
        const color  = THREAT_COLORS[threat] || '#0f9b58';
        const radius = THREAT_RADIUS[threat] || 8;

        // Format timestamp for display
        const time = report.timestamp
            ? new Date(report.timestamp).toLocaleString('en-IN')
            : 'Unknown';

        // Status badge color
        const statusColor = report.status === 'RESOLVED' ? '#0f9b58' : '#f5a623';

        // Create circle marker
        const marker = L.circleMarker([report.latitude, report.longitude], {
            radius:      radius,
            fillColor:   color,
            color:       color,
            weight:      2,
            opacity:     1,
            fillOpacity: 0.8
        });

        // Popup HTML — shown when marker is clicked
        marker.bindPopup(`
            <div style="min-width:220px; font-family:'Inter', system-ui, -apple-system, sans-serif; overflow:hidden;">
                <div style="background:${color};color:white;padding:10px 14px;
                            font-weight:bold; font-size: 0.95rem; font-family: 'Outfit', sans-serif;">
                    ${getIncidentEmoji(report.incident_type)} ${report.incident_type}
                </div>
                <div style="padding:12px 14px;background:#0c0f22;color:#f3f4f6;font-size:0.88rem;">
                    <div style="margin-bottom:6px;">
                        <strong style="color:#8f9bb3;">Report ID:</strong> <code style="color:var(--accent); font-weight:600;">#${report.report_id}</code>
                    </div>
                    <div style="margin-bottom:6px;">
                        <strong style="color:#8f9bb3;">City:</strong> ${report.city}
                    </div>
                    <div style="margin-bottom:6px;">
                        <strong style="color:#8f9bb3;">Threat:</strong>
                        <span style="color:${color};font-weight:bold;">
                            ${threat}
                        </span>
                    </div>
                    <div style="margin-bottom:6px;">
                        <strong style="color:#8f9bb3;">AI Verify:</strong> <span style="font-weight:600;">${report.ai_result}</span>
                    </div>
                    <div style="margin-bottom:6px;">
                        <strong style="color:#8f9bb3;">Status:</strong>
                        <span style="color:${statusColor};font-weight:bold;">
                            ${report.status}
                        </span>
                    </div>
                    <div style="color:#8f9bb3;font-size:0.78rem;margin-top:8px;">
                        📅 ${time}
                    </div>
                    <div style="margin-top:10px;padding:10px;background:rgba(255,255,255,0.04);
                                border-radius:8px;font-size:0.82rem;line-height:1.4;border:1px solid rgba(255,255,255,0.06);color:#d1d5db;">
                        💬 ${report.reason || 'No reason provided'}
                    </div>
                </div>
            </div>
        `, {
            maxWidth: 280
        });

        marker.addTo(map);
        markers.push(marker);   // Track marker so we can remove it later
    });

    updateReportCount(reports.length);
}


// ── Filters ───────────────────────────────────────────────
function applyFilters() {
    /**
     * Reads current filter dropdown values.
     * Filters the allReports array.
     * Re-plots only matching reports.
     */
    const cityFilter   = document.getElementById('filterCity').value;
    const typeFilter   = document.getElementById('filterType').value;
    const threatFilter = document.getElementById('filterThreat').value;
    const statusFilter = document.getElementById('filterStatus').value;

    // Array.filter() keeps only items where the function returns true
    const filtered = allReports.filter(report => {
        // If filter is empty string → match all (no filter applied)
        const cityMatch   = !cityFilter   || report.city          === cityFilter;
        const typeMatch   = !typeFilter   || report.incident_type === typeFilter;
        const threatMatch = !threatFilter || report.threat_level  === threatFilter;
        const statusMatch = !statusFilter || report.status        === statusFilter;

        // Report must match ALL active filters
        return cityMatch && typeMatch && threatMatch && statusMatch;
    });

    plotMarkers(filtered);
}


function clearFilters() {
    /**Resets all filter dropdowns and shows all reports*/
    document.getElementById('filterCity').value   = '';
    document.getElementById('filterType').value   = '';
    document.getElementById('filterThreat').value = '';
    document.getElementById('filterStatus').value = '';
    plotMarkers(allReports);
}


function updateReportCount(count) {
    document.getElementById('reportCount').textContent =
        `📍 Showing ${count} report${count !== 1 ? 's' : ''}`;
}


// ── Auto-Refresh ──────────────────────────────────────────
function startAutoRefresh() {
    /**
     * Silently reloads reports every 10 seconds.
     * New reports appear on map automatically.
     * This is called "polling" — simple alternative to WebSockets.
     */
    refreshTimer = setInterval(() => {
        loadReports();   // Re-fetch from server
        console.log('🔄 Map auto-refreshed');
    }, 10000);   // 10000ms = 10 seconds
}


// ── Helper Functions ──────────────────────────────────────
function getIncidentEmoji(type) {
    const emojis = {
        'Suspicious Person':  '👤',
        'Abandoned Object':   '📦',
        'Suspicious Vehicle': '🚗',
        'Criminal Activity':  '⚠️'
    };
    return emojis[type] || '📍';
}
