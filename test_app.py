"""Offline tests: python test_app.py   (no API key, no network — LLM_PROVIDER=mock)

Covers: the 12 templates render complete letters, blanks stay as visible [placeholders] and are
never invented, the "कहाँ जमा करें" box carries the right portals/helplines, the prompt sent to
the model contains only the operator's own fields, the model's JSON is clamped to the schema,
the .docx export opens, the grievance addressee follows city/village, and /health responds.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["LLM_PROVIDER"] = "mock"
sys.path.insert(0, str(Path(__file__).parent))

import app  # noqa: E402
import forms  # noqa: E402
import letter  # noqa: E402
import prompts as P  # noqa: E402


def sample(matter: dict, **overrides) -> dict:
    fields = {}
    for f in matter["fields"]:
        if f["id"] in overrides:
            fields[f["id"]] = overrides[f["id"]]
        elif f["type"] == "select":
            fields[f["id"]] = f["options"][0]
        elif f["id"] == "name":
            fields[f["id"]] = "राम कुमार यादव"
        elif f["id"] == "mobile":
            fields[f["id"]] = "9876543210"
        elif f["type"] == "textarea":
            fields[f["id"]] = "पहली लाइन\nदूसरी लाइन"
        else:
            fields[f["id"]] = f"टेस्ट-{f['id']}"
    return fields


def test_forms_verified():
    assert len(forms.MATTERS) == 12 and len(forms.DISTRICTS) == 75
    assert forms.DISTRICT_DEFAULT in forms.DISTRICTS
    assert "कानपुर नगर" in forms.DISTRICTS and "रायबरेली" in forms.DISTRICTS


def test_every_matter_renders_a_complete_letter():
    for m in forms.MATTERS:
        fields = sample(m)
        draft = P.mock_draft(m, forms.DISTRICT_DEFAULT, fields)
        out = letter.compose(m, forms.DISTRICT_DEFAULT, fields, draft)
        assert out["letter"].strip(), m["id"]
        assert out["whatsapp"].strip(), m["id"]
        assert "[" not in out["letter"], f"{m['id']} invented or left a blank despite full input"
        assert "None" not in out["letter"] and "{" not in out["letter"], m["id"]
        assert "टेस्ट-" in out["letter"], m["id"]  # operator's facts must survive into the letter
        if m.get("style") == "biodata":
            assert "व्यक्तिगत जानकारी" in out["letter"] and "शिक्षा" in out["letter"]
        else:
            for needed in ("सेवा में,", "विषय:", "महोदय,", "प्रार्थना है कि", "भवदीय,", "संलग्नक:"):
                assert needed in out["letter"], f"{m['id']} missing {needed!r}"
            assert out["kahan"].startswith("### 🏢"), m["id"]


def test_missing_facts_become_visible_placeholders_never_inventions():
    m = forms.get_matter("electricity")
    fields = sample(m, consumer_no="")  # required on the form, but mock path must still be safe
    out = letter.compose(m, forms.DISTRICT_DEFAULT, fields, P.mock_draft(m, forms.DISTRICT_DEFAULT, fields))
    assert "[केवाई नंबर लिखें]" in out["letter"]
    assert forms.sv({}, "any", "जो भी") == "[जो भी]"


def test_kahan_box_has_the_right_portals():
    cases = {"rti": "rtionline", "rti_appeal": "rtionline", "ration": "1967", "pension": "sspy",
             "electricity": "1912", "police": "112", "grievance": "jansunwai",
             "certificate": "edistrict", "school": "scholarship", "bank": "cms.rbi",
             "correction": "uidai", "biodata": ""}
    for mid, needle in cases.items():
        k = letter.kahan_box(forms.get_matter(mid))
        if needle:
            assert needle in k, f"{mid}: {needle!r} missing from कहाँ जमा करें"


def test_prompt_contains_only_this_matters_fields():
    m = forms.get_matter("police")
    fields = sample(m)
    msgs = P.letter_prompt(m, forms.DISTRICT_DEFAULT, fields)
    user = msgs[-1]["content"]
    assert "MATTER_ID: police" in user and "FIELD NOTES" in user
    for marker in ("टेस्ट-station", "टेस्ट-incident_date", "राम कुमार यादव"):
        assert marker in user, marker
    rti_label = forms.get_matter("rti")["fields"][5]["label"]  # 'कौन-सी सूचना चाहिए?'
    assert rti_label not in user  # no cross-matter leakage


def test_validate_draft_clamps_partial_model_json():
    m = forms.get_matter("ration")
    fields = sample(m)
    good = P.validate_draft({"body": "एक ही पैराग्राफ", "request": "कृपया कार्यवाही करें।"}, m, forms.DISTRICT_DEFAULT, fields)
    assert good["body"] == ["एक ही पैराग्राफ"] and good["request"] == "कृपया कार्यवाही करें।"
    assert good["whatsapp"] and good["english"]["subject"]  # fallbacks filled in
    bad = P.validate_draft({}, m, forms.DISTRICT_DEFAULT, fields)
    assert bad["body"] and bad["subject"] and bad["request"]
    biod = P.validate_draft({}, forms.get_matter("biodata"), forms.DISTRICT_DEFAULT, sample(forms.get_matter("biodata")))
    assert biod["about"] and biod["whatsapp"]


def test_grievance_addressee_city_vs_village():
    m = forms.get_matter("grievance")
    city = forms.addressee_lines(m, sample(m, area_type="शहर (नगर पालिका क्षेत्र)"), "रायबरेली")
    village = forms.addressee_lines(m, sample(m, area_type="गाँव (पंचायत क्षेत्र)"), "रायबरेली")
    assert any("नगर पालिका" in ln for ln in city)
    assert any("खंड विकास अधिकारी" in ln for ln in village)


def test_docx_opens_and_carries_the_letter():
    m = forms.get_matter("rti")
    fields = sample(m)
    out = letter.compose(m, forms.DISTRICT_DEFAULT, fields, P.mock_draft(m, forms.DISTRICT_DEFAULT, fields))
    path = letter.docx_from_letter(out["letter"], m["label"])
    from docx import Document

    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs)
    assert len(doc.paragraphs) >= 8
    assert "सेवा में," in text and "विषय:" in text and "राम कुमार यादव" in text
    Path(path).unlink(missing_ok=True)


def test_health_endpoint():
    from fastapi.testclient import TestClient

    r = TestClient(app.api).get("/health")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok" and d["matters"] == 12 and d["districts"] == 75 and d["service"] == "arzi-likho"


def test_generate_full_roundtrip_and_required_validation():
    m = forms.get_matter("ration")
    sm = app.slot_map(m)
    vals = [""] * app.N_POOL
    for f in m["fields"]:
        vals[sm[f["id"]]] = sample(m)[f["id"]]
    outputs = list(app.generate("ration", "रायबरेली", *vals, []))
    status, letter_text, kahan, english, whatsapp, store = outputs[-1]
    assert letter_text and "सेवा में," in letter_text and "रायबरेली" in letter_text
    assert len(store) == 1 and store[0]["matter"] == "ration"
    # a second letter for the same matter replaces nothing but stacks — max 12
    assert store[0]["draft"]["whatsapp"]  # draft survives for reload
    # required-field guard
    vals2 = list(vals)
    vals2[sm["detail"]] = ""
    try:
        list(app.generate("ration", "रायबरेली", *vals2, []))
        raised = False
    except Exception as err:  # gradio.Error
        raised = "ज़रूरी" in str(err)
    assert raised


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"✅ {name}")
            except Exception as err:  # noqa: BLE001
                failed += 1
                print(f"❌ {name}: {err!r}")
    sys.exit(1 if failed else 0)
