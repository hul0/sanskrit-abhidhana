"""
Sanskrit Abhidhana - Monier-Williams Entry Parser
Parses Monier-Williams dictionary XML entries into clean, human-readable structured Python dictionaries.
"""

import re
import sys
import os
import site
from typing import Dict, Any, Optional, List

# Ensure user site packages in sys.path
user_site = site.getusersitepackages()
if user_site and os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Ensure root directory in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.transliterate import slp1_to_iast, slp1_to_devanagari, slp1_to_ascii
from app.abbreviations import expand_grammatical_info, expand_definition_text, get_abbreviation_map


def parse_mw_entry(key_slp1: str, lnum: float, xml_data: str, include_raw_xml: bool = False) -> Dict[str, Any]:
    """
    Parse a raw Monier-Williams XML entry into a clean, human-readable structured dictionary.
    """
    # 1. Extract Homonym
    hom_match = re.search(r'<hom>([0-9]+)</hom>', xml_data)
    homonym = int(hom_match.group(1)) if hom_match else None

    # 2. Extract Grammatical Info (<lex>...</lex>)
    lex_match = re.search(r'<lex>(.*?)</lex>', xml_data)
    grammatical_code = None
    grammatical_info = None
    if lex_match:
        grammatical_code = re.sub(r'<[^>]+>', '', lex_match.group(1)).strip()
        grammatical_info = expand_grammatical_info(grammatical_code)

    # 3. Extract Page/Column (<pc>...</pc>)
    pc_match = re.search(r'<pc>([0-9,]+)</pc>', xml_data)
    page_column = pc_match.group(1) if pc_match else None

    # 4. Extract and Expand Body Definition
    body_match = re.search(r'<body>(.*?)</body>', xml_data, re.DOTALL)
    body_xml = body_match.group(1) if body_match else xml_data

    # Expand abbreviations and citations in body XML
    expanded_body_xml, detected_tooltips = expand_definition_text(body_xml)

    # Replace <s>...</s> tags with converted IAST / Devanagari Sanskrit words
    def replace_sanskrit(m):
        raw_slp = m.group(1).replace('/', '').strip()
        if not raw_slp:
            return ''
        return f" [{slp1_to_iast(raw_slp)} / {slp1_to_devanagari(raw_slp)}] "

    cleaned_body = re.sub(r'<s>(.*?)</s>', replace_sanskrit, expanded_body_xml)

    # Strip remaining XML tags
    cleaned_body = re.sub(r'<[^>]+>', ' ', cleaned_body)

    # Normalize whitespace & HTML entities
    cleaned_body = cleaned_body.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    cleaned_body = re.sub(r'\s+', ' ', cleaned_body).strip()

    # Generate headword in IAST, Devanagari, and ASCII
    clean_key = key_slp1.replace('/', '').strip()
    headword_iast = slp1_to_iast(clean_key)
    headword_devanagari = slp1_to_devanagari(clean_key)
    headword_ascii = slp1_to_ascii(clean_key)

    result = {
        "key_slp1": clean_key,
        "headword_iast": headword_iast,
        "headword_devanagari": headword_devanagari,
        "headword_ascii": headword_ascii,
        "homonym": homonym,
        "grammatical_code": grammatical_code,
        "grammatical_info": grammatical_info,
        "definition": cleaned_body,
        "abbreviations": detected_tooltips,
        "line_number": float(lnum),
        "page_column": page_column
    }

    if include_raw_xml:
        result["raw_xml"] = xml_data

    return result
