"""
prompts.py — the AI half of Arzi Likho, and its deterministic stand-in.

Gemma's job is deliberately NARROW: turn the operator's plain-Hindi field notes into the
narrative paragraphs (and an English version) of a formal letter. Addressee, subject line,
acts, fees, time limits and portals are decided by forms.py — the model never writes them.
If a needed fact is blank, the letter shows a visible [placeholder], never an invention.

The mock (mock_draft / mock_reply) makes the whole app, the tests and the screenshots run
with zero network and zero API key — and doubles as the fallback when the model is down.
"""
from __future__ import annotations

import json
import re
from typing import Dict, List

import forms

# ----------------------------------------------------------------------------- system prompts
SYSTEM = """You are the drafting engine of "Arzi Likho", a tool used at cyber-café and Jan Seva Kendra
counters in small-town India to type formal Hindi applications (arziyaan) to government offices.

Your job: turn the operator's plain-Hindi field notes into the NARRATIVE paragraphs of a formal
letter. The fixed parts — addressee, subject line, act/section, fee, time limits, where to file —
are added by the app's templates. You never write them.

Return ONLY a JSON object with exactly these keys:
{"subject": "...", "body": ["...", "..."], "request": "...", "whatsapp": "...",
 "english": {"subject": "...", "body": ["...", "..."], "request": "..."}}

Rules:
1. LANGUAGE: shuddh, formal Hindi — the सरकारी कार्यालय register (कृपया, अतः, उपरोक्त, निवेदन है, भवदीय).
   No Hinglish, no Roman-script Hindi inside the Hindi fields. Official abbreviations are fine:
   आरटीआई, केवाईसी, एफआईआर, एनओसी, पी.आई.ओ.
2. FACTS: use ONLY the facts in the form. Never invent names, dates, numbers, amounts, places or events.
   If a needed detail is blank, write a placeholder in square brackets: [खाता संख्या], [तारीख लिखें].
3. TONE: respectful and unhurried. No threats, no legal advice, no promises about outcomes,
   no criticism of any officer or department.
4. LENGTH: body = 2–3 short paragraphs, ≤ 160 words total. request = 1–2 sentences ending with a
   polite कृपया. Subject ≤ 20 words, no "विषय:" prefix, no salutation inside the body.
5. whatsapp: a polite 1–2 line follow-up message the applicant can send later asking the status,
   with [संदर्भ संख्या] left blank.
6. english: a faithful formal-English version (subject/body/request) of the same letter, for offices
   that accept English.
7. No markdown, no emojis, no quotes around the JSON."""

BIODATA_SYSTEM = """You are the drafting engine of "Arzi Likho", a cyber-café tool in small-town India.
Today you are polishing a bio-data (बायोडाटा) — for a marriage or a job — from facts the operator typed in.

Return ONLY a JSON object with exactly these keys:
{"about": "...", "whatsapp": "...", "english_about": "..."}

Rules:
- "about": 3–4 lines of Hindi introducing the person warmly and respectfully — education, work, family,
  nature — using ONLY the given facts. No horoscope, no caste praise, no inventions.
- "whatsapp": one polite Hindi line to send with the bio-data PDF.
- "english_about": the same introduction in simple English.
- If something is blank, leave it out — do not guess. No markdown, no emojis."""


# ----------------------------------------------------------------------------- prompt builders
def _field_payload(matter: dict, fields: Dict[str, str]) -> str:
    rows = []
    for fld in matter["fields"]:
        v = (fields.get(fld["id"]) or "").strip()
        rows.append({"field": fld["id"], "label": fld["label"], "value": v})  # "" = operator left it blank
    return json.dumps(rows, ensure_ascii=False, indent=1)


def letter_prompt(matter: dict, district: str, fields: Dict[str, str]) -> List[dict]:
    """The matter's own facts are the ONLY input the model may use."""
    user = (
        f"MATTER_ID: {matter['id']}\n"
        f"MATTER: {matter['label']}\n"
        f"FIELD NOTES (value \"\" means the operator left it blank):\n{_field_payload(matter, fields)}\n\n"
        f"GUIDANCE — tone: {matter['tone']}\n"
        f"body outline: {'; '.join(matter['outline'])}\n"
        f"The subject line of the letter will be: \"{matter['subject_fn'](fields)}\" (written by the app — do not repeat it in the body).\n"
        f"Do NOT re-introduce the applicant's name/address in the first body paragraph — the app adds that line itself.\n\n"
        "Write the JSON object now."
    )
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def biodata_prompt(matter: dict, district: str, fields: Dict[str, str]) -> List[dict]:
    user = (
        f"MATTER_ID: {matter['id']}\n"
        f"MATTER: {matter['label']}\n"
        f"FIELD NOTES (value \"\" means blank):\n{_field_payload(matter, fields)}\n\n"
        "Write the JSON object now."
    )
    return [{"role": "system", "content": BIODATA_SYSTEM}, {"role": "user", "content": user}]


# ----------------------------------------------------------------------------- mock (no API key)
def _whatsapp_mock(fields: Dict[str, str], subject: str) -> str:
    name = (fields.get("name") or "").strip() or "[नाम]"
    mob = (fields.get("mobile") or "").strip() or "[मोबाइल]"
    return (f"नमस्ते, मैं {name} (मोबाइल {mob})। दिनांक [जमा करने की तारीख] को जमा की गई मेरी अर्ज़ी "
            f"'{subject}' (संदर्भ संख्या [संदर्भ संख्या]) की स्थिति बताने का कष्ट करें। धन्यवाद।")


def mock_draft(matter: dict, district: str, fields: Dict[str, str]) -> dict:
    """The whole letter, no model: subject from the template, body from the fact templates."""
    subject = matter["subject_fn"](fields)
    if matter.get("style") == "biodata":
        return {
            "about": (f"{(fields.get('name') or '[नाम]').strip()} — यह बायोडाटा दी गई जानकारी से तैयार किया गया है। "
                      "(AI मॉडल जुड़ने पर यहाँ एक सुंदर संक्षिप्त परिचय लिखा जाएगा।)"),
            "whatsapp": f"नमस्ते, {(fields.get('name') or '[नाम]').strip()} का बायोडाटा संलग्न है। कृपया देखें। धन्यवाद।",
            "english_about": "(Connect an AI model — LLM_API_KEY — to generate the English introduction.)",
        }
    body = forms.mock_body(matter, fields) or ["(विवरण ऊपर फ़ॉर्म में भरें।)"]
    return {
        "subject": subject,
        "body": body,
        "request": matter["request"],
        "whatsapp": _whatsapp_mock(fields, subject),
        "english": {
            "subject": matter.get("subject_en", ""),
            "body": ["(Connect an AI model — LLM_API_KEY — to generate the full English translation of this letter.)"],
            "request": "",
        },
    }


def mock_reply(messages: List[dict], json_mode: bool) -> str:
    """Registered as llm.MOCK_HANDLER: parse MATTER_ID from the prompt, answer deterministically."""
    user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    m = re.search(r"MATTER_ID:\s*(\S+)", user)
    matter = forms.get_matter(m.group(1)) if m else forms.MATTERS[0]
    f = re.search(r"FIELD NOTES.*?\n(\[.*?\])\n", user, re.S)
    fields: Dict[str, str] = {}
    if f:
        try:
            fields = {r["field"]: r["value"] for r in json.loads(f.group(1))}
        except Exception:  # noqa: BLE001
            fields = {}
    district = forms.DISTRICT_DEFAULT
    return json.dumps(mock_draft(matter, district, fields), ensure_ascii=False)


# ----------------------------------------------------------------------------- real path
def draft_letter(matter: dict, district: str, fields: Dict[str, str]) -> dict:
    """Call the model, then clamp its output to the schema (fallback = mock parts)."""
    import llm

    msgs = biodata_prompt(matter, district, fields) if matter.get("style") == "biodata" else letter_prompt(matter, district, fields)
    raw = llm.chat(msgs, json_mode=True, max_tokens=3000, budget=90)
    return validate_draft(llm.parse_json(raw), matter, district, fields)


def _s(x) -> str:
    return str(x or "").strip()


def validate_draft(d: dict, matter: dict, district: str, fields: Dict[str, str]) -> dict:
    """The model may return partial JSON; the letter must still be complete and safe."""
    mock = mock_draft(matter, district, fields)
    if not isinstance(d, dict):
        return mock
    if matter.get("style") == "biodata":
        return {
            "about": _s(d.get("about")) or mock["about"],
            "whatsapp": _s(d.get("whatsapp")) or mock["whatsapp"],
            "english_about": _s(d.get("english_about")) or mock["english_about"],
        }
    body = d.get("body")
    if isinstance(body, str):
        body = [p for p in body.split("\n") if p.strip()]
    body = [ _s(p) for p in body if _s(p) ][:4] if isinstance(body, list) else []
    if not body:
        body = mock["body"]
    english = d.get("english") if isinstance(d.get("english"), dict) else {}
    e_body = english.get("body")
    e_body = [ _s(p) for p in e_body if _s(p) ][:4] if isinstance(e_body, list) else (mock["english"]["body"] if e_body is None else [])
    return {
        "subject": _s(d.get("subject")) or mock["subject"],
        "body": body,
        "request": _s(d.get("request")) or mock["request"],
        "whatsapp": _s(d.get("whatsapp")) or mock["whatsapp"],
        "english": {
            "subject": _s(english.get("subject")) or mock["english"]["subject"],
            "body": e_body or mock["english"]["body"],
            "request": _s(english.get("request")),
        },
    }
