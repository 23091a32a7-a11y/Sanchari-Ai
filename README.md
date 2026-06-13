# 🧭 Sanchari AI — Multilingual Travel Assistant (v2)

> **सञ्चारी** (*Sanchari*) = *Traveller* in Sanskrit

A multilingual, AI-powered travel assistant for India — runs on cloud APIs (BYOK) **or** fully offline via Ollama.

---

## ✅ Features

| Feature | Description |
|---|---|
| **💬 Multilingual Chat** | Ask anything about India travel in 6 languages |
| **🗓️ Trip Planner** | AI-generated day-by-day itineraries with costs |
| **🚦 Smart Route Finder** | Best train/flight/bus/road options by budget & preference |
| **📅 Season Recommender** | Top destinations matched to your travel month & budget |
| **🌤️ Live Weather** | Real-time weather at any Indian city (free, no API key needed) |
| **💰 Budget Tracker** | Log expenses, track savings, get AI spend advice |
| **🎫 Booking Hub** | One-click deep-links to IRCTC, OYO, MakeMyTrip, Airbnb, flights |

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🌐 Supported Languages

English · हिन्दी · తెలుగు · தமிழ் · ಕನ್ನಡ · मराठी

---

## 🤖 AI Providers

### ☁️ Cloud (BYOK)
| Provider | Key Source |
|---|---|
| **Anthropic (Claude)** | [console.anthropic.com](https://console.anthropic.com) |
| **OpenAI (GPT)** | [platform.openai.com](https://platform.openai.com) |
| **Google (Gemini)** | [aistudio.google.com](https://aistudio.google.com) |
| **Groq** | [console.groq.com](https://console.groq.com) |

### 🏠 Local (Ollama)
```bash
ollama serve
ollama pull llama3
```

---

## 🌤️ Weather (no API key needed)

Weather uses [Open-Meteo](https://open-meteo.com/) (free, no signup) + OpenStreetMap Nominatim for geocoding.
No extra keys required — it works out of the box!

---

## 💰 Budget Tracker

1. Enter your total savings / travel fund
2. Log expenses by category (transport, stay, food, activities…)
3. Watch the progress bar and status indicator
4. Hit **"Get AI Spending Advice"** for a personalised financial review

---

## 🎫 Booking Hub

All booking buttons deep-link with your entered cities and dates pre-filled:
- **Trains**: IRCTC (official), MakeMyTrip
- **Buses**: redBus
- **Flights**: IndiGo, Air India, SpiceJet, Google Flights
- **Hotels**: OYO, MakeMyTrip, Booking.com, Airbnb, Goibibo

---

## 🗂️ File Structure

```
sanchari_ai/
├── app.py            # Main Streamlit UI (all tabs)
├── translations.py   # i18n strings + l10n helpers
├── ai_backend.py     # AI routing (Ollama + Anthropic + OpenAI + Gemini + Groq)
├── requirements.txt
└── README.md
```

---

*Made with ❤️ for India*
