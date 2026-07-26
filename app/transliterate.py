"""
Sanskrit Abhidhana - Sanskritic Transliteration Engine
Strictly utilizes the `indic_transliteration` library (indic_transliteration.sanscript)
for multi-script conversions across Devanagari, IAST, SLP1, Harvard-Kyoto (HK), ITRANS,
Velthuis, Telugu, Bengali, Kannada, Malayalam, Tamil, Gujarati, Gurmukhi, Oriya, Grantha.
"""

import sys
import os
import site
import re
from typing import Tuple, Optional

# Ensure user site-packages (~/.local/lib/python3.x/site-packages) is included in sys.path
user_site = site.getusersitepackages()
if user_site and os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

# pyrefly: ignore [missing-import]
from indic_transliteration import sanscript
# pyrefly: ignore [missing-import]
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate


def get_scheme_constant(scheme_name: str) -> Optional[str]:
    """Map string scheme identifier to indic_transliteration.sanscript scheme string constant."""
    if not scheme_name:
        return None

    scheme_clean = scheme_name.lower().replace('-', '_').strip()
    mapping = {
        'devanagari': sanscript.DEVANAGARI,
        'iast': sanscript.IAST,
        'slp1': sanscript.SLP1,
        'hk': sanscript.HK,
        'harvard_kyoto': sanscript.HK,
        'itrans': sanscript.ITRANS,
        'velthuis': sanscript.VELTHUIS,
        'telugu': sanscript.TELUGU,
        'bengali': sanscript.BENGALI,
        'kannada': sanscript.KANNADA,
        'malayalam': sanscript.MALAYALAM,
        'tamil': sanscript.TAMIL,
        'gujarati': sanscript.GUJARATI,
        'gurmukhi': sanscript.GURMUKHI,
        'oriya': sanscript.ORIYA,
        'grantha': getattr(sanscript, 'GRANTHA', 'grantha')
    }
    return mapping.get(scheme_clean, None)


def detect_script(text: str) -> str:
    """
    Automatically detect the script of input text.
    Returns scheme identifier string usable with indic_transliteration.sanscript.
    """
    if not text:
        return 'slp1'
    if re.search(r'[\u0900-\u097F]', text):
        return 'devanagari'
    if re.search(r'[\u0C00-\u0C7F]', text):
        return 'telugu'
    if re.search(r'[\u0980-\u09FF]', text):
        return 'bengali'
    if re.search(r'[\u0C80-\u0CFF]', text):
        return 'kannada'
    if re.search(r'[\u0D00-\u0D7F]', text):
        return 'malayalam'
    if re.search(r'[\u0B80-\u0BFF]', text):
        return 'tamil'
    if re.search(r'[āīūṛṝḷḹṃḥṅñṭḍṇśṣ]', text):
        return 'iast'
    if re.search(r'R\^i|RR\^i|l\^i|\.m|\.h|Sh', text):
        return 'itrans'
    if re.search(r'[wWqQRSzMHFxX]', text):
        return 'slp1'
    return 'ascii'


def normalize_ascii(text: str) -> str:
    """Normalize input text to clean lowercase ASCII string for loose matching."""
    text = text.lower().strip()
    replacements = {
        'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'ri', 'ṝ': 'ri', 'ḷ': 'l', 'ḹ': 'l',
        'ṃ': 'm', 'ḥ': 'h', 'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n',
        'ś': 'sh', 'ṣ': 'sh', 's': 's'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def convert_script(text: str, _from: str, _to: str) -> str:
    """
    Transliterate text from source scheme to target scheme using indic_transliteration.sanscript.
    Supports Devanagari, IAST, SLP1, HK, ITRANS, Velthuis, Telugu, Bengali, Kannada, Malayalam, Tamil, etc.
    """
    if not text or _from == _to:
        return text

    src_scheme = get_scheme_constant(_from) or sanscript.SLP1
    tgt_scheme = get_scheme_constant(_to) or sanscript.SLP1

    try:
        return transliterate(text, src_scheme, tgt_scheme)
    except Exception:
        if src_scheme in SCHEMES and tgt_scheme in SCHEMES:
            scheme_map = SchemeMap(SCHEMES[src_scheme], SCHEMES[tgt_scheme])
            return transliterate(text, scheme_map=scheme_map)
        return text


def to_slp1_key(query: str, script: str = None) -> Tuple[str, str]:
    """
    Convert query word to database SLP1 key using indic_transliteration.
    Returns (slp1_key, detected_script).
    """
    query = query.strip()
    if not script or script == 'auto':
        script = detect_script(query)

    if script == 'ascii':
        return normalize_ascii(query), 'ascii'

    slp1_key = convert_script(query, script, 'slp1')
    return slp1_key, script


def slp1_to_iast(slp: str) -> str:
    """Convert SLP1 string to IAST string using indic_transliteration."""
    return transliterate(slp, sanscript.SLP1, sanscript.IAST)


def slp1_to_devanagari(slp: str) -> str:
    """Convert SLP1 string to Devanagari string using indic_transliteration."""
    return transliterate(slp, sanscript.SLP1, sanscript.DEVANAGARI)


def slp1_to_ascii(slp: str) -> str:
    """Convert SLP1 string to loose English ASCII string."""
    iast = slp1_to_iast(slp)
    return normalize_ascii(iast)
