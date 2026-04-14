import json

# The strings we want to encode safely
hi_profile = """निश्चित रूप से! कृपया अपनी पात्रता जांचने के लिए विवरण साझा करें:

  • आयु (Age)
  • वार्षिक आय (जैसे 1.5 लाख, 50,000)
  • व्यवसाय (जैसे छात्र, किसान, स्व-नियोजित)
  • राज्य (जैसे गुजरात)
  • लिंग (पुरुष / महिला)
  • जाता/श्रेणी (SC / ST / OBC / General / EWS / SEBC / NT / DNT / Minority)

उपहार:
  आयु: 22, आय: 1.5 लाख, व्यवसाय: छात्र, राज्य: गुजरात, जाति: OBC, लिंग: पुरुष"""

hi_no_schemes = "कोई मिलान वाली योजना ढूंढने में विफल। आयु, आय, व्यवसाय, राज्य और जाति जैसी अधिक जानकारी प्रदान करने का प्रयास करें।"
hi_no_add = "आपकी प्रोफाइल के लिए कोई अतिरिक्त मिलान वाली योजना नहीं मिली।"
hi_ask_first = "कृपया पहले कुछ योजनाओं के बारे में पूछें, फिर मैं उनके लिए आपकी पात्रता की जांच कर सकता हूँ।"

gu_profile = """ચોક્કસ! કૃપા કરીને તમારી પાત્રતા તપાસવા માટે વિગતો શેર કરો:

  • ઉંમર (Age)
  • વાર્ષિક આવક (દા.ત. 1.5 લાખ, 50,000)
  • વ્યવસાય (દા.ત. વિદ્યાર્થી, ખેડૂત, સ્વ-રોજગાર)
  • રાજ્ય (દા.ત. ગુજરાત)
  • લલિંગ (પુરુષ / મહિલા)
  • જ્ઞાતિ/શ્રેણી (SC / ST / OBC / General / EWS / SEBC / NT / DNT / Minority)

ઉદાહરણ:
  ઉંમર: 22, આવક: 1.5 લાખ, વ્યવસાય: વિદ્યાર્થી, રાજ્ય: ગુજરાત, જ્ઞાતિ: OBC, લિંગ: પુરુષ"""

gu_no_schemes = "કોઈ મેળ ખાતી યોજનાઓ મળી નથી। ઉંમર, આવક, વ્યવસાય, રાજ્ય અને જ્ઞાતિ જેવી વિગતો આપવાનો પ્રયત્ન કરો।"
gu_no_add = "તમારી પ્રોફાઇલ માટે કોઈ વધારાની યોજના મળી નથી।"
gu_ask_first = "કૃપા કરીને પહેલા કેટલીક યોજનાઓ વિશે પૂછો, પછી હું તે માટે તમારી પાત્રતા તપાસી શકું છું।"

def to_unicode(text):
    return "".join(f"\\u{ord(c):04x}" if ord(c) > 127 else c for c in text)

content = f'''import re
import json
from rag.llm import get_llm, TranslatedScheme

# -------------------------------------------------
# Language Support
# -------------------------------------------------

SUPPORTED_LANGUAGES = {{"english": "en", "hindi": "hi", "gujarati": "gu"}}

LANG_STRINGS = {{
    "en": {{
        "profile_request": """Sure! Please share your details so I can check eligibility:\\n\\n  \u2022 Age\\n  \u2022 Annual Income  (e.g. 1.5 lakh, 50,000)\\n  \u2022 Occupation     (e.g. student, farmer, self-employed)\\n  \u2022 State          (e.g. Gujarat)\\n  \u2022 Gender         (Male / Female)\\n  \u2022 Caste/Category (SC / ST / OBC / General / EWS / SEBC / NT / DNT / Minority)\\n\\nExample:\\n  age: 22, income: 1.5 lakh, occupation: student, state: Gujarat, caste: OBC, Gender: Male""",
        "no_schemes_found": "No matching schemes found. Try providing more details like age, income, occupation, state, and caste/category.",
        "no_additional_schemes": "No additional matching schemes found for your profile.",
        "ask_schemes_first": "Please first ask for some schemes, then I can check your eligibility for them.",
    }},
    "hi": {{
        "profile_request": """{to_unicode(hi_profile)}""",
        "no_schemes_found": "{to_unicode(hi_no_schemes)}",
        "no_additional_schemes": "{to_unicode(hi_no_add)}",
        "ask_schemes_first": "{to_unicode(hi_ask_first)}",
    }},
    "gu": {{
        "profile_request": """{to_unicode(gu_profile)}""",
        "no_schemes_found": "{to_unicode(gu_no_schemes)}",
        "no_additional_schemes": "{to_unicode(gu_no_add)}",
        "ask_schemes_first": "{to_unicode(gu_ask_first)}",
    }},
}}

def detect_language(text: str) -> str:
    """Detect language: gu, hi, or en using Unicode ranges then romanized hints."""
    if re.search(r"[\\u0A80-\\u0AFF]", text):
        return "gu"
    if re.search(r"[\\u0900-\\u097F]", text):
        return "hi"
    lower = text.lower()
    gu_hints = ["kem cho", "tamne", "mane", "yojana", "aavak", "ummar", "vyvsa", "khedu", "rajya", "patrata"]
    hi_hints = ["mujhe", "kaunsi", "kya hai", "kaun si", "kaise", "bataiye", "sarkari", "patrata", "labh"]
    if any(w in lower for w in gu_hints):
        return "gu"
    if any(w in lower for w in hi_hints):
        return "hi"
    return "en"

def translate_to_english(text: str, source_lang: str) -> str:
    """Translate user input to English for internal processing."""
    if source_lang == "en":
        return text

    clean = text.strip()
    buttons = {{
        "{to_unicode("ખેડૂતો માટે યોજનાઓ 🌾")}": "Schemes for farmers",
        "{to_unicode("મહિલા કલ્યાણ યોજનાઓ")}": "Women welfare schemes",
        "{to_unicode("શિક્ષણ શિષ્યવૃત્તિ")}": "Education scholarships",
        "{to_unicode("આરોગ્ય યોજનાઓ")}": "Healthcare schemes",
        "{to_unicode("આવાસ યોજના")}": "housing scheme",
        "{to_unicode("યુવાનો માટે સ્ટાર્ટઅપ યોજનાઓ")}": "Startup schemes for youth",
        "{to_unicode("ગુજરાતમાં યોજનાઓ")}": "Schemes in Gujarat",
        "{to_unicode("કૌશલ્ય વિકાસ કાર્યક્રમ")}": "Skill development programs",
        
        "{to_unicode("किसानों के लिए योजनाएं 🌾")}": "Schemes for farmers",
        "{to_unicode("महिला कल्याण योजनाएं")}": "Women welfare schemes",
        "{to_unicode("शिक्षा छात्रवृत्ति")}": "Education scholarships",
        "{to_unicode("स्वास्थ्य योजनाएं")}": "Healthcare schemes",
        "{to_unicode("आवास योजना")}": "housing scheme",
        "{to_unicode("युवाओं के लिए स्टार्टअप योजनाएं")}": "Startup schemes for youth",
        "{to_unicode("गुजरात में योजनाएं")}": "Schemes in Gujarat",
        "{to_unicode("कौशल विकास कार्यक्रम")}": "Skill development programs"
    }}
    if clean in buttons:
        return buttons[clean]

    if not text or not text.strip():
        return text

    lang_name = {{"hi": "Hindi", "gu": "Gujarati"}}[source_lang]
    prompt = (
        f"Translate this {{lang_name}} query to English for a government scheme search engine.\\n"
        f"Critical for Search Accuracy: For local terms (especially agricultural crops like 'Bajri', 'Kapas', or 'Jowar', products, or occupations like 'Khedut'), "
        f"provide BOTH the common transliterated name and the standard English translation. "
        f"Keep unchanged: scheme names, acronyms like SC/ST/OBC/EWS/SEBC, state names, numbers, rupee amounts.\\n"
        f"Return ONLY the English translation.\\n\\n"
        f"{{lang_name}}: {{text}}\\n"
        f"English:"
    )
    r = get_llm().invoke(prompt)
    translated = r.content.strip()
    return translated if translated else text

def translate_response(text: str, target_lang: str) -> str:
    """Translate agent response from English to target language."""
    if target_lang == "en":
        return text
    if not text or not text.strip():
        return text

    lang_name = {{"hi": "Hindi ({to_unicode("\u0939\u093f\u0902\u0926\u0940")}, Devanagari script)", "gu": "Gujarati ({to_unicode("\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0")}, Gujarati script)"}}[target_lang]
    script_warn = {{
        "hi": "IMPORTANT: Use ONLY Hindi language with Devanagari script ({to_unicode("\u0939\u093f\u0902\u0926\u0940")}). Do NOT use Gujarati script.",
        "gu": "IMPORTANT: Use ONLY Gujarati language with Gujarati script ({to_unicode("\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0")}). Do NOT use Hindi/Devanagari script.",
    }}[target_lang]
    r = get_llm().invoke(
        f"Translate this English text to {{lang_name}}.\\n"
        f"{{script_warn}}\\n"
        f"Keep unchanged: scheme names, official links, SC/ST/OBC/EWS/SEBC, state names, amounts, numbers.\\n"
        f"Return ONLY the translation.\\n\\nEnglish: {{text}}\\n\\nTranslation:"
    )
    translated = r.content.strip()
    return translated if translated else text

def get_string(key: str, lang: str) -> str:
    """Get a static UI string in the given language."""
    return LANG_STRINGS.get(lang, LANG_STRINGS["en"]).get(key, LANG_STRINGS["en"].get(key, ""))

def translate_scheme_dict(d: dict, target_lang: str) -> dict:
    if target_lang == "en":
        return d
    lang_name = {{"hi": "Hindi", "gu": "Gujarati"}}.get(target_lang, "English")
    keys_to_translate = [k for k in ("scheme_name", "description", "benefits", 
                                     "eligibility", "documents_required", 
                                     "application_process", "category") 
                         if k in d and d[k]]
    if not keys_to_translate:
        return d

    to_translate = {{k: d[k] for k in keys_to_translate}}
    json_in = json.dumps(to_translate, ensure_ascii=False)
    
    script_warn = {{
        "hi": "IMPORTANT: Use ONLY Hindi language with Devanagari script ({to_unicode("\u0939\u093f\u0902\u0926\u0940")}). Do NOT output Gujarati.",
        "gu": "IMPORTANT: Use ONLY Gujarati language with Gujarati script ({to_unicode("\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0")}). Do NOT output Hindi.",
    }}.get(target_lang, "")
    prompt = f"""Translate text values to {{lang_name}} while keeping numbers, Rs amounts, links, and SC/ST/OBC acronyms exactly the same.
CRITICAL: Preserve all original line breaks and structural patterns like numbered lists (1. 2. 3.) or bullet points ({to_unicode("\u2022")}).
CLEAN UI RULE: Remove redundant link-directing filler phrases such as "click here", "click", "here", "visit link", or native versions from the output.
{{script_warn}}
Return ONLY valid JSON that matches the required schema.

Input JSON to translate:
{{json_in}}
"""
    try:
        translated = get_llm().with_structured_output(TranslatedScheme).invoke(prompt)
        res = d.copy()
        res.update({{k: v for k, v in translated.model_dump().items() if v}})
        return res
    except Exception as e:
        print(f"[translate_scheme_dict] Translation failed: {{e}}")
        return d
'''

with open("rag/translation.py", "w", encoding="utf-8") as f:
    f.write(content)
