# 🛡️ NagarRaksha — AI-Powered Citizen Safety Reporting System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=flat-square&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini_AI-1.5_Flash-orange?style=flat-square&logo=google)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow?style=flat-square&logo=javascript)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Empowering Indian citizens to report suspicious activity with AI-powered photo analysis, instant SOS alerts, and live crime heatmaps.**

[🔴 Live Demo](https://nagarraksha.onrender.com) • [📸 Screenshots](#screenshots) • [🚀 Quick Start](#quick-start) • [📋 Features](#features)

> ⚠️ **Note:** Hosted on free tier — first load may take 30 seconds to wake up.

</div>

---

## 🎯 Problem Statement

In India, when a citizen witnesses suspicious activity, they hesitate to report it due to:
- No easy, fast reporting platform
- No way to submit photo evidence digitally
- No real-time awareness of crime patterns in their area
- Slow response times with no SOS option for emergencies

**NagarRaksha solves all of this.**

---

## ✨ Features

| Feature | Description | Status |
|---|---|---|
| 📷 AI Photo Analysis | Google Gemini analyzes uploaded photos for threat level | ✅ Real |
| 🗺️ Live Crime Heatmap | Leaflet.js map with colored markers by threat level | ✅ Real |
| 🆘 SOS Emergency | One-tap emergency alert with GPS location | ✅ Real |
| 📊 Analytics Dashboard | Chart.js bar, pie, and line charts with live data | ✅ Real |
| 👮 Authority Panel | Police can view and resolve reports in real-time | ✅ Real |
| 🔐 Role-Based Login | Separate dashboards for Citizen, Authority, Government | ✅ Real |
| 🔄 Auto-Refresh | Map and charts update every 10-15 seconds | ✅ Real |

---

## 🖥️ Screenshots

> *(Add screenshots of each page here after building)*

| Login Page | Report + AI Result |
|---|---|
| ![Login](docs/login.png) | ![Report](docs/report.png) |

| Crime Heatmap | Government Dashboard |
|---|---|
| ![Map](docs/heatmap.png) | ![Dashboard](docs/dashboard.png) |

---

## 🛠️ Tech Stack

```
Frontend:   HTML5, CSS3, Vanilla JavaScript
Backend:    Python 3.10, Flask 3.0
AI:         Google Gemini 1.5 Flash API
Maps:       Leaflet.js (OpenStreetMap — free, no API key)
Charts:     Chart.js 4.4
Storage:    JSON file (no database required)
Deployment: Render (backend) + GitHub Pages (static)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key (free from [Google AI Studio](https://aistudio.google.com))

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/nagarraksha.git
cd nagarraksha
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
copy .env.example .env
# Open .env and add your Gemini API key
```

Your `.env` file should look like:
```
GEMINI_API_KEY=your_key_here
SECRET_KEY=any-random-string
USE_MOCK_AI=false
```

### 4. Initialize project
```bash
python run_once.py
```

### 5. Run the application
```bash
python app.py
```

### 6. Open in browser
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Credentials

| Role | Email | Password |
|---|---|---|
| 👤 Citizen | citizen@nr.com | citizen123 |
| 👮 Authority | authority@nr.com | authority123 |
| 🏛️ Government | government@nr.com | government123 |

---

## 📁 Project Structure

```
nagarraksha/
├── app.py                 # Flask routes and main application
├── data_helper.py         # All JSON read/write operations
├── gemini_helper.py       # Google Gemini AI integration
├── run_once.py            # Project setup script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
│
├── data/
│   ├── reports.json       # All citizen reports
│   └── sos_events.json    # SOS event logs
│
├── static/
│   ├── css/               # Page-specific stylesheets
│   ├── js/                # JavaScript for each page
│   └── uploads/           # Citizen uploaded photos
│
├── templates/
│   ├── base.html          # Master layout template
│   ├── login.html         # Login page
│   ├── citizen.html       # Citizen dashboard
│   ├── report.html        # Report + AI result page
│   ├── sos.html           # SOS emergency page
│   ├── heatmap.html       # Crime heatmap
│   └── dashboard.html     # Government analytics
│
└── tests/
    ├── test_data_helper.py # Unit tests (13 cases)
    └── test_routes.py      # Integration tests (20 cases)
```

---

## 🤖 How AI Analysis Works

```
1. Citizen uploads photo
2. Flask saves photo to static/uploads/
3. gemini_helper.py sends image + structured prompt to Gemini API
4. Gemini responds with:
   RESULT: REAL or FAKE
   THREAT: LOW / MEDIUM / HIGH / CRITICAL
   REASON: One sentence explanation
5. Response parsed and saved to reports.json
6. Result displayed to citizen with threat bars
```

---

## 🔮 Future Scope

- [ ] Real police database integration
- [ ] Twilio SMS alerts to family members
- [ ] Real GPS tracking via Google Maps API
- [ ] Android and iOS mobile app
- [ ] Support for all 22 Indian languages
- [ ] Submit to Smart India Hackathon (SIH)

---

## 🧪 Running Tests

```bash
# Unit tests for data operations
python tests/test_data_helper.py

# Integration tests for Flask routes
python tests/test_routes.py
```

---

## 👨‍💻 Developer

**Gangireddy Mahendra Reddy**
B.Tech CSE (AI & ML) — RISE Krishna Sai Prakasam Group of Institutions, JNTUK

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/yourprofile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github)](https://github.com/yourusername)

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
🛡️ <strong>NagarRaksha — Safer India. One Report at a Time.</strong>
</div>
