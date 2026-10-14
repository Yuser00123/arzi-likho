"""
अर्ज़ी लिखो (Arzi Likho) — 12 तरह की सरकारी अर्ज़ियाँ, 3 मिनट में।

Built for the typing counter of a cyber café / Jan Seva Kendra: the operator picks the matter,
fills 5–10 plain-Hindi fields, and gets a formal letter (सेवा में / विषय / महोदय / प्रार्थना / भवदीय /
संलग्नक) plus the "कहाँ जमा करें" box — printable, downloadable as .docx, translatable to English.

Who splits what: the legal/structural parts (addressee, act & section, fee, time limit, portals,
attachments) come from editable templates in forms.py — never from the model. The open-weight
model (Gemma 4) writes only the narrative paragraphs, and only from the facts given; blanks stay
visible [placeholders]. Nothing is stored on the server — drafts live in the browser (BrowserState).

Hacktoberfest 2026 · Week 2: Side Hustle · https://github.com/Yuser00123/arzi-likho
"""
from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path

_env = Path(__file__).with_name(".env")  # tiny .env loader (no python-dotenv dependency)
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

import gradio as gr  # noqa: E402
from fastapi import FastAPI  # noqa: E402

import forms  # noqa: E402
import letter  # noqa: E402
import llm  # noqa: E402
import prompts as P  # noqa: E402

llm.MOCK_HANDLER = P.mock_reply
REPO_URL = os.getenv("REPO_URL", "https://github.com/Yuser00123/arzi-likho")
STARTED = time.time()

TYPES = ("text", "textarea", "select")
POOL_SIZE = {"text": 10, "textarea": 4, "select": 3}
OFF = {"text": 0, "textarea": 10, "select": 14}
N_POOL = sum(POOL_SIZE.values())


def slot_map(matter: dict) -> dict:
    """field id → index in the flattened component pool (deterministic, mirrors apply_matter)."""
    used = {t: 0 for t in TYPES}
    m = {}
    for fld in matter["fields"]:
        m[fld["id"]] = OFF[fld["type"]] + used[fld["type"]]
        used[fld["type"]] += 1
    return m


def apply_matter(matter_id: str):
    """Relabel + show only the fields this matter needs (a fixed pool keeps the UI snappy)."""
    try:
        matter = forms.get_matter(matter_id or "")
    except KeyError:
        matter = None
    updates: list = [gr.update()] * N_POOL
    if not matter:
        return tuple(updates)
    used = {t: 0 for t in TYPES}
    for fld in matter["fields"]:
        idx = OFF[fld["type"]] + used[fld["type"]]
        used[fld["type"]] += 1
        if fld["type"] == "select":
            updates[idx] = gr.Dropdown(label=fld["label"], choices=fld["options"], value=None, visible=True)
        elif fld["type"] == "textarea":
            updates[idx] = gr.Textbox(label=fld["label"], placeholder=fld.get("ph", ""), lines=3, visible=True)
        else:
            updates[idx] = gr.Textbox(label=fld["label"], placeholder=fld.get("ph", ""), visible=True)
    return tuple(updates)


def _matter_choices():
    return [(f"{m['emoji']} {m['label']}", m["id"]) for m in forms.MATTERS]


def _draft_choices(store):
    return [(e["label"], e["id"]) for e in (store or [])]


def generate(matter_id, district, *args):
    """Operator's form → (status, letter text, कहाँ जमा करें, English, WhatsApp, drafts store)."""
    store, vals = list(args[-1] or []), args[:-1]
    try:
        matter = forms.get_matter((matter_id or "").strip())
    except KeyError:
        raise gr.Error("पहले बताएँ — किस काम की अर्ज़ी है?")
    district = (district or "").strip() or forms.DISTRICT_DEFAULT
    sm = slot_map(matter)
    fields = {f["id"]: (vals[sm[f["id"]]] or "").strip() for f in matter["fields"]}
    missing = [f["label"] for f in matter["fields"] if f.get("required") and not fields[f["id"]]]
    if missing:
        raise gr.Error("पहले ये ज़रूरी जानकारी भरें: " + ", ".join(missing))

    note = ""
    draft = None
    if llm.available():
        yield ("⏳ Gemma आपकी अर्ज़ी लिख रहा है… (आमतौर पर 30–70 सेकंड)", gr.update(), gr.update(), gr.update(), gr.update(), gr.update())
        try:
            draft = P.draft_letter(matter, district, fields)
        except Exception as err:  # noqa: BLE001 — the letter must still go out
            note = f"⚠️ मॉडल से लिख नहीं मिला ({err}) — नीचे नमूना प्रारूप (mock) है, पढ़कर मिलाकर इस्तेमाल करें।"
    if draft is None:
        draft = P.mock_draft(matter, district, fields)

    out = letter.compose(matter, district, fields, draft)
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "label": f"{datetime.now().strftime('%d %b %I:%M %p')} · {matter['emoji']} {matter['label'].split('—')[0].strip()} · {(fields.get('name') or '')[:18]}",
        "matter": matter["id"], "district": district, "fields": fields, "draft": draft,
    }
    store = ([entry] + [e for e in store if e.get("id") != entry["id"]])[:12]
    yield (note or f"✅ तैयार। ज़रूर पढ़ें — [कोष्ठक] वाली जगहें भरें, फिर प्रिंट करें।",
           out["letter"], out["kahan"], out["english"], out["whatsapp"], store)


def load_draft(choice, store):
    store = list(store or [])
    entry = next((e for e in store if e.get("id") == choice), None)
    if not entry:
        return ("⚠️ पहले सूची से अर्ज़ी चुनें।", gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update())
    matter = forms.get_matter(entry["matter"])
    sm = slot_map(matter)
    vals = [None] * N_POOL
    for f in matter["fields"]:
        vals[sm[f["id"]]] = entry["fields"].get(f["id"], "")
    pool_updates = []
    for i in range(N_POOL):
        if matter["fields"] and i in sm.values():
            pass  # value set below via vals
        pool_updates.append(gr.update())
    # set values through apply_matter-style updates (labels already correct for this matter)
    used = {t: 0 for t in TYPES}
    for f in matter["fields"]:
        idx = OFF[f["type"]] + used[f["type"]]
        used[f["type"]] += 1
        if f["type"] == "select":
            pool_updates[idx] = gr.Dropdown(label=f["label"], choices=f["options"], value=entry["fields"].get(f["id"]) or None, visible=True)
        elif f["type"] == "textarea":
            pool_updates[idx] = gr.Textbox(label=f["label"], placeholder=f.get("ph", ""), lines=3, value=entry["fields"].get(f["id"], ""), visible=True)
        else:
            pool_updates[idx] = gr.Textbox(label=f["label"], placeholder=f.get("ph", ""), value=entry["fields"].get(f["id"], ""), visible=True)
    out = letter.compose(matter, entry["district"], entry["fields"], entry["draft"])
    return (f"📂 पुरानी अर्ज़ी खुली — {out['subject']}", f"{matter['emoji']} {matter['label']}" and matter["id"],
            entry["district"], *pool_updates, out["letter"], out["kahan"], out["english"], out["whatsapp"])


def clear_everything():
    hidden = []
    for t, n in POOL_SIZE.items():
        for _ in range(n):
            hidden.append(gr.Dropdown(visible=False) if t == "select" else gr.Textbox(visible=False))
    return ("सब मिटा दिया गया।", None, forms.DISTRICT_DEFAULT, *hidden, "", "", "", "", "",
            gr.update(choices=[]), [])


def make_docx(letter_text, matter_id):
    if not (letter_text or "").strip():
        raise gr.Error("पहले अर्ज़ी बनाएँ।")
    try:
        label = forms.get_matter((matter_id or "").strip())["label"]
    except KeyError:
        label = "likho"
    return letter.docx_from_letter(letter_text, label)


# ----------------------------------------------------------------------------- UI
CSS = """
.gradio-container { max-width: 860px !important; margin: auto; }
#title h1 { font-size: 1.7rem; margin-bottom: 0; }
#howto { color: #555; }
#letter-print textarea { font-size: 1.02rem; line-height: 1.65; }
#kahan { background: #f6f8ef; border: 1px solid #d9e3c4; border-radius: 10px; padding: 10px 14px; }
button.lg { min-height: 52px; font-size: 1.05rem; }
@media print {
  body * { visibility: hidden; }
  #letter-print, #letter-print * { visibility: visible; }
  #letter-print { position: absolute; left: 0; top: 0; width: 100%; border: none; box-shadow: none; }
  #letter-print textarea { height: auto !important; overflow: visible !important; font-size: 12pt; }
}
"""
PRINT_JS = """() => {
  const ta = document.querySelector('#letter-print textarea');
  if (ta) { ta.style.height = 'auto'; ta.style.height = ta.scrollHeight + 'px'; }
  window.print();
  return null;
}"""
COPY_JS = """async (txt) => {
  try { await navigator.clipboard.writeText(txt); alert('कॉपी हो गया ✓ — अब WhatsApp में पेस्ट करें'); }
  catch (e) { alert('कॉपी नहीं हुआ — टेक्स्ट खुद सिलेक्ट करके कॉपी करें'); }
  return txt;
}"""

with gr.Blocks(title="अर्ज़ी लिखो") as demo:
    drafts = gr.BrowserState([], storage_key="arzi-likho-v1")
    gr.Markdown(
        "# ✍️ अर्ज़ी लिखो\n"
        "**साइबर कैफ़े / जन सेवा केंद्र की काउंटर के लिए** — 12 तरह की सरकारी अर्ज़ियाँ 3 मिनट में।\n"
        "पता, धारा, शुल्क और पोर्टल **टेम्पलेट** से आते हैं; बयान **Gemma** लिखता है — और जो जानकारी नहीं दी गई, "
        "वह **[कोष्ठक]** में खाली रहती है, कभी गढ़ी नहीं जाती।",
        elem_id="title",
    )
    gr.Markdown("**कैसे:** ① काम चुनें → ② जानकारी भरें → ③ अर्ज़ी बनाओ → पढ़ें, बदलें, प्रिंट करें।", elem_id="howto")

    with gr.Tab("✍️ अर्ज़ी बनाओ"):
        with gr.Group():
            with gr.Row():
                matter_dd = gr.Dropdown(choices=_matter_choices(), label="किस काम की अर्ज़ी?", scale=3, filterable=True)
                district_dd = gr.Dropdown(choices=forms.DISTRICTS, value=forms.DISTRICT_DEFAULT, label="जिला", scale=2, allow_custom_value=True)
            blurb_md = gr.Markdown("*ऊपर से काम चुनें — यहाँ उसकी जानकारी दिखेगी…*")
            with gr.Column():
                pool_comps = []
                for _ in range(POOL_SIZE["text"]):
                    pool_comps.append(gr.Textbox(visible=False))
                for _ in range(POOL_SIZE["textarea"]):
                    pool_comps.append(gr.Textbox(visible=False, lines=3))
                for _ in range(POOL_SIZE["select"]):
                    pool_comps.append(gr.Dropdown(visible=False, allow_custom_value=True))
            go_btn = gr.Button("🪶 अर्ज़ी बनाओ", variant="primary", elem_classes=["lg"])

        status_md = gr.Markdown()
        letter_tb = gr.Textbox(label="आपकी अर्ज़ी — यहाँ बदलाव कर सकते हैं", lines=20, elem_id="letter-print")
        with gr.Row():
            print_btn = gr.Button("🖨 प्रिंट / PDF")
            docx_btn = gr.DownloadButton("⬇️ Word (.docx) बनाओ")
        kahan_md = gr.Markdown(elem_id="kahan")
        with gr.Accordion("🇬🇧 English version (केंद्रीय कार्यालयों के लिए)", open=False):
            english_md = gr.Markdown()
        with gr.Accordion("💬 WhatsApp फॉलो-अप मैसेज", open=False):
            with gr.Row():
                whatsapp_tb = gr.Textbox(label="बाद में भेजने के लिए (संदर्भ संख्या भरकर)", scale=4)
                copy_btn = gr.Button("📋 कॉपी", scale=1)

    with gr.Tab("🗂 पिछली अर्ज़ियाँ"):
        gr.Markdown("<small>ड्राफ़्ट **केवल इस ब्राउज़र** में सुरक्षित हैं — सर्वर पर कुछ नहीं जाता।</small>")
        drafts_dd = gr.Dropdown(choices=[], label="अर्ज़ी चुनें")
        with gr.Row():
            load_btn = gr.Button("📂 खोलें")
            clear_btn = gr.Button("🗑 सब मिटाएँ", variant="stop")

    gr.Markdown(
        f"<small>⚠️ यह उपकरण **कानूनी सलाह नहीं** देता। कार्यालय, शुल्क और पोर्टल बदलते रहते हैं — जमा करने से पहले "
        f"कार्यालय / जन सुविधा केंद्र से पुष्टि कर लें। Model: **{llm.describe()}** · "
        f"<a href='{REPO_URL}'>Source</a> · Hacktoberfest 2026 · Week 2: Side Hustle</small>"
    )

    def _blurb(matter_id):
        try:
            m = forms.get_matter(matter_id or "")
        except KeyError:
            return "*ऊपर से काम चुनें — यहाँ उसकी जानकारी दिखेगी…*"
        return f"**{m['emoji']} {m['label']}** — {m['blurb']}"

    matter_dd.change(_blurb, inputs=[matter_dd], outputs=[blurb_md])
    matter_dd.change(apply_matter, inputs=[matter_dd], outputs=pool_comps)
    go_btn.click(generate, inputs=[matter_dd, district_dd, *pool_comps, drafts],
                 outputs=[status_md, letter_tb, kahan_md, english_md, whatsapp_tb, drafts])
    print_btn.click(None, js=PRINT_JS)
    docx_btn.click(make_docx, inputs=[letter_tb, matter_dd], outputs=[docx_btn])
    copy_btn.click(None, inputs=[whatsapp_tb], outputs=[whatsapp_tb], js=COPY_JS)

    load_outputs = [status_md, matter_dd, district_dd, *pool_comps, letter_tb, kahan_md, english_md, whatsapp_tb]
    load_btn.click(load_draft, inputs=[drafts_dd, drafts], outputs=load_outputs)
    clear_outputs = [status_md, matter_dd, district_dd, *pool_comps, letter_tb, kahan_md, english_md, whatsapp_tb, drafts_dd, drafts]
    clear_btn.click(clear_everything, outputs=clear_outputs)
    drafts.change(lambda s: gr.update(choices=_draft_choices(s)), inputs=[drafts], outputs=[drafts_dd])

api = FastAPI(title="Arzi Likho")


@api.get("/health")
def health():
    return {
        "status": "ok", "service": "arzi-likho", "model": llm.describe(),
        "matters": len(forms.MATTERS), "districts": len(forms.DISTRICTS),
        "uptime_seconds": int(time.time() - STARTED), "version": "1.0.0",
    }


app = gr.mount_gradio_app(api, demo, path="/", theme=gr.themes.Soft(primary_hue="emerald", secondary_hue="amber"), css=CSS, pwa=True)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))
