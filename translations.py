"""
i18n (Internationalization) + l10n (Localization) for Sanchari AI
i18n = structuring the app to support multiple languages (the skeleton)
l10n = actual translated content + locale-specific formats (the flesh)
"""

from datetime import datetime
import locale

# ── Supported locales ────────────────────────────────────────────────────────
LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "te": "తెలుగు (Telugu)",
    "ta": "தமிழ் (Tamil)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "mr": "मराठी (Marathi)",
}

# ── Translation strings ───────────────────────────────────────────────────────
TRANSLATIONS = {
    # ── App shell ──────────────────────────────────────────────────────────────
    "app_title": {
        "en": "🧭 Sanchari AI",
        "hi": "🧭 संचारी AI",
        "te": "🧭 సంచారి AI",
        "ta": "🧭 சஞ்சாரி AI",
        "kn": "🧭 ಸಂಚಾರಿ AI",
        "mr": "🧭 संचारी AI",
    },
    "app_subtitle": {
        "en": "Your Multilingual Travel Companion",
        "hi": "आपका बहुभाषी यात्रा साथी",
        "te": "మీ బహుభాషా ప్రయాణ సహాయకుడు",
        "ta": "உங்கள் பன்மொழி பயண உதவியாளர்",
        "kn": "ನಿಮ್ಮ ಬಹುಭಾಷಾ ಪ್ರಯಾಣ ಸಹಾಯಕ",
        "mr": "तुमचा बहुभाषिक प्रवास सहाय्यक",
    },
    # ── Sidebar ────────────────────────────────────────────────────────────────
    "settings": {
        "en": "⚙️ Settings",
        "hi": "⚙️ सेटिंग्स",
        "te": "⚙️ సెట్టింగులు",
        "ta": "⚙️ அமைப்புகள்",
        "kn": "⚙️ ಸೆಟ್ಟಿಂಗ್‌ಗಳು",
        "mr": "⚙️ सेटिंग्ज",
    },
    "language": {
        "en": "🌐 Language",
        "hi": "🌐 भाषा",
        "te": "🌐 భాష",
        "ta": "🌐 மொழி",
        "kn": "🌐 ಭಾಷೆ",
        "mr": "🌐 भाषा",
    },
    "ai_provider": {
        "en": "🤖 AI Provider",
        "hi": "🤖 AI प्रदाता",
        "te": "🤖 AI సేవాదాత",
        "ta": "🤖 AI வழங்குநர்",
        "kn": "🤖 AI ಪೂರೈಕೆದಾರ",
        "mr": "🤖 AI पुरवठादार",
    },
    "provider_cloud": {
        "en": "☁️ Cloud API (BYOK)",
        "hi": "☁️ क्लाउड API (BYOK)",
        "te": "☁️ క్లౌడ్ API (BYOK)",
        "ta": "☁️ Cloud API (BYOK)",
        "kn": "☁️ ಕ್ಲೌಡ್ API (BYOK)",
        "mr": "☁️ क्लाउड API (BYOK)",
    },
    "provider_local": {
        "en": "🏠 Local Inference (Ollama)",
        "hi": "🏠 स्थानीय अनुमान (Ollama)",
        "te": "🏠 స్థానిక అనుమానం (Ollama)",
        "ta": "🏠 உள்ளூர் அனுமானம் (Ollama)",
        "kn": "🏠 ಸ್ಥಳೀಯ ಅನುಮಾನ (Ollama)",
        "mr": "🏠 स्थानिक अनुमान (Ollama)",
    },
    "api_provider_label": {
        "en": "API Provider",
        "hi": "API प्रदाता",
        "te": "API సేవాదాత",
        "ta": "API வழங்குநர்",
        "kn": "API ಪೂರೈಕೆದಾರ",
        "mr": "API पुरवठादार",
    },
    "api_key_label": {
        "en": "🔑 Your API Key (BYOK)",
        "hi": "🔑 आपकी API कुंजी (BYOK)",
        "te": "🔑 మీ API కీ (BYOK)",
        "ta": "🔑 உங்கள் API திறவுகோல் (BYOK)",
        "kn": "🔑 ನಿಮ್ಮ API ಕೀ (BYOK)",
        "mr": "🔑 तुमची API की (BYOK)",
    },
    "api_key_placeholder": {
        "en": "Paste your API key here...",
        "hi": "यहाँ अपनी API कुंजी पेस्ट करें...",
        "te": "మీ API కీని ఇక్కడ పేస్ట్ చేయండి...",
        "ta": "உங்கள் API திறவுகோலை இங்கே ஒட்டவும்...",
        "kn": "ನಿಮ್ಮ API ಕೀ ಇಲ್ಲಿ ಅಂಟಿಸಿ...",
        "mr": "तुमची API की येथे पेस्ट करा...",
    },
    "model_label": {
        "en": "Model",
        "hi": "मॉडल",
        "te": "మోడల్",
        "ta": "மாதிரி",
        "kn": "ಮಾಡೆಲ್",
        "mr": "मॉडेल",
    },
    "ollama_url": {
        "en": "Ollama Base URL",
        "hi": "Ollama बेस URL",
        "te": "Ollama బేస్ URL",
        "ta": "Ollama அடிப்படை URL",
        "kn": "Ollama ಬೇಸ್ URL",
        "mr": "Ollama बेस URL",
    },
    # ── Chat ───────────────────────────────────────────────────────────────────
    "chat_placeholder": {
        "en": "Ask me anything about travel in India...",
        "hi": "भारत में यात्रा के बारे में कुछ भी पूछें...",
        "te": "భారతదేశంలో ప్రయాణం గురించి ఏదైనా అడగండి...",
        "ta": "இந்தியாவில் பயணம் பற்றி எதையும் கேளுங்கள்...",
        "kn": "ಭಾರತದಲ್ಲಿ ಪ್ರಯಾಣದ ಬಗ್ಗೆ ಏನಾದರೂ ಕೇಳಿ...",
        "mr": "भारतातील प्रवासाबद्दल काहीही विचारा...",
    },
    "send": {
        "en": "Send",
        "hi": "भेजें",
        "te": "పంపు",
        "ta": "அனுப்பு",
        "kn": "ಕಳುಹಿಸು",
        "mr": "पाठवा",
    },
    "clear_chat": {
        "en": "🗑️ Clear Chat",
        "hi": "🗑️ चैट साफ करें",
        "te": "🗑️ చాట్ తొలగించు",
        "ta": "🗑️ அரட்டையை அழி",
        "kn": "🗑️ ಚಾಟ್ ತೆರವುಗೊಳಿಸಿ",
        "mr": "🗑️ चॅट साफ करा",
    },
    "thinking": {
        "en": "✈️ Sanchari is thinking...",
        "hi": "✈️ संचारी सोच रही है...",
        "te": "✈️ సంచారి ఆలోచిస్తోంది...",
        "ta": "✈️ சஞ்சாரி யோசிக்கிறது...",
        "kn": "✈️ ಸಂಚಾರಿ ಯೋಚಿಸುತ್ತಿದೆ...",
        "mr": "✈️ संचारी विचार करत आहे...",
    },
    # ── Quick prompts ──────────────────────────────────────────────────────────
    "quick_prompts_title": {
        "en": "✨ Quick Prompts",
        "hi": "✨ त्वरित प्रश्न",
        "te": "✨ త్వరిత ప్రశ్నలు",
        "ta": "✨ விரைவு கேள்விகள்",
        "kn": "✨ ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳು",
        "mr": "✨ जलद प्रश्न",
    },
    "quick_prompts": {
        "en": [
            "🗺️ Plan a 5-day trip to Rajasthan",
            "🍛 Best street food in Mumbai",
            "🏔️ Trekking spots in Himachal Pradesh",
            "🛕 Temple tour of Tamil Nadu",
            "🌴 Beach destinations in Kerala",
            "🚂 Scenic train journeys in India",
        ],
        "hi": [
            "🗺️ राजस्थान में 5 दिन की यात्रा योजना",
            "🍛 मुंबई में सर्वोत्तम स्ट्रीट फूड",
            "🏔️ हिमाचल प्रदेश में ट्रेकिंग स्थल",
            "🛕 तमिलनाडु का मंदिर दौरा",
            "🌴 केरल में समुद्र तट",
            "🚂 भारत में सुंदर रेल यात्राएं",
        ],
        "te": [
            "🗺️ రాజస్థాన్‌లో 5 రోజుల పర్యటన",
            "🍛 ముంబైలో వీధి ఆహారం",
            "🏔️ హిమాచల్ ప్రదేశ్‌లో ట్రెక్కింగ్",
            "🛕 తమిళనాడు దేవాలయాల పర్యటన",
            "🌴 కేరళలో బీచ్‌లు",
            "🚂 భారతదేశంలో సుందర రైలు ప్రయాణాలు",
        ],
        "ta": [
            "🗺️ ராஜஸ்தானில் 5 நாள் பயணத் திட்டம்",
            "🍛 மும்பையில் சிறந்த தெரு உணவு",
            "🏔️ இமாச்சல் பிரதேசத்தில் டிரெக்கிங்",
            "🛕 தமிழ்நாடு கோயில் சுற்றுலா",
            "🌴 கேரளாவில் கடற்கரை இடங்கள்",
            "🚂 இந்தியாவில் அழகான ரயில் பயணங்கள்",
        ],
        "kn": [
            "🗺️ ರಾಜಸ್ಥಾನದಲ್ಲಿ 5 ದಿನಗಳ ಪ್ರವಾಸ",
            "🍛 ಮುಂಬೈನಲ್ಲಿ ಬೀದಿ ಆಹಾರ",
            "🏔️ ಹಿಮಾಚಲ ಪ್ರದೇಶದಲ್ಲಿ ಟ್ರೆಕ್ಕಿಂಗ್",
            "🛕 ತಮಿಳುನಾಡಿನ ದೇವಾಲಯ ಪ್ರವಾಸ",
            "🌴 ಕೇರಳದ ಕಡಲ ತೀರಗಳು",
            "🚂 ಭಾರತದ ಸುಂದರ ರೈಲು ಪ್ರಯಾಣಗಳು",
        ],
        "mr": [
            "🗺️ राजस्थानमध्ये 5 दिवसांचा प्रवास",
            "🍛 मुंबईतील सर्वोत्तम स्ट्रीट फूड",
            "🏔️ हिमाचल प्रदेशातील ट्रेकिंग",
            "🛕 तमिळनाडूचा मंदिर दौरा",
            "🌴 केरळमधील समुद्रकिनारे",
            "🚂 भारतातील सुंदर रेल्वे प्रवास",
        ],
    },
    # ── Status / errors ────────────────────────────────────────────────────────
    "no_api_key": {
        "en": "⚠️ Please enter your API key in the sidebar.",
        "hi": "⚠️ कृपया साइडबार में अपनी API कुंजी दर्ज करें।",
        "te": "⚠️ దయచేసి సైడ్‌బార్‌లో మీ API కీని నమోదు చేయండి.",
        "ta": "⚠️ தயவுசெய்து பக்கப்பட்டியில் உங்கள் API திறவுகோலை உள்ளிடுங்கள்.",
        "kn": "⚠️ ದಯವಿಟ್ಟು ಸೈಡ್‌ಬಾರ್‌ನಲ್ಲಿ ನಿಮ್ಮ API ಕೀ ನಮೂದಿಸಿ.",
        "mr": "⚠️ कृपया साइडबारमध्ये तुमची API की प्रविष्ट करा.",
    },
    "error_prefix": {
        "en": "❌ Error",
        "hi": "❌ त्रुटि",
        "te": "❌ లోపం",
        "ta": "❌ பிழை",
        "kn": "❌ ದೋಷ",
        "mr": "❌ त्रुटी",
    },
    "ollama_tip": {
        "en": "💡 Make sure Ollama is running: `ollama serve`",
        "hi": "💡 सुनिश्चित करें Ollama चल रहा है: `ollama serve`",
        "te": "💡 Ollama నడుస్తోందని నిర్ధారించుకోండి: `ollama serve`",
        "ta": "💡 Ollama இயங்குகிறது என்பதை உறுதிசெய்யுங்கள்: `ollama serve`",
        "kn": "💡 Ollama ಚಾಲನೆಯಲ್ಲಿದೆ ಎಂದು ಖಚಿತಪಡಿಸಿ: `ollama serve`",
        "mr": "💡 Ollama चालू आहे याची खात्री करा: `ollama serve`",
    },
    # ── About tab ──────────────────────────────────────────────────────────────
    "about_title": {
        "en": "About Sanchari AI",
        "hi": "संचारी AI के बारे में",
        "te": "సంచారి AI గురించి",
        "ta": "சஞ்சாரி AI பற்றி",
        "kn": "ಸಂಚಾರಿ AI ಬಗ್ಗೆ",
        "mr": "संचारी AI बद्दल",
    },
    "about_desc": {
        "en": (
            "**Sanchari AI** (संचारी = *traveller* in Sanskrit) is an open-source, "
            "privacy-first travel assistant built for India. It supports 6 Indian languages "
            "and works both online (BYOK) and fully offline via Ollama."
        ),
        "hi": (
            "**संचारी AI** (संस्कृत में *यात्री*) भारत के लिए बना एक ओपन-सोर्स, "
            "गोपनीयता-प्रथम यात्रा सहायक है। यह 6 भारतीय भाषाओं को सपोर्ट करता है "
            "और ऑनलाइन (BYOK) व Ollama के जरिए ऑफ़लाइन दोनों काम करता है।"
        ),
        "te": (
            "**సంచారి AI** (సంస్కృతంలో *యాత్రికుడు*) భారతదేశం కోసం నిర్మించిన "
            "ఓపెన్-సోర్స్ ప్రైవసీ-ఫస్ట్ ట్రావెల్ అసిస్టెంట్. ఇది 6 భారతీయ భాషలను "
            "మద్దతు ఇస్తుంది మరియు BYOK ద్వారా ఆన్‌లైన్‌లో మరియు Ollama ద్వారా ఆఫ్‌లైన్‌లో పని చేస్తుంది."
        ),
        "ta": (
            "**சஞ்சாரி AI** (சம்ஸ்கிருதத்தில் *பயணர்*) இந்தியாவுக்காக கட்டப்பட்ட "
            "திறந்த மூல தனியுரிமை-முதல் பயண உதவியாளர். இது 6 இந்திய மொழிகளை ஆதரிக்கிறது "
            "மற்றும் BYOK மூலம் ஆன்லைனிலும் Ollama மூலம் ஆஃப்லைனிலும் செயல்படுகிறது."
        ),
        "kn": (
            "**ಸಂಚಾರಿ AI** (ಸಂಸ್ಕೃತದಲ್ಲಿ *ಪ್ರಯಾಣಿಕ*) ಭಾರತಕ್ಕಾಗಿ ನಿರ್ಮಿಸಲಾದ "
            "ಓಪನ್-ಸೋರ್ಸ್ ಗೋಪನೀಯತೆ-ಮೊದಲ ಪ್ರಯಾಣ ಸಹಾಯಕ. ಇದು 6 ಭಾರತೀಯ ಭಾಷೆಗಳನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ "
            "ಮತ್ತು BYOK ಮೂಲಕ ಆನ್‌ಲೈನ್‌ನಲ್ಲಿ ಮತ್ತು Ollama ಮೂಲಕ ಆಫ್‌ಲೈನ್‌ನಲ್ಲಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ."
        ),
        "mr": (
            "**संचारी AI** (संस्कृतमध्ये *प्रवासी*) भारतासाठी बनवलेला ओपन-सोर्स, "
            "गोपनीयता-प्रथम प्रवास सहाय्यक आहे. हे 6 भारतीय भाषांना समर्थन देते "
            "आणि BYOK द्वारे ऑनलाइन आणि Ollama द्वारे ऑफलाइन दोन्ही कार्य करते."
        ),
    },
    "tab_chat": {
        "en": "💬 Chat",
        "hi": "💬 चैट",
        "te": "💬 చాట్",
        "ta": "💬 அரட்டை",
        "kn": "💬 ಚಾಟ್",
        "mr": "💬 चॅट",
    },
    "tab_planner": {
        "en": "🗓️ Trip Planner",
        "hi": "🗓️ यात्रा योजनाकार",
        "te": "🗓️ ట్రిప్ ప్లానర్",
        "ta": "🗓️ பயண திட்டமிடுபவர்",
        "kn": "🗓️ ಪ್ರವಾಸ ಯೋಜಕ",
        "mr": "🗓️ ट्रिप प्लॅनर",
    },
    "tab_about": {
        "en": "ℹ️ About",
        "hi": "ℹ️ के बारे में",
        "te": "ℹ️ గురించి",
        "ta": "ℹ️ பற்றி",
        "kn": "ℹ️ ಬಗ್ಗೆ",
        "mr": "ℹ️ बद्दल",
    },
    # ── Trip Planner ───────────────────────────────────────────────────────────
    "planner_destination": {
        "en": "Destination",
        "hi": "गंतव्य",
        "te": "గమ్యం",
        "ta": "இலக்கிடம்",
        "kn": "ಗಮ್ಯಸ್ಥಾನ",
        "mr": "गंतव्य",
    },
    "planner_days": {
        "en": "Number of Days",
        "hi": "दिनों की संख्या",
        "te": "రోజుల సంఖ్య",
        "ta": "நாட்களின் எண்ணிக்கை",
        "kn": "ದಿನಗಳ ಸಂಖ್ಯೆ",
        "mr": "दिवसांची संख्या",
    },
    "planner_budget": {
        "en": "Budget (₹)",
        "hi": "बजट (₹)",
        "te": "బడ్జెట్ (₹)",
        "ta": "பட்ஜெட் (₹)",
        "kn": "ಬಜೆಟ್ (₹)",
        "mr": "बजेट (₹)",
    },
    "planner_interests": {
        "en": "Interests",
        "hi": "रुचियां",
        "te": "ఆసక్తులు",
        "ta": "ஆர்வங்கள்",
        "kn": "ಆಸಕ್ತಿಗಳು",
        "mr": "आवडी",
    },
    "planner_generate": {
        "en": "🗺️ Generate Itinerary",
        "hi": "🗺️ यात्रा कार्यक्रम बनाएं",
        "te": "🗺️ యాత్రా కార్యక్రమం రూపొందించు",
        "ta": "🗺️ பயண அட்டவணை உருவாக்கு",
        "kn": "🗺️ ಯಾತ್ರಾ ವೇಳಾಪಟ್ಟಿ ರಚಿಸಿ",
        "mr": "🗺️ प्रवास कार्यक्रम तयार करा",
    },
    "planner_dest_placeholder": {
        "en": "e.g., Goa, Varanasi, Coorg...",
        "hi": "जैसे, गोवा, वाराणसी, कूर्ग...",
        "te": "ఉదా., గోవా, వారణాసి, కూర్గ్...",
        "ta": "எ.கா., கோவா, வாரணாசி, குர்க்...",
        "kn": "ಉದಾ., ಗೋವಾ, ವಾರಣಾಸಿ, ಕೂರ್ಗ್...",
        "mr": "उदा., गोवा, वाराणसी, कूर्ग...",
    },
}


def t(key: str, lang: str) -> str:
    """Translate a key to the given language, falling back to English."""
    return TRANSLATIONS.get(key, {}).get(lang) or TRANSLATIONS.get(key, {}).get("en", key)


# ── l10n helpers ──────────────────────────────────────────────────────────────

CURRENCY_LOCALE = {
    "en": "en_IN",
    "hi": "hi_IN",
    "te": "te_IN",
    "ta": "ta_IN",
    "kn": "kn_IN",
    "mr": "mr_IN",
}

DATE_FORMAT = {
    "en": "%d %B %Y",
    "hi": "%d %B %Y",
    "te": "%d %B %Y",
    "ta": "%d %B %Y",
    "kn": "%d %B %Y",
    "mr": "%d %B %Y",
}


def format_currency(amount: float, lang: str = "en") -> str:
    """l10n: Format a rupee amount according to locale conventions."""
    # Indian number system: lakhs and crores
    if amount >= 10_000_000:
        return f"₹{amount/10_000_000:.2f} करोड़" if lang == "hi" else f"₹{amount/10_000_000:.2f} Cr"
    if amount >= 100_000:
        return f"₹{amount/100_000:.2f} लाख" if lang == "hi" else f"₹{amount/100_000:.2f} L"
    if amount >= 1_000:
        return f"₹{amount:,.0f}"
    return f"₹{int(amount)}"


def format_date(dt: datetime, lang: str = "en") -> str:
    """l10n: Format a date according to locale conventions."""
    fmt = DATE_FORMAT.get(lang, "%d %B %Y")
    return dt.strftime(fmt)
