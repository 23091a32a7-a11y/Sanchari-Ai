"""
Sanchari AI — Multilingual Travel Assistant (Enhanced)
=======================================================
New features added:
  ✅ Smart Route Finder      — best routes based on origin, destination & budget
  ✅ Season-Based Recommender — AI suggests destinations by budget + month/season
  ✅ Weather Report           — live-ish weather via Open-Meteo (free, no key needed)
  ✅ Budget Tracker           — enter savings, log expenses, get AI spend advice
  ✅ Booking Links            — quick deep-links to IRCTC, MakeMyTrip, OYO, etc.
"""

import streamlit as st
import requests
from datetime import date

from translations import LANGUAGES, t, format_currency
from ai_backend import (
    CLOUD_PROVIDERS,
    list_ollama_models,
    stream_response,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sanchari AI 🧭",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Noto+Sans:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', 'Noto Sans', sans-serif; }

.sanchari-hero {
    background: linear-gradient(135deg, #FF6B35 0%, #F7C59F 40%, #1A936F 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: white;
    text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
.sanchari-hero h1 { font-size: 2.6rem; font-weight: 700; margin: 0; }
.sanchari-hero p  { font-size: 1.1rem; margin: 0.3rem 0 0; opacity: 0.92; }

.user-bubble {
    background: #FF6B35; color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1.1rem; margin: 0.4rem 0;
    max-width: 80%; margin-left: auto;
}
.assistant-bubble {
    background: #f0fdf4; color: #1a202c;
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1.1rem; margin: 0.4rem 0;
    max-width: 85%; border-left: 4px solid #1A936F;
}

.stButton > button { border-radius: 20px !important; font-size: 0.85rem !important; }

.sidebar-brand { font-size: 1.3rem; font-weight: 700; color: #FF6B35; margin-bottom: 0.5rem; }

.feature-badge {
    display: inline-block; background: #e8f5e9; color: #2e7d32;
    border-radius: 12px; padding: 0.2rem 0.7rem;
    font-size: 0.8rem; font-weight: 600; margin: 0.2rem;
}

.info-card {
    background: #fff8f0; border: 1px solid #FFD4B2;
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.8rem 0;
}

.weather-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px; padding: 1.5rem; color: white; text-align: center;
}
.weather-card h2 { font-size: 3rem; margin: 0; }
.weather-card p  { margin: 0.2rem 0; opacity: 0.9; }

.budget-card {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    border-radius: 16px; padding: 1.2rem; color: white;
}
.budget-card-danger {
    background: linear-gradient(135deg, #e53e3e 0%, #fc8181 100%);
    border-radius: 16px; padding: 1.2rem; color: white;
}
.budget-card-warn {
    background: linear-gradient(135deg, #d69e2e 0%, #faf089 100%);
    border-radius: 16px; padding: 1.2rem; color: #1a202c;
}

.booking-btn {
    display: inline-block; padding: 0.6rem 1.2rem;
    border-radius: 10px; font-weight: 600; font-size: 0.95rem;
    text-decoration: none; margin: 0.3rem;
    transition: opacity 0.2s;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state ───────────────────────────────────────────────────────────────
defaults = {
    "lang": "en",
    "messages": [],
    "provider_type": "cloud",
    "cloud_provider": "Anthropic (Claude)",
    "api_key": "",
    "cloud_model": CLOUD_PROVIDERS["Anthropic (Claude)"]["default_model"],
    "ollama_url": "http://localhost:11434",
    "ollama_model": "llama3",
    "quick_prompt": None,
    # Budget tracker
    "savings": 0.0,
    "expenses": [],  # list of {"label": str, "amount": float, "date": str}
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

lang = st.session_state.lang


# ── Helpers ─────────────────────────────────────────────────────────────────────

def ai_ready() -> bool:
    if st.session_state.provider_type == "cloud":
        return bool(st.session_state.api_key)
    return True


def run_stream(history, user_message) -> str:
    full = ""
    for token in stream_response(
        history=history,
        user_message=user_message,
        provider_type=st.session_state.provider_type,
        provider_name=st.session_state.cloud_provider,
        model=(
            st.session_state.cloud_model
            if st.session_state.provider_type == "cloud"
            else st.session_state.ollama_model
        ),
        api_key=st.session_state.api_key,
        ollama_url=st.session_state.ollama_url,
        language=lang,
    ):
        full += token
    return full


def get_weather(city: str) -> dict | None:
    """Geocode city with Nominatim then fetch weather from Open-Meteo (free, no key)."""
    try:
        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{city}, India", "format": "json", "limit": 1},
            headers={"User-Agent": "SanchariAI/2.0"},
            timeout=5,
        ).json()
        if not geo:
            return None
        lat, lon = geo[0]["lat"], geo[0]["lon"]
        display = geo[0].get("display_name", city).split(",")[0]

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode",
                "timezone": "Asia/Kolkata",
                "forecast_days": 1,
            },
            timeout=5,
        ).json()
        cur = weather.get("current", {})
        code = cur.get("weathercode", 0)

        # WMO weather code → emoji + description
        def decode(c):
            if c == 0:   return "☀️", "Clear sky"
            if c <= 3:   return "⛅", "Partly cloudy"
            if c <= 49:  return "🌫️", "Foggy / Drizzle"
            if c <= 67:  return "🌧️", "Rain"
            if c <= 77:  return "❄️", "Snow"
            if c <= 82:  return "🌦️", "Rain showers"
            if c <= 99:  return "⛈️", "Thunderstorm"
            return "🌡️", "Unknown"

        emoji, desc = decode(code)
        return {
            "city": display,
            "temp": cur.get("temperature_2m", "—"),
            "humidity": cur.get("relative_humidity_2m", "—"),
            "wind": cur.get("wind_speed_10m", "—"),
            "emoji": emoji,
            "desc": desc,
        }
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-brand">🧭 Sanchari AI</div>', unsafe_allow_html=True)
    st.caption("*संचारी* - Travel like a bird")
    st.divider()

    st.subheader(t("language", lang))
    selected_lang = st.selectbox(
        label="Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda k: LANGUAGES[k],
        index=list(LANGUAGES.keys()).index(lang),
        label_visibility="collapsed",
    )
    if selected_lang != lang:
        st.session_state.lang = selected_lang
        lang = selected_lang
        st.rerun()

    st.divider()

    st.subheader(t("ai_provider", lang))
    provider_options = [t("provider_cloud", lang), t("provider_local", lang)]
    provider_choice = st.radio(
        "Provider Type", options=provider_options,
        index=0 if st.session_state.provider_type == "cloud" else 1,
        label_visibility="collapsed",
    )
    st.session_state.provider_type = "cloud" if provider_options.index(provider_choice) == 0 else "local"
    st.divider()

    if st.session_state.provider_type == "cloud":
        st.markdown("**☁️ BYOK — Bring Your Own Key**")
        chosen_provider = st.selectbox(
            t("api_provider_label", lang),
            options=list(CLOUD_PROVIDERS.keys()),
            index=list(CLOUD_PROVIDERS.keys()).index(st.session_state.cloud_provider),
        )
        st.session_state.cloud_provider = chosen_provider
        provider_cfg = CLOUD_PROVIDERS[chosen_provider]
        st.caption(f"Get key → {provider_cfg['docs']}")

        api_key_input = st.text_input(
            t("api_key_label", lang),
            value=st.session_state.api_key,
            type="password",
            placeholder=provider_cfg["key_hint"],
        )
        st.session_state.api_key = api_key_input

        chosen_model = st.selectbox(
            t("model_label", lang),
            options=provider_cfg["models"],
            index=(
                provider_cfg["models"].index(st.session_state.cloud_model)
                if st.session_state.cloud_model in provider_cfg["models"]
                else 0
            ),
        )
        st.session_state.cloud_model = chosen_model

        if st.session_state.api_key:
            st.success("✅ Key saved (session only)")
        else:
            st.warning(t("no_api_key", lang))
    else:
        st.markdown("**🏠 Ollama Local Inference**")
        st.caption("Run AI 100% on your machine.")
        ollama_url = st.text_input(t("ollama_url", lang), value=st.session_state.ollama_url)
        st.session_state.ollama_url = ollama_url
        local_models = list_ollama_models(ollama_url)
        if local_models:
            st.session_state.ollama_model = st.selectbox(
                "Select Model", options=local_models,
                index=local_models.index(st.session_state.ollama_model)
                if st.session_state.ollama_model in local_models else 0,
            )
            st.success(f"✅ {len(local_models)} model(s) found")
        else:
            st.session_state.ollama_model = st.text_input("Model name", value=st.session_state.ollama_model)
            st.info("Start Ollama: `ollama serve`")

    st.divider()
    if st.button("🗑️ " + t("clear_chat", lang).replace("🗑️ ", ""), use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="sanchari-hero">
        <h1>{t('app_title', lang)}</h1>
        <p>{t('app_subtitle', lang)}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_chat, tab_planner, tab_route, tab_season, tab_weather, tab_budget, tab_booking, tab_about = st.tabs([
    t("tab_chat", lang),
    t("tab_planner", lang),
    "🚦 Routes",
    "📅 Season Picks",
    "🌤️ Weather",
    "💰 Budget Tracker",
    "🎫 Bookings",
    t("tab_about", lang),
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown(f"**{t('quick_prompts_title', lang)}**")
    quick_prompts = t("quick_prompts", lang)
    cols = st.columns(3)
    for idx, prompt in enumerate(quick_prompts):
        if cols[idx % 3].button(prompt, key=f"qp_{idx}", use_container_width=True):
            st.session_state.quick_prompt = prompt
    st.divider()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧳" if msg["role"] == "user" else "🧭"):
            st.markdown(msg["content"])

    prefill = st.session_state.get("quick_prompt") or ""
    if prefill:
        st.session_state.quick_prompt = None

    user_input = st.chat_input(t("chat_placeholder", lang))
    final_input = user_input or prefill or None

    if final_input:
        if not ai_ready():
            st.warning(t("no_api_key", lang))
            st.stop()

        st.session_state.messages.append({"role": "user", "content": final_input})
        with st.chat_message("user", avatar="🧳"):
            st.markdown(final_input)

        with st.chat_message("assistant", avatar="🧭"):
            placeholder = st.empty()
            full_response = ""
            placeholder.markdown(t("thinking", lang))
            try:
                for token in stream_response(
                    history=st.session_state.messages[:-1],
                    user_message=final_input,
                    provider_type=st.session_state.provider_type,
                    provider_name=st.session_state.cloud_provider,
                    model=(
                        st.session_state.cloud_model
                        if st.session_state.provider_type == "cloud"
                        else st.session_state.ollama_model
                    ),
                    api_key=st.session_state.api_key,
                    ollama_url=st.session_state.ollama_url,
                    language=lang,
                ):
                    full_response += token
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                placeholder.error(f"{t('error_prefix', lang)}: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TRIP PLANNER
# ══════════════════════════════════════════════════════════════════════════════
with tab_planner:
    st.subheader("🗓️ Trip Planner")
    col1, col2 = st.columns([2, 1])

    with col1:
        destination = st.text_input(
            t("planner_destination", lang),
            placeholder=t("planner_dest_placeholder", lang),
        )
        interests_options = [
            "🏛️ History & Heritage", "🍛 Food & Cuisine", "🌿 Nature & Wildlife",
            "🏖️ Beaches", "⛰️ Trekking & Adventure", "🛕 Temples & Spirituality",
            "🎭 Arts & Culture", "🛍️ Shopping & Markets",
        ]
        interests = st.multiselect(
            t("planner_interests", lang), options=interests_options,
            default=["🏛️ History & Heritage", "🍛 Food & Cuisine"],
        )

    with col2:
        days = st.number_input(t("planner_days", lang), min_value=1, max_value=30, value=5)
        budget = st.select_slider(
            t("planner_budget", lang),
            options=[5000, 10000, 20000, 50000, 100000, 200000],
            value=20000,
            format_func=lambda x: format_currency(x, lang),
        )
        travellers = st.number_input("👥 Travellers", min_value=1, max_value=20, value=2)

    if st.button(t("planner_generate", lang), type="primary", use_container_width=True):
        if not destination:
            st.warning("Please enter a destination.")
        elif not ai_ready():
            st.warning(t("no_api_key", lang))
        else:
            prompt = (
                f"Create a detailed {days}-day travel itinerary for {destination}, India "
                f"for {travellers} traveller(s) with a total budget of {format_currency(budget, lang)}. "
                f"Interests: {', '.join(interests)}. "
                f"Include day-by-day breakdown, top attractions, local food recommendations, "
                f"transportation tips, accommodation suggestions, and approximate costs in ₹. "
                f"Make it practical and culturally authentic."
            )
            with st.spinner(t("thinking", lang)):
                result_area = st.empty()
                full_response = ""
                try:
                    for token in stream_response(
                        history=[], user_message=prompt,
                        provider_type=st.session_state.provider_type,
                        provider_name=st.session_state.cloud_provider,
                        model=(st.session_state.cloud_model if st.session_state.provider_type == "cloud" else st.session_state.ollama_model),
                        api_key=st.session_state.api_key,
                        ollama_url=st.session_state.ollama_url,
                        language=lang,
                    ):
                        full_response += token
                        result_area.markdown(full_response + "▌")
                    result_area.markdown(full_response)
                    st.session_state.messages.extend([
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": full_response},
                    ])
                    st.success("✅ Itinerary saved to chat history!")
                except Exception as e:
                    st.error(f"{t('error_prefix', lang)}: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SMART ROUTE FINDER  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_route:
    st.subheader("🚦 Smart Route Finder")
    st.caption("Enter your origin, destination, and budget — get the best ways to travel with pros, cons, and costs.")

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        origin = st.text_input("📍 From", placeholder="e.g., Hyderabad")
    with rc2:
        dest_route = st.text_input("🎯 To", placeholder="e.g., Goa")
    with rc3:
        route_budget = st.number_input("💰 Budget (₹)", min_value=500, max_value=500000, value=5000, step=500)

    travel_prefs = st.multiselect(
        "Travel preferences",
        ["🚅 Fastest", "💸 Cheapest", "🛋️ Most Comfortable", "🌄 Scenic", "🚗 Flexible (own vehicle)"],
        default=["💸 Cheapest"],
    )
    travellers_r = st.number_input("👥 Travellers", min_value=1, max_value=20, value=1, key="travellers_route")

    if st.button("🔍 Find Best Routes", type="primary", use_container_width=True, key="find_routes"):
        if not origin or not dest_route:
            st.warning("Please enter both origin and destination.")
        elif not ai_ready():
            st.warning(t("no_api_key", lang))
        else:
            prompt = (
                f"I want to travel from {origin} to {dest_route} in India "
                f"for {travellers_r} person(s) with a budget of ₹{route_budget:,} total.\n"
                f"Travel preferences: {', '.join(travel_prefs)}.\n\n"
                f"Please provide a detailed comparison of ALL realistic travel options including:\n"
                f"1. Flight options (if applicable) — airlines, approximate fares, duration, booking tips\n"
                f"2. Train options — train names/numbers, class recommendations, fares, journey time, IRCTC booking tips\n"
                f"3. Bus options — operators, types (Volvo/sleeper/AC), fares, duration\n"
                f"4. Road trip / self-drive — distance, toll costs, fuel estimate, highway route\n"
                f"For each option include: ✅ Pros, ❌ Cons, ₹ Estimated Cost, ⏱ Duration.\n"
                f"End with a clear RECOMMENDATION based on the stated preferences and budget.\n"
                f"All costs in Indian Rupees (₹)."
            )
            with st.spinner("🔍 Analysing routes..."):
                result = st.empty()
                full = ""
                try:
                    for token in stream_response(
                        history=[], user_message=prompt,
                        provider_type=st.session_state.provider_type,
                        provider_name=st.session_state.cloud_provider,
                        model=(st.session_state.cloud_model if st.session_state.provider_type == "cloud" else st.session_state.ollama_model),
                        api_key=st.session_state.api_key,
                        ollama_url=st.session_state.ollama_url,
                        language=lang,
                    ):
                        full += token
                        result.markdown(full + "▌")
                    result.markdown(full)
                    st.session_state.messages.extend([
                        {"role": "user", "content": f"Best routes from {origin} to {dest_route}"},
                        {"role": "assistant", "content": full},
                    ])
                except Exception as e:
                    st.error(f"{t('error_prefix', lang)}: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — SEASON-BASED DESTINATION RECOMMENDER  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_season:
    st.subheader("📅 Season-Based Destination Recommender")
    st.caption("Tell us your travel month and budget — get personalized destination picks.")

    sc1, sc2 = st.columns(2)
    with sc1:
        travel_month = st.selectbox(
            "📆 When are you planning to travel?",
            ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"],
            index=date.today().month - 1,
        )
        season_budget = st.select_slider(
            "💰 Total Budget per person (₹)",
            options=[3000, 5000, 10000, 20000, 30000, 50000, 100000, 200000],
            value=20000,
            format_func=lambda x: format_currency(x, lang),
        )
    with sc2:
        duration_days = st.number_input("📅 Trip Duration (days)", min_value=1, max_value=30, value=4)
        travel_style = st.multiselect(
            "🎒 Travel Style",
            ["🏖️ Beaches & Relaxation", "🏔️ Mountains & Adventure",
             "🛕 Culture & Heritage", "🌿 Nature & Wildlife",
             "🎉 Festivals & Events", "🍛 Food & Culinary",
             "💑 Romantic / Honeymoon", "👨‍👩‍👧 Family-friendly"],
            default=["🏖️ Beaches & Relaxation"],
        )
        origin_city = st.text_input("📍 Travelling from (optional)", placeholder="e.g., Bangalore")

    if st.button("✨ Recommend Destinations", type="primary", use_container_width=True, key="season_rec"):
        if not ai_ready():
            st.warning(t("no_api_key", lang))
        else:
            from_text = f" travelling from {origin_city}" if origin_city else ""
            prompt = (
                f"I'm planning a {duration_days}-day trip in {travel_month}{from_text} "
                f"with a budget of {format_currency(season_budget, lang)} per person.\n"
                f"Travel style preferences: {', '.join(travel_style)}.\n\n"
                f"Please recommend the TOP 5 destinations in India perfectly suited for {travel_month}, "
                f"this budget, and these preferences. For each destination:\n"
                f"- 📍 Name & State\n"
                f"- 🌤️ Why {travel_month} is great/avoid for this place\n"
                f"- 🎯 Top 3 things to do\n"
                f"- 💰 Realistic budget breakdown (stay/food/transport/activities) in ₹\n"
                f"- 🚆 How to reach it\n"
                f"- ⚠️ Any cautions or seasonal advisories\n\n"
                f"Also mention 1-2 hidden gems or off-beat alternatives."
            )
            with st.spinner("✨ Finding best destinations for your season & budget..."):
                result = st.empty()
                full = ""
                try:
                    for token in stream_response(
                        history=[], user_message=prompt,
                        provider_type=st.session_state.provider_type,
                        provider_name=st.session_state.cloud_provider,
                        model=(st.session_state.cloud_model if st.session_state.provider_type == "cloud" else st.session_state.ollama_model),
                        api_key=st.session_state.api_key,
                        ollama_url=st.session_state.ollama_url,
                        language=lang,
                    ):
                        full += token
                        result.markdown(full + "▌")
                    result.markdown(full)
                    st.session_state.messages.extend([
                        {"role": "user", "content": f"Recommend destinations for {travel_month} with budget {format_currency(season_budget, lang)}"},
                        {"role": "assistant", "content": full},
                    ])
                except Exception as e:
                    st.error(f"{t('error_prefix', lang)}: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — WEATHER REPORT  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_weather:
    st.subheader("🌤️ Live Weather Report")
    st.caption("Check current weather at any Indian city before you travel. Powered by Open-Meteo (free, no API key needed).")

    wc1, wc2 = st.columns([3, 1])
    with wc1:
        weather_city = st.text_input("🏙️ Enter city name", placeholder="e.g., Manali, Jaisalmer, Kochi...")
    with wc2:
        st.write("")
        st.write("")
        check_weather = st.button("🔍 Check Weather", type="primary", use_container_width=True)

    if check_weather and weather_city:
        with st.spinner(f"Fetching weather for {weather_city}..."):
            wd = get_weather(weather_city)

        if wd:
            ww1, ww2, ww3, ww4 = st.columns(4)
            ww1.metric("🌡️ Temperature", f"{wd['temp']}°C")
            ww2.metric("💧 Humidity", f"{wd['humidity']}%")
            ww3.metric("💨 Wind Speed", f"{wd['wind']} km/h")
            ww4.metric("🌥️ Condition", f"{wd['emoji']} {wd['desc']}")

            st.info(f"📍 Showing weather for: **{wd['city']}**")

            # AI travel tip based on weather
            if ai_ready():
                with st.expander("🧭 AI Travel Tip for this weather", expanded=True):
                    tip_prompt = (
                        f"Current weather in {wd['city']}: {wd['temp']}°C, {wd['desc']}, "
                        f"humidity {wd['humidity']}%, wind {wd['wind']} km/h.\n"
                        f"Give a short, practical travel advisory for a tourist visiting {wd['city']} today: "
                        f"what to wear, what to carry, best activities for this weather, and any cautions. "
                        f"Keep it friendly and under 150 words."
                    )
                    tip_area = st.empty()
                    tip = ""
                    try:
                        for token in stream_response(
                            history=[], user_message=tip_prompt,
                            provider_type=st.session_state.provider_type,
                            provider_name=st.session_state.cloud_provider,
                            model=(st.session_state.cloud_model if st.session_state.provider_type == "cloud" else st.session_state.ollama_model),
                            api_key=st.session_state.api_key,
                            ollama_url=st.session_state.ollama_url,
                            language=lang,
                        ):
                            tip += token
                            tip_area.markdown(tip + "▌")
                        tip_area.markdown(tip)
                    except Exception:
                        tip_area.info("Configure an AI provider in the sidebar for travel tips.")
            else:
                st.info("Configure an AI provider in the sidebar to get personalized travel tips for this weather.")
        else:
            st.error(f"Could not fetch weather for **{weather_city}**. Try a different spelling or a nearby major city.")

    elif check_weather and not weather_city:
        st.warning("Please enter a city name.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — BUDGET TRACKER  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_budget:
    st.subheader("💰 Travel Budget Tracker")
    st.caption("Enter your savings, log trip expenses, and get AI-powered advice on whether to proceed or pause.")

    # ── Setup savings ──────────────────────────────────────────────────────────
    bt1, bt2 = st.columns([2, 1])
    with bt1:
        new_savings = st.number_input(
            "🏦 Your available savings / travel fund (₹)",
            min_value=0, value=int(st.session_state.savings), step=1000,
        )
        if new_savings != st.session_state.savings:
            st.session_state.savings = float(new_savings)

    total_spent = sum(e["amount"] for e in st.session_state.expenses)
    remaining = st.session_state.savings - total_spent
    pct_used = (total_spent / st.session_state.savings * 100) if st.session_state.savings > 0 else 0

    with bt2:
        if st.session_state.savings > 0:
            if pct_used < 60:
                card_cls = "budget-card"
                status = "✅ On track"
            elif pct_used < 85:
                card_cls = "budget-card-warn"
                status = "⚠️ Watch spending"
            else:
                card_cls = "budget-card-danger"
                status = "🚨 Over budget!"

            st.markdown(
                f"""<div class="{card_cls}">
                <b>{status}</b><br>
                Spent: ₹{total_spent:,.0f} ({pct_used:.0f}%)<br>
                Remaining: ₹{remaining:,.0f}
                </div>""",
                unsafe_allow_html=True,
            )

    if st.session_state.savings > 0:
        st.progress(min(pct_used / 100, 1.0))

    st.divider()

    # ── Add expense ────────────────────────────────────────────────────────────
    st.markdown("**➕ Log an Expense**")
    ec1, ec2, ec3, ec4 = st.columns([3, 2, 2, 1])
    with ec1:
        exp_label = st.text_input("Description", placeholder="e.g., Train ticket BLR-GOA", label_visibility="collapsed")
    with ec2:
        exp_amount = st.number_input("Amount (₹)", min_value=0, value=0, step=100, label_visibility="collapsed")
    with ec3:
        exp_cat = st.selectbox("Category", ["🚆 Transport", "🏨 Stay", "🍛 Food", "🎭 Activities", "🛍️ Shopping", "🏥 Medical", "📦 Misc"], label_visibility="collapsed")
    with ec4:
        st.write("")
        add_exp = st.button("Add", use_container_width=True)

    if add_exp and exp_label and exp_amount > 0:
        st.session_state.expenses.append({
            "label": exp_label,
            "amount": float(exp_amount),
            "category": exp_cat,
            "date": date.today().strftime("%d %b"),
        })
        st.rerun()

    # ── Expense table ──────────────────────────────────────────────────────────
    if st.session_state.expenses:
        st.markdown("**📋 Expense Log**")
        for i, exp in enumerate(st.session_state.expenses):
            ec1, ec2, ec3, ec4 = st.columns([3, 2, 1, 1])
            ec1.write(f"{exp['category']} {exp['label']}")
            ec2.write(f"₹{exp['amount']:,.0f}")
            ec3.write(exp.get("date", ""))
            if ec4.button("🗑️", key=f"del_exp_{i}"):
                st.session_state.expenses.pop(i)
                st.rerun()

        st.markdown(f"**Total: ₹{total_spent:,.0f}** | Remaining: ₹{remaining:,.0f}")

        st.divider()

        # ── AI financial advice ────────────────────────────────────────────────
        if st.button("🤖 Get AI Spending Advice", type="primary", use_container_width=True):
            if not ai_ready():
                st.warning(t("no_api_key", lang))
            else:
                exp_summary = "\n".join(
                    f"- {e['category']} {e['label']}: ₹{e['amount']:,.0f}" for e in st.session_state.expenses
                )
                advice_prompt = (
                    f"I'm on a trip in India. My total travel savings are ₹{st.session_state.savings:,.0f}.\n"
                    f"My expenses so far:\n{exp_summary}\n"
                    f"Total spent: ₹{total_spent:,.0f} ({pct_used:.0f}% of budget).\n"
                    f"Remaining: ₹{remaining:,.0f}.\n\n"
                    f"Please analyse my spending:\n"
                    f"1. Is my spending pattern healthy? Which categories are high?\n"
                    f"2. Should I continue travelling as planned, slow down, or cut something?\n"
                    f"3. Give 3-5 practical money-saving tips specific to Indian travel.\n"
                    f"4. Final verdict: Can I comfortably continue, or should I be cautious?\n"
                    f"Be direct, helpful, and practical."
                )
                with st.spinner("🤖 Analysing your budget..."):
                    advice_area = st.empty()
                    advice_text = ""
                    try:
                        for token in stream_response(
                            history=[], user_message=advice_prompt,
                            provider_type=st.session_state.provider_type,
                            provider_name=st.session_state.cloud_provider,
                            model=(st.session_state.cloud_model if st.session_state.provider_type == "cloud" else st.session_state.ollama_model),
                            api_key=st.session_state.api_key,
                            ollama_url=st.session_state.ollama_url,
                            language=lang,
                        ):
                            advice_text += token
                            advice_area.markdown(advice_text + "▌")
                        advice_area.markdown(advice_text)
                    except Exception as e:
                        advice_area.error(f"Error: {e}")

        if st.button("🗑️ Clear All Expenses", use_container_width=True):
            st.session_state.expenses = []
            st.rerun()
    else:
        st.info("No expenses logged yet. Add your first expense above to start tracking.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — BOOKINGS  (NEW)
# ══════════════════════════════════════════════════════════════════════════════
with tab_booking:
    st.subheader("🎫 Book Your Trip")
    st.caption("Quick links to official Indian booking platforms. All links open in a new tab.")

    # ── Train Booking ──────────────────────────────────────────────────────────
    st.markdown("### 🚆 Train Tickets")
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        book_from = st.text_input("From Station", placeholder="e.g., NDLS, HYB, MAS")
    with bc2:
        book_to = st.text_input("To Station", placeholder="e.g., MMCT, SBC, ADI")
    with bc3:
        book_date = st.date_input("Journey Date", value=date.today())

    date_str = book_date.strftime("%Y%m%d")
    irctc_url = (
        f"https://www.irctc.co.in/nget/train-search?from={book_from.upper()}&to={book_to.upper()}&date={date_str}&class=SL"
        if book_from and book_to
        else "https://www.irctc.co.in/nget/train-search"
    )
    makemytrip_train = f"https://www.makemytrip.com/railways/?from={book_from}&to={book_to}" if book_from and book_to else "https://www.makemytrip.com/railways/"

    st.markdown(
        f"""
        <a href="{irctc_url}" target="_blank" class="booking-btn" style="background:#1a56db;color:white;">
            🚆 Book on IRCTC (Official)
        </a>
        <a href="{makemytrip_train}" target="_blank" class="booking-btn" style="background:#e84393;color:white;">
            🚆 MakeMyTrip Trains
        </a>
        <a href="https://www.redbus.in/" target="_blank" class="booking-btn" style="background:#ef4444;color:white;">
            🚌 redBus (Buses)
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Flight Booking ─────────────────────────────────────────────────────────
    st.markdown("### ✈️ Flights")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        flight_from = st.text_input("Origin Airport", placeholder="e.g., HYD, BLR, DEL", key="ff")
    with fc2:
        flight_to = st.text_input("Dest Airport", placeholder="e.g., BOM, COK, JAI", key="ft")
    with fc3:
        flight_date = st.date_input("Departure Date", value=date.today(), key="fd")

    fdate = flight_date.strftime("%Y-%m-%d")
    st.markdown(
        f"""
        <a href="https://www.makemytrip.com/flights/cheap-flights-from-{flight_from.lower()}-to-{flight_to.lower()}.html"
           target="_blank" class="booking-btn" style="background:#e84393;color:white;">
            ✈️ MakeMyTrip Flights
        </a>
        <a href="https://www.goindigo.in/" target="_blank" class="booking-btn" style="background:#0033a0;color:white;">
            ✈️ IndiGo
        </a>
        <a href="https://www.airindia.com/" target="_blank" class="booking-btn" style="background:#ef4444;color:white;">
            ✈️ Air India
        </a>
        <a href="https://www.spicejet.com/" target="_blank" class="booking-btn" style="background:#ff5733;color:white;">
            ✈️ SpiceJet
        </a>
        <a href="https://www.google.com/travel/flights/search?tfs=CBwQAhoeEgoyMDI1LTAxLTAxagcIARIDSFlEcgcIARIDQkxSQAFIAXABggELCP___________wGYAQI"
           target="_blank" class="booking-btn" style="background:#4285f4;color:white;">
            ✈️ Google Flights (compare all)
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Hotel Booking ──────────────────────────────────────────────────────────
    st.markdown("### 🏨 Hotels")
    hc1, hc2, hc3 = st.columns(3)
    with hc1:
        hotel_city = st.text_input("City", placeholder="e.g., Goa, Manali, Agra", key="hc")
    with hc2:
        checkin = st.date_input("Check-in", value=date.today(), key="ci")
    with hc3:
        checkout = st.date_input("Check-out", value=date.today(), key="co")

    ci_str = checkin.strftime("%Y-%m-%d")
    co_str = checkout.strftime("%Y-%m-%d")
    city_enc = hotel_city.replace(" ", "%20")

    st.markdown(
        f"""
        <a href="https://www.oyorooms.com/s/?location={city_enc}&checkin={ci_str}&checkout={co_str}"
           target="_blank" class="booking-btn" style="background:#ef4444;color:white;">
            🏨 OYO Rooms
        </a>
        <a href="https://www.makemytrip.com/hotels/{city_enc.lower()}-hotels.html"
           target="_blank" class="booking-btn" style="background:#e84393;color:white;">
            🏨 MakeMyTrip Hotels
        </a>
        <a href="https://www.booking.com/searchresults.html?ss={city_enc}&checkin={ci_str}&checkout={co_str}"
           target="_blank" class="booking-btn" style="background:#003580;color:white;">
            🏨 Booking.com
        </a>
        <a href="https://www.airbnb.co.in/s/{city_enc}/homes?checkin={ci_str}&checkout={co_str}"
           target="_blank" class="booking-btn" style="background:#ff5a5f;color:white;">
            🏠 Airbnb India
        </a>
        <a href="https://www.goibibo.com/hotels/{city_enc.lower()}-hotels/"
           target="_blank" class="booking-btn" style="background:#1a936f;color:white;">
            🏨 Goibibo
        </a>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── AI Booking Advice ──────────────────────────────────────────────────────
    st.markdown("### 🤖 Not sure what to book? Ask Sanchari!")
    booking_q = st.text_area(
        "Describe your trip and ask for booking advice",
        placeholder="e.g., I want to go from Hyderabad to Coorg for 3 nights in October with ₹15,000 budget. What's the best combo of train + bus + hotel to book?",
        height=100,
    )
    if st.button("💬 Get Booking Advice", type="primary", key="booking_advice"):
        if not booking_q:
            st.warning("Please describe your trip.")
        elif not ai_ready():
            st.warning(t("no_api_key", lang))
        else:
            prompt = (
                f"Travel booking question for India: {booking_q}\n\n"
                f"Please give practical, specific booking advice including:\n"
                f"- Which platforms to use and why\n"
                f"- Best booking timing (how far in advance)\n"
                f"- Specific train names/numbers if relevant\n"
                f"- Money-saving tips and traps to avoid\n"
                f"- Any important notes for Indian travel booking"
            )
            with st.spinner("🤖 Getting booking advice..."):
                ba = st.empty()
                ba_text = ""
                try:
                    for token in stream_response(
                        history=[], user_message=prompt,
                        provider_type=st.session_state.provider_type,
                        provider_name=st.session_state.cloud_provider,
                        model=(st.session_state.cloud_model if st.session_state.provider_type == "cloud" else st.session_state.ollama_model),
                        api_key=st.session_state.api_key,
                        ollama_url=st.session_state.ollama_url,
                        language=lang,
                    ):
                        ba_text += token
                        ba.markdown(ba_text + "▌")
                    ba.markdown(ba_text)
                except Exception as e:
                    ba.error(f"Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — ABOUT
# ══════════════════════════════════════════════════════════════════════════════
with tab_about:
    st.subheader(t("about_title", lang))
    st.markdown(t("about_desc", lang))
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🌐 Supported Languages")
        for code, name in LANGUAGES.items():
            st.markdown(f"- {name} `{code}`")

        st.markdown("### 🤖 AI Providers")
        st.markdown("**Cloud (BYOK):** Anthropic, OpenAI, Google Gemini, Groq")
        st.markdown("**Local:** Ollama (Llama 3, Mistral, Gemma 2, Phi-3…)")

    with col2:
        st.markdown("### ✨ Features")
        features = [
            ("💬", "Multilingual Chat", "Ask anything about travel in India"),
            ("🗓️", "Trip Planner", "AI-generated day-by-day itineraries"),
            ("🚦", "Smart Route Finder", "Best transport options by budget"),
            ("📅", "Season Recommender", "Picks matched to month & budget"),
            ("🌤️", "Live Weather", "Real-time weather via Open-Meteo"),
            ("💰", "Budget Tracker", "Log expenses + AI financial advice"),
            ("🎫", "Booking Hub", "Quick links to IRCTC, OYO, flights & more"),
        ]
        for emoji, name, desc in features:
            st.markdown(f"{emoji} **{name}** — {desc}")

        st.markdown("### 📦 Tech Stack")
        st.markdown(
            "| Layer | Technology |\n|---|---|\n"
            "| UI | Streamlit |\n"
            "| i18n/l10n | Custom `translations.py` |\n"
            "| Cloud AI | Anthropic, OpenAI, Gemini, Groq |\n"
            "| Local AI | Ollama |\n"
            "| Weather | Open-Meteo + Nominatim (free) |"
        )

    st.markdown("---")
    st.markdown("Made with ❤️ for India · [i18n & l10n explained](https://blog.mozilla.org/l10n/2011/12/14/i18n-vs-l10n-whats-the-diff/)")
