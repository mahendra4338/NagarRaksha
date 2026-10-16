// ============================================================
// dashboard.js — NagarRaksha Government Dashboard
// ============================================================
// PURPOSE: Loads stats from API, renders Chart.js charts,
//          populates reports table, auto-refreshes every 15s
// ============================================================

// Store chart instances so we can update (not recreate) them
let barChart  = null;
let pieChart  = null;
let lineChart = null;


// ── Initialize on page load ───────────────────────────────
window.addEventListener('load', function() {
    loadStats();
    loadCityStats();
    loadTypeStats();
    loadTrendStats();
    loadReportsTable();
    startAutoRefresh();
});


// ── Stat Cards ────────────────────────────────────────────
function loadStats() {
    /**
     * Fetches summary numbers from /api/stats.
     * Updates the 4 stat cards at the top.
     */
    fetch('/api/stats')
        .then(r => r.json())
        .then(data => {
            // Update each stat card number with animation
            animateNumber('statTotal',     data.total       || 0);
            animateNumber('statResolved',  data.resolved    || 0);
            animateNumber('statPending',   data.pending     || 0);
            animateNumber('statHighThreat',data.high_threat || 0);
        })
        .catch(err => console.error('Stats error:', err));
}


function animateNumber(elementId, targetValue) {
    /**
     * Counts up from 0 to targetValue with animation.
     * Makes the dashboard feel alive and dynamic.
     *
     * Example: 0 → 1 → 2 → ... → 47
     */
    const el       = document.getElementById(elementId);
    const duration = 800;    // ms
    const steps    = 20;
    const stepTime = duration / steps;
    const increment = targetValue / steps;
    let current    = 0;

    const timer = setInterval(() => {
        current += increment;
        if (current >= targetValue) {
            el.textContent = targetValue;
            clearInterval(timer);
        } else {
            el.textContent = Math.floor(current);
        }
    }, stepTime);
}


// ── Bar Chart ─────────────────────────────────────────────
function loadCityStats() {
    /**
     * Fetches crime counts per city from /api/city-stats.
     * Renders a bar chart using Chart.js.
     */
    fetch('/api/city-stats')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('barChart').getContext('2d');

            if (barChart) {
                // Update existing chart data (don't recreate)
                barChart.data.labels            = data.cities;
                barChart.data.datasets[0].data  = data.counts;
                barChart.update();
                return;
            }

            // Create premium gradient
            const gradient = ctx.createLinearGradient(0, 0, 0, 260);
            gradient.addColorStop(0, 'rgba(59, 130, 246, 0.85)');
            gradient.addColorStop(1, 'rgba(59, 130, 246, 0.15)');

            // Create chart for the first time
            barChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.cities || [],    // City names on X axis
                    datasets: [{
                        label:           'Reports',
                        data:            data.counts || [],   // Counts on Y axis
                        backgroundColor: gradient,
                        borderColor:     '#3b82f6',
                        borderWidth:     1.5,
                        borderRadius:    8,
                        borderSkipped:   false
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#f3f4f6', font: { family: 'Inter', weight: 500 } }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#8f9bb3', font: { family: 'Inter' } },
                            grid:  { color: 'rgba(255, 255, 255, 0.04)' }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#8f9bb3', stepSize: 1, font: { family: 'Inter' } },
                            grid:  { color: 'rgba(255, 255, 255, 0.04)' }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('City stats error:', err));
}


// ── Pie Chart ─────────────────────────────────────────────
function loadTypeStats() {
    /**
     * Fetches incident type breakdown from /api/type-stats.
     * Renders a pie chart using Chart.js.
     */
    fetch('/api/type-stats')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('pieChart').getContext('2d');

            if (pieChart) {
                pieChart.data.labels           = data.types;
                pieChart.data.datasets[0].data = data.counts;
                pieChart.update();
                return;
            }

            pieChart = new Chart(ctx, {
                type: 'doughnut',   // doughnut looks cleaner than pie
                data: {
                    labels: data.types || [],
                    datasets: [{
                        data:            data.counts || [],
                        backgroundColor: [
                            'rgba(99, 102, 241, 0.85)',  // Suspicious Person — Indigo
                            'rgba(245, 158, 11, 0.85)',  // Abandoned Object — Amber
                            'rgba(6, 182, 212, 0.85)',   // Suspicious Vehicle — Cyan
                            'rgba(239, 68, 68, 0.85)'    // Criminal Activity — Red
                        ],
                        borderColor:     '#0c0f22',
                        borderWidth:     2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color:   '#f3f4f6',
                                padding: 15,
                                font:    { family: 'Inter', size: 12, weight: 500 }
                            }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Type stats error:', err));
}


// ── Line Chart ────────────────────────────────────────────
function loadTrendStats() {
    /**
     * Fetches 30-day trend data from /api/trend.
     * Renders a line chart showing report volume over time.
     */
    fetch('/api/trend')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('lineChart').getContext('2d');

            if (lineChart) {
                lineChart.data.labels           = data.dates;
                lineChart.data.datasets[0].data = data.counts;
                lineChart.update();
                return;
            }

            const lineGradient = ctx.createLinearGradient(0, 0, 0, 200);
            lineGradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
            lineGradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

            lineChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates  || [],
                    datasets: [{
                        label:           'Daily Reports',
                        data:            data.counts || [],
                        borderColor:     '#3b82f6',
                        backgroundColor: lineGradient,
                        borderWidth:     2.5,
                        pointBackgroundColor: '#3b82f6',
                        pointRadius:     4,
                        tension:         0.4,    // Smooth curve (0 = straight lines)
                        fill:            true    // Fill area under line
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: '#f3f4f6', font: { family: 'Inter', weight: 500 } }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#8f9bb3', maxTicksLimit: 10, font: { family: 'Inter' } },
                            grid:  { color: 'rgba(255,255,255,0.04)' }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#8f9bb3', stepSize: 1, font: { family: 'Inter' } },
                            grid:  { color: 'rgba(255,255,255,0.04)' }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Trend error:', err));
}


// ── Reports Table ─────────────────────────────────────────
function loadReportsTable() {
    /**
     * Fetches all reports and populates the bottom table.
     */
    fetch('/api/reports')
        .then(r => r.json())
        .then(reports => {
            const tbody = document.getElementById('reportsTableBody');

            if (!reports || reports.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align:center;
                            color:var(--text-muted);padding:30px;">
                            No reports submitted yet.
                        </td>
                    </tr>`;
                return;
            }

            // Update count
            document.getElementById('tableCount').textContent =
                `${reports.length} total`;

            // Build table rows
            tbody.innerHTML = reports.map(r => `
                <tr>
                    <td><code style="color:var(--accent)">#${r.report_id}</code></td>
                    <td>${r.city || '—'}</td>
                    <td>${getTypeEmoji(r.incident_type)} ${r.incident_type || '—'}</td>
                    <td>
                        <span class="badge badge-${(r.ai_result||'').toLowerCase()}">
                            ${r.ai_result || '—'}
                        </span>
                    </td>
                    <td>
                        <span class="badge badge-${(r.threat_level||'low').toLowerCase()}">
                            ${r.threat_level || '—'}
                        </span>
                    </td>
                    <td>
                        <span class="badge badge-${(r.status||'pending').toLowerCase()}">
                            ${r.status || '—'}
                        </span>
                    </td>
                    <td style="color:var(--text-muted);font-size:0.82rem;">
                        ${r.timestamp ? new Date(r.timestamp).toLocaleDateString('en-IN') : '—'}
                    </td>
                </tr>
            `).join('');
        })
        .catch(err => console.error('Table error:', err));
}


// ── Auto-Refresh ──────────────────────────────────────────
function startAutoRefresh() {
    /**
     * Refreshes all dashboard data every 15 seconds.
     * Charts update in place (no flicker).
     * Stat numbers count up again with animation.
     */
    setInterval(() => {
        loadStats();
        loadCityStats();
        loadTypeStats();
        loadTrendStats();
        loadReportsTable();
        console.log('📊 Dashboard auto-refreshed');
    }, 15000);   // 15000ms = 15 seconds
}


// ── Helpers ───────────────────────────────────────────────
function getTypeEmoji(type) {
    const map = {
        'Suspicious Person':  '👤',
        'Abandoned Object':   '📦',
        'Suspicious Vehicle': '🚗',
        'Criminal Activity':  '⚠️'
    };
    return map[type] || '📍';
}
