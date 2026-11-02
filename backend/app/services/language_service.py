"""Multilingual language detection and script handling service."""
import re
from typing import Dict, Any, List

LANGUAGE_METADATA = {
    "en": {"name": "English", "native": "English", "script": "Latin", "direction": "ltr"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "script": "Devanagari", "direction": "ltr"},
    "mr": {"name": "Marathi", "native": "मराठी", "script": "Devanagari", "direction": "ltr"},
    "bn": {"name": "Bengali", "native": "বাংলা", "script": "Bengali", "direction": "ltr"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "script": "Tamil", "direction": "ltr"},
    "te": {"name": "Telugu", "native": "తెలుగు", "script": "Telugu", "direction": "ltr"},
    "es": {"name": "Spanish", "native": "Español", "script": "Latin", "direction": "ltr"},
    "fr": {"name": "French", "native": "Français", "script": "Latin", "direction": "ltr"},
    "de": {"name": "German", "native": "Deutsch", "script": "Latin", "direction": "ltr"},
    "ar": {"name": "Arabic", "native": "العربية", "script": "Arabic", "direction": "rtl"},
}

# Unicode Script Ranges
UNICODE_RANGES = {
    "ar": (0x0600, 0x06FF),  # Arabic
    "bn": (0x0980, 0x09FF),  # Bengali
    "ta": (0x0B80, 0x0BFF),  # Tamil
    "te": (0x0C00, 0x0C7F),  # Telugu
    "devanagari": (0x0900, 0x097F),  # Devanagari (Hindi / Marathi)
}

# Distinguishing markers for Marathi vs Hindi in Devanagari
MARATHI_MARKERS = {"आहे", "नाही", "आहेत", "काय", "कसे", "करा", "होते", "झाले", "करावे", "माहिती", "बद्दल", "सांगा"}
HINDI_MARKERS = {"है", "हैं", "नहीं", "क्या", "कैसे", "करें", "था", "थी", "हुआ", "जानकारी", "बारे", "बताओ"}

# Distinguishing common words for Latin-based languages
SPANISH_WORDS = {"el", "la", "los", "las", "un", "una", "de", "que", "en", "por", "para", "como", "esta", "este"}
FRENCH_WORDS = {"le", "la", "les", "un", "une", "des", "du", "de", "que", "qui", "dans", "pour", "avec", "est"}
GERMAN_WORDS = {"der", "die", "das", "ein", "eine", "und", "in", "den", "von", "zu", "mit", "sich", "auf", "für", "ist"}


class LanguageService:
    @staticmethod
    def detect_language(text: str) -> str:
        """Detects the ISO 639-1 language code from input text."""
        if not text or not text.strip():
            return "en"

        text_clean = text.strip()

        # 1. Check Unicode character counts for non-Latin scripts
        script_counts = {"ar": 0, "bn": 0, "ta": 0, "te": 0, "devanagari": 0}
        total_letters = 0

        for char in text_clean:
            code = ord(char)
            if char.isalpha():
                total_letters += 1
            for script, (start, end) in UNICODE_RANGES.items():
                if start <= code <= end:
                    script_counts[script] += 1

        # Check prominent non-Latin scripts
        for script, count in script_counts.items():
            if count >= 2:
                if script == "devanagari":
                    # Distinguish Hindi vs Marathi
                    words = set(re.findall(r"\w+", text_clean))
                    marathi_hits = len(words.intersection(MARATHI_MARKERS))
                    hindi_hits = len(words.intersection(HINDI_MARKERS))
                    return "mr" if marathi_hits > hindi_hits else "hi"
                return script

        # 2. Latin-script language heuristics using token matches
        tokens = set(re.findall(r"\b\w+\b", text_clean.lower()))
        es_matches = len(tokens.intersection(SPANISH_WORDS))
        fr_matches = len(tokens.intersection(FRENCH_WORDS))
        de_matches = len(tokens.intersection(GERMAN_WORDS))

        max_matches = max(es_matches, fr_matches, de_matches)
        if max_matches >= 2:
            if max_matches == de_matches:
                return "de"
            if max_matches == fr_matches:
                return "fr"
            if max_matches == es_matches:
                return "es"

        # Default fallback
        return "en"

    @staticmethod
    def get_language_info(lang_code: str) -> Dict[str, Any]:
        return LANGUAGE_METADATA.get(lang_code, LANGUAGE_METADATA["en"])

    @staticmethod
    def get_supported_languages() -> List[Dict[str, Any]]:
        return [{"code": code, **meta} for code, meta in LANGUAGE_METADATA.items()]


language_service = LanguageService()
