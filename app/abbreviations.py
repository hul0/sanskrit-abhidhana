"""
Sanskrit Abhidhana - Abbreviation & Citation Expander
Loads Monier-Williams linguistic abbreviations (mwab.sqlite) and literary title/author citations (mwauthtooltips.sqlite)
to convert cryptic dictionary codes (e.g. f., m., mfn., N., L., Comm., RV., MBh., q.v.) into clear human-readable expansions.
"""

import sqlite3
import os
import re
import contextlib
from typing import Dict, List, Any, Optional, Tuple

MWAB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mw', 'mwab.sqlite')
TOOLTIPS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'mw', 'mwauthtooltips.sqlite')

# Global cache dictionary
_ABBREVIATION_CACHE: Dict[str, str] = {}


def init_abbreviations() -> Dict[str, str]:
    """Load all abbreviations and literary title tooltips into memory."""
    global _ABBREVIATION_CACHE
    if _ABBREVIATION_CACHE:
        return _ABBREVIATION_CACHE

    ab_map = {
        'f.': 'feminine',
        'm.': 'masculine gender',
        'n.': 'neuter gender',
        'mfn.': 'adjective (masculine, feminine, or neuter)',
        'mf.': 'masculine or feminine',
        'mn.': 'masculine or neuter',
        'ind.': 'indeclinable',
        'vt.': 'transitive verb',
        'vi.': 'intransitive verb',
        'N.': 'Name',
        'L.': 'Lexicographers (ancient native Sanskrit dictionaries)',
        'Comm.': 'commentator or commentary',
        'q.v.': 'which see (quod vide)',
        'cf.': 'compare (confer)',
        'Nom.': 'Nominative case',
        'Acc.': 'Accusative case',
        'Instr.': 'Instrumental case',
        'Dat.': 'Dative case',
        'Abl.': 'Ablative case',
        'Gen.': 'Genitive case',
        'Loc.': 'Locative case',
        'Voc.': 'Vocative case',
        'P.': 'Parasmaipada (active verb form)',
        'A.': 'Ātmanepada (middle verb form)'
    }

    # 1. Load from mwab.sqlite
    if os.path.exists(MWAB_PATH):
        try:
            conn = sqlite3.connect(MWAB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, data FROM mwab;")
            for row in c.fetchall():
                abb_id = row[0].strip()
                disp_match = re.search(r'<disp>(.*?)</disp>', row[1])
                if disp_match:
                    clean_txt = re.sub(r'<[^>]+>', '', disp_match.group(1)).strip()
                    if abb_id not in ab_map:
                        ab_map[abb_id] = clean_txt
            conn.close()
        except Exception:
            pass

    # 2. Load from mwauthtooltips.sqlite
    if os.path.exists(TOOLTIPS_PATH):
        try:
            conn = sqlite3.connect(TOOLTIPS_PATH)
            c = conn.cursor()
            c.execute("SELECT key, data FROM mwauthtooltips;")
            for row in c.fetchall():
                key = row[0].strip()
                clean_txt = re.sub(r'<[^>]+>', '', row[1]).strip()
                if key not in ab_map:
                    ab_map[key] = clean_txt
            conn.close()
        except Exception:
            pass

    _ABBREVIATION_CACHE = ab_map
    return ab_map


def get_abbreviation_map() -> Dict[str, str]:
    """Get loaded abbreviation dictionary."""
    if not _ABBREVIATION_CACHE:
        return init_abbreviations()
    return _ABBREVIATION_CACHE


def expand_grammatical_info(gram_code: Optional[str]) -> str:
    """Expand cryptic grammatical tag into clear human-readable string."""
    if not gram_code:
        return ""

    ab_map = get_abbreviation_map()
    clean_code = gram_code.strip()

    if clean_code in ab_map:
        return ab_map[clean_code]

    # Check for sub-parts like mf(A/)n.
    tokens = re.split(r'[\s(),/]+', clean_code)
    expanded_parts = []
    for tok in tokens:
        if not tok:
            continue
        tok_dot = tok if tok.endswith('.') else tok + '.'
        if tok_dot in ab_map:
            expanded_parts.append(ab_map[tok_dot])
        elif tok in ab_map:
            expanded_parts.append(ab_map[tok])
        else:
            expanded_parts.append(tok)

    return " ".join(expanded_parts) if expanded_parts else clean_code


def expand_definition_text(body_xml: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Expand abbreviations and literature citations inside Monier-Williams definition XML text.
    Returns (human_readable_definition, list_of_detected_abbreviation_tooltips).
    """
    ab_map = get_abbreviation_map()
    detected_tooltips: List[Dict[str, str]] = []
    seen_codes = set()

    def add_tooltip(code: str, exp: str):
        if code not in seen_codes and exp:
            seen_codes.add(code)
            detected_tooltips.append({"code": code, "expansion": exp})

    # 1. Expand <lex> tags (part of speech)
    def lex_replacer(m):
        code = m.group(1).strip()
        exp = expand_grammatical_info(code)
        add_tooltip(code, exp)
        return f" [{exp}] "

    body_xml = re.sub(r'<lex>(.*?)</lex>', lex_replacer, body_xml)

    # 2. Expand <ab> tags (general abbreviations)
    def ab_replacer(m):
        code = m.group(1).strip()
        code_dot = code if code.endswith('.') else code + '.'
        exp = ab_map.get(code, ab_map.get(code_dot, code))
        add_tooltip(code, exp)
        return f" {exp} "

    body_xml = re.sub(r'<ab>(.*?)</ab>', ab_replacer, body_xml)

    # 3. Expand <ls> tags (literature citations)
    def ls_replacer(m):
        raw_ls = m.group(1).strip()
        # Separate title code from volume/line numbers (e.g. "RV. x, 94, 5" -> "RV.", "x, 94, 5")
        parts = raw_ls.split(maxsplit=1)
        title_code = parts[0].strip()
        location_num = f" {parts[1]}" if len(parts) > 1 else ""

        title_code_dot = title_code if title_code.endswith('.') else title_code + '.'
        exp = ab_map.get(title_code, ab_map.get(title_code_dot, title_code))
        add_tooltip(title_code, exp)

        return f" [{exp}{location_num}] "

    body_xml = re.sub(r'<ls>(.*?)</ls>', ls_replacer, body_xml)

    return body_xml, detected_tooltips


# Initialize cache at module load time
init_abbreviations()
