"""
forms.py — the deterministic half of Arzi Likho (अर्ज़ी लिखो).

Twelve matters that cyber-café / Jan Seva Kendra counters type every single day.
Every addressee, act/section, fee, time limit, portal, helpline and attachment list
lives HERE, in editable Python — the model NEVER writes these. The AI only turns the
operator's field notes into the narrative paragraphs. A café owner can open this file,
add their tehsil's office or fix a fee, and the app updates — no vendor ticket.

Fields:  type = "text" | "textarea" | "select"  (optional fields become visible
         [placeholder] blanks in the letter, never invented facts).
Style:   "letter" (formal government letter) | "biodata".
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

# ----------------------------------------------------------------------------- districts (UP, 75)
DISTRICTS = sorted([
    "कानपुर नगर", "कानपुर देहात", "रायबरेली", "लखनऊ", "उन्नाव", "बाराबंकी", "अमेठी", "सुल्तानपुर",
    "प्रतापगढ़", "फतेहपुर", "कौशांबी", "प्रयागराज", "झांसी", "ललितपुर", "जालौन", "बांदा", "चित्रकूट",
    "हमीरपुर", "महोबा", "बरेली", "बदायूँ", "शाहजहाँपुर", "पीलीभीत", "लखीमपुर खीरी", "हरदोई", "सीतापुर",
    "रामपुर", "मुरादाबाद", "बिजनौर", "अमरोहा", "संभल", "मेरठ", "बागपत", "हापुड़", "गौतम बुद्ध नगर",
    "गाज़ियाबाद", "बुलंदशहर", "अलीगढ़", "हाथरस", "कासगंज", "एटा", "आगरा", "फ़िरोज़ाबाद", "मथुरा",
    "मैनपुरी", "इटावा", "औरैया", "फ़र्रुख़ाबाद", "कन्नौज", "सहारनपुर", "मुज़फ़्फ़रनगर", "शामली",
    "बहराइच", "श्रावस्ती", "बलरामपुर", "गोंडा", "अयोध्या", "अंबेडकर नगर", "बस्ती", "संत कबीर नगर",
    "सिद्धार्थनगर", "महाराजगंज", "गोरखपुर", "कुशीनगर", "देवरिया", "आज़मगढ़", "मऊ", "बलिया", "गाज़ीपुर",
    "चंदौली", "वाराणसी", "भदोही", "जौनपुर", "मिर्ज़ापुर", "सोनभद्र",
])
DISTRICT_DEFAULT = "रायबरेली"
assert len(DISTRICTS) == 75, len(DISTRICTS)


# ----------------------------------------------------------------------------- helpers
def sv(fields: Dict[str, str], key: str, placeholder: str) -> str:
    """Field value or a visible blank — the letter never invents facts."""
    v = (fields.get(key) or "").strip()
    return v if v else f"[{placeholder}]"


def _line(fields: Dict[str, str], key: str, tpl: str) -> Optional[str]:
    v = (fields.get(key) or "").strip()
    return tpl.format(v=v) if v else None


def personal(father_label: str = "पिता / पति का नाम") -> List[dict]:
    """The four-five identity fields every letter needs (gender only fixes Hindi grammar)."""
    return [
        {"id": "name", "type": "text", "label": "आवेदक का पूरा नाम", "ph": "जैसे: राम कुमार यादव", "required": True},
        {"id": "father", "type": "text", "label": father_label, "ph": "जैसे: श्री सुरेश यादव", "required": True},
        {"id": "address", "type": "text", "label": "पूरा पता (गाँव/मोहल्ला, पोस्ट, थाना)", "ph": "जैसे: मोहल्ला गाँधी नगर, पोस्ट सदर, थाना कोतवाली", "required": True},
        {"id": "mobile", "type": "text", "label": "मोबाइल नंबर", "ph": "10 अंकों का नंबर", "required": False},
        {"id": "gender", "type": "select", "label": "लिंग (व्याकरण के लिए)", "options": ["पुरुष", "महिला"], "required": False},
    ]


DEPARTMENTS = [
    "विद्युत विभाग (उ.प्र. पावर कॉर्पोरेशन)", "शिक्षा विभाग", "स्वास्थ्य एवं परिवार कल्याण विभाग",
    "पंचायती राज विभाग", "राजस्व विभाग", "पुलिस विभाग", "जन निर्माण विभाग", "ग्राम्य विकास विभाग", "अन्य विभाग",
]


# ----------------------------------------------------------------------------- the 12 matters
MATTERS: List[dict] = [
    # 1 ---------------------------------------------------------------- RTI application
    {
        "id": "rti",
        "emoji": "📋",
        "label": "आरटीआई — किसी विभाग से सूचना माँगना",
        "blurb": "सूचना का अधिकार अधिनियम 2005, धारा 6(1) — ₹10 शुल्क, 30 दिन में जवाब",
        "style": "letter",
        "fields": personal() + [
            {"id": "department", "type": "select", "label": "किस विभाग से सूचना चाहिए?", "options": DEPARTMENTS, "required": True},
            {"id": "points", "type": "textarea", "label": "कौन-सी सूचना चाहिए? (एक बिंदु = एक लाइन)", "ph": "जैसे: पिछले वर्ष के सभी बिलों का ब्योरा\nगलत बिल वसूली के आदेश की प्रति", "required": True},
            {"id": "period", "type": "text", "label": "किस अवधि की सूचना? (वैकल्पिक)", "ph": "जैसे: अप्रैल 2025 से मार्च 2026", "required": False},
        ],
        "addressee": ["जन सूचना अधिकारी (पी.आई.ओ.)", "{department}", "जिला — {district} (उत्तर प्रदेश)"],
        "legal": "सूचना का अधिकार अधिनियम, 2005 — धारा 6(1)",
        "fee": "₹10 नकद / भारतीय पोस्टल ऑर्डर (बी.पी.एल. प्रमाण-पत्रधारक शुल्क से मुक्त)",
        "time_limit": "जवाब 30 दिन में (जीवन-मृत्यु से जुड़ी सूचना 48 घंटे में)",
        "online": "rtionline.up.gov.in (उ.प्र.) · rtionline.gov.in (केंद्र)",
        "helpline": "सीएम हेल्पलाइन 1076",
        "attachments": ["आवेदन की पावती (अपने पास रखें)", "बी.पी.एल. कार्ड की प्रति (शुल्क मुक्ति हेतु, यदि हो)"],
        "subject_fn": lambda f: f"{sv(f, 'department', 'विभाग का नाम')} के अंतर्गत सूचना उपलब्ध कराने बाबत आवेदन",
        "subject_en": "Application under the Right to Information Act, 2005",
        "facts": [
            lambda f: f"मुझे {sv(f, 'department', 'विभाग का नाम')} से निम्नलिखित सूचना चाहिए — {sv(f, 'points', 'सूचना के बिंदु लिखें')}",
            lambda f: _line(f, "period", "यह सूचना {v} की है।"),
        ],
        "request": "कृपया निर्धारित अवधि में उपरोक्त सूचना उपलब्ध कराने की कृपा करें।",
        "tone": "neutral and precise; list the information points exactly as given",
        "outline": ["who is asking and for which records (restate the points as numbered items)",
                    "the period/scope of the request if given"],
    },
    # 2 ---------------------------------------------------------------- RTI first appeal
    {
        "id": "rti_appeal",
        "emoji": "📨",
        "label": "आरटीआई पहली अपील (जवाब नहीं मिला / अधूरा मिला)",
        "blurb": "धारा 19(1) — जवाब न मिलने पर 30 दिन के भीतर, कोई शुल्क नहीं",
        "style": "letter",
        "fields": personal() + [
            {"id": "department", "type": "select", "label": "किस विभाग को आरटीआई भेजी थी?", "options": DEPARTMENTS, "required": True},
            {"id": "rti_date", "type": "text", "label": "मूल आरटीआई कब जमा की थी?", "ph": "जैसे: 05/08/2026", "required": True},
            {"id": "reply_status", "type": "select", "label": "जवाब का क्या हुआ?", "options": ["जवाब नहीं मिला", "अधूरा जवाब मिला", "सूचना देने से मना कर दिया गया", "गलत सूचना दी गई"], "required": True},
            {"id": "points", "type": "textarea", "label": "किन बिंदुओं का जवाब नहीं मिला / क्या गड़बड़ लगी?", "ph": "अपने मूल बिंदु यहाँ लिखें", "required": True},
        ],
        "addressee": ["प्रथम अपीलीय अधिकारी", "{department}", "जिला — {district} (उत्तर प्रदेश)"],
        "legal": "सूचना का अधिकार अधिनियम, 2005 — धारा 19(1)",
        "fee": "कोई शुल्क नहीं",
        "time_limit": "जवाब न मिलने की स्थिति में 30 दिन के भीतर पहली अपील; निपटान 30–45 दिन",
        "online": "rtionline.gov.in → 'Submit First Appeal' (यदि मूल आवेदन ऑनलाइन जमा हुआ था)",
        "helpline": "सीएम हेल्पलाइन 1076",
        "attachments": ["मूल आरटीआई आवेदन की प्रति", "जमा कराने की पावती", "मिले जवाब की प्रति (यदि मिला हो)"],
        "subject_fn": lambda f: f"दिनांक {sv(f, 'rti_date', 'आरटीआई जमा करने की तारीख')} के आरटीआई आवेदन के संबंध में प्रथम अपील",
        "subject_en": "First appeal under Section 19(1) of the RTI Act, 2005",
        "facts": [
            lambda f: f"मैंने दिनांक {sv(f, 'rti_date', 'तारीख लिखें')} को {sv(f, 'department', 'विभाग का नाम')} में सूचना का अधिकार अधिनियम 2005 के अंतर्गत एक आवेदन जमा किया था।",
            lambda f: f"उक्त आवेदन का {sv(f, 'reply_status', 'जवाब की स्थिति लिखें')}। मुझे निम्नलिखित सूचना चाहिए थी — {sv(f, 'points', 'बिंदु लिखें')}",
        ],
        "request": "कृपया मेरी अपील स्वीकार कर निर्धारित अवधि में संपूर्ण सूचना उपलब्ध कराने की कृपा करें।",
        "tone": "firm but respectful; stick strictly to what was asked and what went missing",
        "outline": ["the original application: date, department, what was asked",
                    "what went wrong with the reply"],
    },
    # 3 ---------------------------------------------------------------- ration card
    {
        "id": "ration",
        "emoji": "🛒",
        "label": "राशन कार्ड — नया / नाम जोड़ना / सुधार / शिकायत",
        "blurb": "जिला पूर्ति अधिकारी · fcs.up.gov.in · हेल्पलाइन 1967",
        "style": "letter",
        "fields": personal() + [
            {"id": "purpose", "type": "select", "label": "क्या कराना है?", "options": ["नया राशन कार्ड बनवाना है", "परिवार के सदस्य का नाम जोड़ना है", "कार्ड से नाम हटाना है", "कार्ड में सुधार कराना है", "दुकान से राशन नहीं मिल रहा है"], "required": True},
            {"id": "card_no", "type": "text", "label": "राशन कार्ड संख्या (वैकल्पिक)", "ph": "यदि कार्ड पहले से है", "required": False},
            {"id": "shop", "type": "text", "label": "राशन की दुकान / डीलर का नाम (वैकल्पिक)", "ph": "जैसे: श्री शर्मा किराना स्टोर, सदर बाज़ार", "required": False},
            {"id": "detail", "type": "textarea", "label": "पूरी बात — क्या कराना है, किसका नाम, कब से…", "ph": "जैसे: मेरी पत्नी का नाम कार्ड में जोड़वाना है, शादी जून 2026 में हुई है", "required": True},
        ],
        "addressee": ["जिला पूर्ति अधिकारी महोदय", "खाद्य एवं रसद नियंत्रण विभाग", "जिला — {district} (उत्तर प्रदेश)"],
        "legal": "राष्ट्रीय खाद्य सुरक्षा अधिनियम, 2013",
        "fee": "जन सुविधा केंद्र पर जानकारी लें (नए कार्ड हेतु सामान्यतः ₹20–45)",
        "time_limit": "सामान्यतः 30 दिन में निपटान",
        "online": "fcs.up.gov.in (खाद्य एवं रसद विभाग) · शिकायत: jansunwai.up.gov.in",
        "helpline": "1967 (खाद्य एवं आपूर्ति हेल्पलाइन)",
        "attachments": ["आधार कार्ड की प्रति", "पुराना राशन कार्ड (यदि हो)", "आय / निवास प्रमाण पत्र (नए कार्ड हेतु)"],
        "subject_fn": lambda f: (f"{sv(f, 'purpose', 'काम लिखें')} — राशन कार्ड सं. {f['card_no'].strip()}" if f.get("card_no", "").strip() else f"{sv(f, 'purpose', 'काम लिखें')} — राशन कार्ड के संबंध में आवेदन"),
        "subject_en": "Application regarding my ration card",
        "facts": [
            lambda f: f"{sv(f, 'purpose', 'काम लिखें')}। विवरण: {sv(f, 'detail', 'विवरण लिखें')}",
            lambda f: _line(f, "card_no", "मेरा राशन कार्ड संख्या {v} है।"),
            lambda f: _line(f, "shop", "मेरी राशन दुकान '{v}' है।"),
        ],
        "request": "कृपया उपरोक्त कार्यवाही शीघ्र कराने की कृपा करें।",
        "tone": "simple, factual; keep household details exactly as given",
        "outline": ["what needs to happen (new card / add name / correction / complaint)", "the specifics: whose name, since when, which shop"],
    },
    # 4 ---------------------------------------------------------------- pension
    {
        "id": "pension",
        "emoji": "👵",
        "label": "पेंशन — वृद्धावस्था / विधवा / दिव्यांग",
        "blurb": "जिला समाज कल्याण अधिकारी · sspy-up.gov.in",
        "style": "letter",
        "fields": personal() + [
            {"id": "ptype", "type": "select", "label": "कौन-सी पेंशन?", "options": ["वृद्धावस्था पेंशन", "विधवा पेंशन", "दिव्यांग पेंशन"], "required": True},
            {"id": "purpose", "type": "select", "label": "क्या मामला है?", "options": ["नई पेंशन के लिए आवेदन है", "पेंशन की किश्त रुकी है", "पेंशन स्वीकृत हुई, पैसा नहीं मिल रहा"], "required": True},
            {"id": "last_credit", "type": "text", "label": "पिछली किश्त कब तक मिली थी? (वैकल्पिक)", "ph": "जैसे: मार्च 2026", "required": False},
            {"id": "detail", "type": "textarea", "label": "पूरी बात लिखें", "ph": "जैसे: पेंशन अप्रैल 2026 से बंद है, बैंक में कुछ जमा नहीं हुआ", "required": True},
        ],
        "addressee": ["जिला समाज कल्याण अधिकारी महोदय", "समाज कल्याण विभाग", "जिला — {district} (उत्तर प्रदेश)"],
        "legal": "उत्तर प्रदेश सरकार की सामाजिक सुरक्षा पेंशन योजनाएँ",
        "fee": "कोई शुल्क नहीं (जन सुविधा केंद्र का शुल्क अलग)",
        "time_limit": "नई पेंशन: सामान्यतः 60 दिन · रुकी किश्त: 30 दिन",
        "online": "sspy-up.gov.in (पेंशन पोर्टल) · शिकायत: jansunwai.up.gov.in",
        "helpline": "181 (समाज कल्याण हेल्पलाइन)",
        "attachments": ["आधार कार्ड", "बैंक पासबुक की प्रति", "आय प्रमाण पत्र", "पासपोर्ट फोटो", "विधवा पेंशन हेतु: पति का मृत्यु प्रमाण पत्र", "दिव्यांग पेंशन हेतु: दिव्यांगता प्रमाण पत्र"],
        "subject_fn": lambda f: f"{sv(f, 'ptype', 'पेंशन का नाम')} — {sv(f, 'purpose', 'मामला लिखें')}",
        "subject_en": "Application regarding pension",
        "facts": [
            lambda f: f"{sv(f, 'purpose', 'मामला लिखें')}। विवरण: {sv(f, 'detail', 'विवरण लिखें')}",
            lambda f: _line(f, "last_credit", "पिछली किश्त {v} तक मेरे खाते में आई थी।"),
        ],
        "request": "कृपया मेरा आवेदन स्वीकार कर आवश्यक कार्यवाही शीघ्र कराने की कृपा करें।",
        "tone": "dignified and simple; this is often written for an elderly person — no jargon",
        "outline": ["what kind of pension and what happened", "timeline: last credit, when it stopped"],
    },
    # 5 ---------------------------------------------------------------- electricity
    {
        "id": "electricity",
        "emoji": "⚡",
        "label": "बिजली — गलत बिल / मीटर / कनेक्शन / कटौती",
        "blurb": "अधिशासी अभियंता (यूपीपीसीएल) · हेल्पलाइन 1912",
        "style": "letter",
        "fields": personal() + [
            {"id": "issue", "type": "select", "label": "क्या समस्या है?", "options": ["अत्यधिक / गलत बिल आया है", "मीटर खराब है", "नया कनेक्शन चाहिए", "बार-बार बिजली कटती है", "खंभा / तार की समस्या है", "बिल जमा होने पर भी कनेक्शन काटा गया"], "required": True},
            {"id": "consumer_no", "type": "text", "label": "उपभोक्ता (केवाई) नंबर", "ph": "बिल के ऊपर लिखा होता है", "required": True},
            {"id": "bill_month", "type": "text", "label": "किस महीने का बिल? (वैकल्पिक)", "ph": "जैसे: सितंबर 2026", "required": False},
            {"id": "detail", "type": "textarea", "label": "पूरी बात लिखें", "ph": "जैसे: हमेशा ₹400 का बिल आता था, इस बार ₹3800 आया है, कोई नई उपकरण नहीं लगा", "required": True},
        ],
        "addressee": ["अधिशासी अभियंता महोदय", "विद्युत वितरण खंड", "उ.प्र. पावर कॉर्पोरेशन लि.", "जिला — {district} (उत्तर प्रदेश)"],
        "legal": "विद्युत अधिनियम, 2003 — उपभोक्ता शिकायत निस्तारण गारंटी",
        "fee": "कोई शुल्क नहीं (शिकायत हेतु)",
        "time_limit": "बिल शिकायत: सामान्यतः 15–30 दिन",
        "online": "1912 (बिजली हेल्पलाइन) · uppcl.org → 'मेरी शिकायत दर्ज करें'",
        "helpline": "1912",
        "attachments": ["विद्युत बिल की प्रति", "पुरानी जमा रसीदों की प्रतियाँ"],
        "subject_fn": lambda f: f"उपभोक्ता संख्या {sv(f, 'consumer_no', 'केवाई नंबर लिखें')} — {sv(f, 'issue', 'समस्या लिखें')}",
        "subject_en": "Complaint regarding electricity connection",
        "facts": [
            lambda f: f"मेरा उपभोक्ता (केवाई) नंबर {sv(f, 'consumer_no', 'केवाई नंबर लिखें')} है। {sv(f, 'issue', 'समस्या लिखें')}।",
            lambda f: f"विवरण: {sv(f, 'detail', 'विवरण लिखें')}",
            lambda f: _line(f, "bill_month", "यह शिकायत {v} के बिल के संबंध में है।"),
        ],
        "request": "कृपया उपरोक्त शिकायत की जाँच कराकर आवश्यक कार्यवाही करने की कृपा करें।",
        "tone": "factual; amounts, months and account numbers must match the form exactly",
        "outline": ["the connection and the problem", "the specifics: bill month, amounts, how long"],
    },
    # 6 ---------------------------------------------------------------- police complaint
    {
        "id": "police",
        "emoji": "🚨",
        "label": "पुलिस — शिकायत / एफआईआर दर्ज कराना",
        "blurb": "थानाध्यक्ष (प्रतिलिपि: पुलिस अधीक्षक) · 112 आपातकाल",
        "style": "letter",
        "fields": personal() + [
            {"id": "station", "type": "text", "label": "थाने का नाम", "ph": "जैसे: थाना कोतवाली", "required": True},
            {"id": "incident_date", "type": "text", "label": "घटना की तारीख", "ph": "जैसे: 10/10/2026", "required": True},
            {"id": "place", "type": "text", "label": "घटनास्थल (गाँव/मोहल्ला, गली…)", "ph": "जैसे: गाँधी नगर, बस स्टैंड के पास", "required": True},
            {"id": "against", "type": "text", "label": "किसके विरुद्ध? (वैकल्पिक)", "ph": "नाम / पहचान, जितनी पता हो", "required": False},
            {"id": "want", "type": "select", "label": "क्या चाहते हैं?", "options": ["एफआईआर दर्ज करानी है", "लिखित शिकायत दर्ज करानी है"], "required": True},
            {"id": "detail", "type": "textarea", "label": "क्या हुआ — क्रम से लिखें", "ph": "जैसे: शाम 7 बजे घर लौट रहा था, तभी…", "required": True},
        ],
        "addressee": ["थानाध्यक्ष महोदय", "थाना — {station}", "जिला — {district} (उत्तर प्रदेश)"],
        "cc": ["प्रतिलिपि — पुलिस अधीक्षक महोदय, जिला {district} को सूचनार्थ एवं आवश्यक कार्यवाही हेतु"],
        "legal": "दंड प्रक्रिया संहिता (सी.आर.पी.सी.) — धारा 154 (एफआईआर)",
        "fee": "कोई शुल्क नहीं",
        "time_limit": "तत्काल शिकायत दर्ज करनी चाहिए; पावती/शिकायत की प्रति अवश्य लें",
        "online": "112 (आपातकालीन) · uppolice.gov.in → ऑनलाइन शिकायत",
        "helpline": "112",
        "attachments": ["पहचान पत्र की प्रति", "चोट का मेडिकल (यदि हो)", "सबूत / गवाहों का विवरण (यदि हो)"],
        "subject_fn": lambda f: f"दिनांक {sv(f, 'incident_date', 'तारीख लिखें')} को घटित घटना ({sv(f, 'place', 'स्थान लिखें')}) की शिकायत",
        "subject_en": "Complaint regarding an incident",
        "facts": [
            lambda f: f"दिनांक {sv(f, 'incident_date', 'तारीख लिखें')} को {sv(f, 'place', 'स्थान लिखें')} में मेरे साथ निम्नलिखित घटना घटी — {sv(f, 'detail', 'घटना लिखें')}",
            lambda f: _line(f, "against", "यह घटना {v} के द्वारा की गई है।"),
        ],
        "request": "कृपया मेरी शिकायत दर्ज कर आवश्यक कार्यवाही करने की कृपा करें।",
        "tone": "chronological and unemotional; dates, places and sequence exactly as given — no accusations beyond the facts",
        "outline": ["when and where it happened, in order", "who was involved (if known)"],
    },
    # 7 ---------------------------------------------------------------- public grievance
    {
        "id": "grievance",
        "emoji": "🛠️",
        "label": "सरकारी शिकायत — सड़क / नाली / पानी / बत्ती / सफाई",
        "blurb": "नगर पालिका / खंड विकास अधिकारी · jansunwai.up.gov.in · 1076",
        "style": "letter",
        "fields": personal() + [
            {"id": "area_type", "type": "select", "label": "जगह शहर में है या गाँव में?", "options": ["शहर (नगर पालिका क्षेत्र)", "गाँव (पंचायत क्षेत्र)"], "required": True},
            {"id": "gtype", "type": "select", "label": "क्या समस्या है?", "options": ["सड़क टूटी है", "नाली जाम / टूटी है", "पेयजल की समस्या है", "स्ट्रीट लाइट खराब है", "अतिक्रमण है", "सफाई नहीं होती", "अन्य समस्या"], "required": True},
            {"id": "place", "type": "text", "label": "समस्या का स्थान (मोहल्ला/गाँव, गली, सड़क…)", "ph": "जैसे: शास्त्री नगर, गली सं. 4, मस्जिद के सामने", "required": True},
            {"id": "since", "type": "text", "label": "कब से है? (वैकल्पिक)", "ph": "जैसे: लगभग 2 महीने से", "required": False},
            {"id": "detail", "type": "textarea", "label": "समस्या से क्या असर है? (वैकल्पिक)", "ph": "जैसे: बरसात में पानी जम जाता है, बच्चों के स्कूल जाने में दिक्कत", "required": False},
        ],
        "addressee_fn": lambda f, d: (
            ["अधिशासी अधिकारी महोदय", "नगर पालिका परिषद", f"{d} (उत्तर प्रदेश)"] if f.get("area_type", "").startswith("शहर")
            else ["खंड विकास अधिकारी महोदय", "विकास खंड — [खंड का नाम]", f"जिला — {d} (उत्तर प्रदेश)"]
        ),
        "legal": "",
        "fee": "कोई शुल्क नहीं",
        "time_limit": "आई.जी.आर.एस. (जनसुनवाई) शिकायतों का निपटान सामान्यतः 30 दिन",
        "online": "jansunwai.up.gov.in (आई.जी.आर.एस.) · सीएम हेल्पलाइन 1076",
        "helpline": "1076",
        "attachments": ["समस्या की फोटो (यदि खींची हो)"],
        "subject_fn": lambda f: f"{sv(f, 'place', 'स्थान लिखें')} — {sv(f, 'gtype', 'समस्या लिखें')}",
        "subject_en": "Complaint regarding a public problem",
        "facts": [
            lambda f: f"{sv(f, 'place', 'स्थान लिखें')} में {sv(f, 'gtype', 'समस्या लिखें')}।",
            lambda f: _line(f, "since", "यह समस्या {v} से है।"),
            lambda f: _line(f, "detail", "{v}"),
        ],
        "request": "कृपया उपरोक्त समस्या का निरीक्षण कराकर शीघ्र सुधार कराने की कृपा करें।",
        "tone": "civic and matter-of-fact; describe impact on daily life in the complainant's own words",
        "outline": ["the problem and its exact location", "how long it has been there and how it affects people"],
    },
    # 8 ---------------------------------------------------------------- certificates
    {
        "id": "certificate",
        "emoji": "📜",
        "label": "प्रमाण पत्र — आय / निवास / जाति / चरित्र",
        "blurb": "तहसीलदार · edistrict.up.gov.in · जन सुविधा केंद्र",
        "style": "letter",
        "fields": personal() + [
            {"id": "ctype", "type": "select", "label": "कौन-सा प्रमाण पत्र चाहिए?", "options": ["आय प्रमाण पत्र", "निवास प्रमाण पत्र", "जाति प्रमाण पत्र", "चरित्र प्रमाण पत्र"], "required": True},
            {"id": "purpose", "type": "text", "label": "किस काम के लिए चाहिए? (वैकल्पिक)", "ph": "जैसे: छात्रवृत्ति फॉर्म के लिए", "required": False},
            {"id": "tehsil", "type": "text", "label": "तहसील का नाम (वैकल्पिक)", "ph": "जैसे: सदर", "required": False},
        ],
        "addressee": ["तहसीलदार महोदय", "तहसील — {tehsil}", "जिला — {district} (उत्तर प्रदेश)"],
        "legal": "",
        "fee": "जन सुविधा केंद्र पर जानकारी लें (सामान्यतः ₹20–60)",
        "time_limit": "ई-डिस्ट्रिक्ट पोर्टल पर सामान्यतः 15–21 दिन",
        "online": "edistrict.up.gov.in (ई-डिस्ट्रिक्ट) · नज़दीकी जन सुविधा केंद्र (सी.एस.सी.)",
        "helpline": "1076",
        "attachments": ["आधार कार्ड", "राशन कार्ड / पुराना प्रमाण पत्र", "पासपोर्ट फोटो", "स्कूल प्रमाण पत्र (जाति प्रमाण पत्र हेतु, यदि हो)"],
        "subject_fn": lambda f: f"{sv(f, 'ctype', 'प्रमाण पत्र चुनें')} जारी कराने हेतु आवेदन",
        "subject_en": "Application for issuance of a certificate",
        "facts": [
            lambda f: f"मुझे {sv(f, 'ctype', 'प्रमाण पत्र चुनें')} जारी कराना है।",
            lambda f: _line(f, "purpose", "यह प्रमाण पत्र {v} के लिए आवश्यक है।"),
            lambda f: _line(f, "tehsil", "मेरी तहसील {v} है।"),
        ],
        "request": "कृपया मेरा आवेदन स्वीकार कर उक्त प्रमाण पत्र जारी कराने की कृपा करें।",
        "tone": "short and formal",
        "outline": ["which certificate and why it is needed"],
    },
    # 9 ---------------------------------------------------------------- school
    {
        "id": "school",
        "emoji": "🎓",
        "label": "स्कूल — टीसी / बोनाफाइड / छात्रवृत्ति / फीस माफी",
        "blurb": "प्रधानाचार्य · scholarship.up.gov.in",
        "style": "letter",
        "fields": personal("पिता का नाम (छात्र के)") + [
            {"id": "school_name", "type": "text", "label": "विद्यालय का नाम व पता", "ph": "जैसे: राजकीय इंटर कॉलेज, सदर रोड", "required": True},
            {"id": "stype", "type": "select", "label": "क्या चाहिए?", "options": ["ट्रांसफर सर्टिफिकेट (टी.सी.) चाहिए", "बोनाफाइड प्रमाण पत्र चाहिए", "छात्रवृत्ति हेतु प्रमाण पत्र चाहिए", "फीस माफी / छूट का अनुरोध है"], "required": True},
            {"id": "student", "type": "text", "label": "छात्र/छात्रा का नाम (वैकल्पिक, यदि आवेदक स्वयं नहीं हैं)", "ph": "जैसे: अंशु यादव", "required": False},
            {"id": "cls", "type": "text", "label": "कक्षा व सत्र", "ph": "जैसे: कक्षा 10, सत्र 2025–26", "required": True},
            {"id": "roll", "type": "text", "label": "अनुक्रमांक / स्कॉलर नंबर (वैकल्पिक)", "ph": "यदि पता हो", "required": False},
            {"id": "reason", "type": "text", "label": "कारण (वैकल्पिक — टीसी / फीस माफी हेतु)", "ph": "जैसे: पिता का तबादला, परिवार में आर्थिक परेशानी", "required": False},
        ],
        "addressee": ["प्रधानाचार्य महोदय", "{school_name}"],
        "legal": "",
        "fee": "कोई शुल्क नहीं (टी.सी. सामान्यतः निःशुल्क)",
        "time_limit": "सामान्यतः तुरंत / 7 दिन",
        "online": "छात्रवृत्ति: scholarship.up.gov.in · बाकी: विद्यालय में",
        "helpline": "1076",
        "attachments": ["पुरानी फीस रसीद", "आधार कार्ड की प्रति", "स्कॉलर नंबर वाली पुस्तिका"],
        "subject_fn": lambda f: (f"{sv(f, 'stype', 'काम चुनें')} — {f['student'].strip()}, {sv(f, 'cls', 'कक्षा लिखें')}" if f.get("student", "").strip() else f"{sv(f, 'stype', 'काम चुनें')} — {sv(f, 'cls', 'कक्षा लिखें')}"),
        "subject_en": "Request to the school principal",
        "facts": [
            lambda f: (f"मेरी सन्तान {f['student'].strip()} आपके विद्यालय में {sv(f, 'cls', 'कक्षा लिखें')} में पढ़ती है।" if f.get("student", "").strip() else f"मैं स्वयं आपके विद्यालय में {sv(f, 'cls', 'कक्षा लिखें')} में पढ़ता/पढ़ती हूँ।"),
            lambda f: f"{sv(f, 'stype', 'काम चुनें')}।",
            lambda f: _line(f, "roll", "अनुक्रमांक/स्कॉलर नंबर {v} है।"),
            lambda f: _line(f, "reason", "कारण: {v}"),
        ],
        "request": "कृपया मेरा अनुरोध स्वीकार कर आवश्यक प्रमाण पत्र जारी कराने की कृपा करें।",
        "tone": "polite parent/child tone to a principal",
        "outline": ["who studies here (class, roll no)", "what is needed and why"],
    },
    # 10 --------------------------------------------------------------- bank
    {
        "id": "bank",
        "emoji": "🏦",
        "label": "बैंक — केवाईसी / खाता बंद / एनओसी / गलत कटौती",
        "blurb": "शाखा प्रबंधक · शिकायत: cms.rbi.org.in (बैंकिंग लोकपाल)",
        "style": "letter",
        "fields": personal() + [
            {"id": "bank", "type": "text", "label": "बैंक का नाम", "ph": "जैसे: भारतीय स्टेट बैंक", "required": True},
            {"id": "branch", "type": "text", "label": "शाखा का नाम / पता", "ph": "जैसे: सदर बाज़ार शाखा", "required": True},
            {"id": "btype", "type": "select", "label": "क्या कराना है?", "options": ["केवाईसी (KYC) अपडेट करानी है", "खाता बंद कराना है", "एनओसी (NOC) चाहिए", "गलत राशि कटने की शिकायत है", "पासबुक अपडेट करानी है"], "required": True},
            {"id": "account_no", "type": "text", "label": "खाता संख्या", "ph": "पूरा नंबर लिखें", "required": True},
            {"id": "amount", "type": "text", "label": "कटी राशि व तारीख (वैकल्पिक — गलत कटौती हेतु)", "ph": "जैसे: ₹500, दिनांक 03/10/2026", "required": False},
            {"id": "detail", "type": "textarea", "label": "अन्य जानकारी (वैकल्पिक)", "ph": "जो भी जोड़ना हो", "required": False},
        ],
        "addressee": ["शाखा प्रबंधक महोदय", "{bank}", "शाखा — {branch}"],
        "legal": "आर.बी.आई. निर्देश — बैंक शिकायत का निपटान 30 दिन में; असंतोष होने पर बैंकिंग लोकपाल",
        "fee": "कोई शुल्क नहीं (खाता बंद कराना सामान्यतः निःशुल्क)",
        "time_limit": "शिकायत का निपटान 30 दिन में",
        "online": "बैंक ऐप / शाखा · शिकायत: cms.rbi.org.in",
        "helpline": "बैंक का टोल-फ्री नंबर",
        "attachments": ["आधार कार्ड", "पासबुक की प्रति", "संबंधित रसीद / स्टेटमेंट"],
        "subject_fn": lambda f: f"खाता संख्या {sv(f, 'account_no', 'खाता संख्या लिखें')} — {sv(f, 'btype', 'काम चुनें')}",
        "subject_en": "Request to the bank branch manager",
        "facts": [
            lambda f: f"मेरा आपकी {sv(f, 'branch', 'शाखा लिखें')} शाखा में खाता संख्या {sv(f, 'account_no', 'खाता संख्या लिखें')} है।",
            lambda f: f"{sv(f, 'btype', 'काम चुनें')}।",
            lambda f: _line(f, "amount", "{v} की राशि कटी है।"),
            lambda f: _line(f, "detail", "{v}"),
        ],
        "request": "कृपया उपरोक्त कार्यवाही शीघ्र करने की कृपा करें।",
        "tone": "business-like; account numbers exactly as given",
        "outline": ["the account and the request", "any amounts/dates relevant"],
    },
    # 11 --------------------------------------------------------------- corrections
    {
        "id": "correction",
        "emoji": "✏️",
        "label": "नाम / जन्मतिथि में सुधार (किसी दस्तावेज़ में)",
        "blurb": "जारीकर्ता प्राधिकारी · आधार: myaadhaar.uidai.gov.in (1947)",
        "style": "letter",
        "fields": personal() + [
            {"id": "doc", "type": "select", "label": "किस दस्तावेज़ में सुधार है?", "options": ["आधार कार्ड", "मतदाता पहचान पत्र", "राशन कार्ड", "विद्युत बिल", "मार्कशीट", "अन्य दस्तावेज़"], "required": True},
            {"id": "doc_no", "type": "text", "label": "दस्तावेज़ का नंबर (वैकल्पिक)", "ph": "यदि पता हो", "required": False},
            {"id": "wrong", "type": "text", "label": "अभी जो गलत लिखा है", "ph": "जैसे: नाम 'रम कुमार' लिखा है", "required": True},
            {"id": "correct", "type": "text", "label": "जो सही होना चाहिए", "ph": "जैसे: 'राम कुमार'", "required": True},
            {"id": "proof", "type": "text", "label": "सही जानकारी का सबूत क्या है? (वैकल्पिक)", "ph": "जैसे: हाईस्कूल मार्कशीट, आधार", "required": False},
        ],
        "addressee_fn": lambda f, d: {
            "आधार कार्ड": ["अधिष्ठान प्रमुख / आधार अपडेट केंद्र", f"जिला — {d} (उत्तर प्रदेश)"],
            "मतदाता पहचान पत्र": ["जिला निर्वाचन अधिकारी कार्यालय", f"जिला — {d} (उत्तर प्रदेश)"],
            "राशन कार्ड": ["जिला पूर्ति अधिकारी महोदय", "खाद्य एवं रसद नियंत्रण विभाग", f"जिला — {d} (उत्तर प्रदेश)"],
            "विद्युत बिल": ["अधिशासी अभियंता महोदय", "विद्युत वितरण खंड", f"जिला — {d} (उत्तर प्रदेश)"],
            "मार्कशीट": ["सचिव महोदय, संबंधित बोर्ड / विश्वविद्यालय", "उत्तर प्रदेश"],
        }.get(f.get("doc", ""), ["संबंधित जारीकर्ता प्राधिकारी", f"जिला — {d} (उत्तर प्रदेश)"]),
        "legal": "",
        "fee": "जन सुविधा केंद्र / कार्यालय पर जानकारी लें",
        "time_limit": "आधार अपडेट: सामान्यतः 7–15 दिन · अन्य: 15–30 दिन",
        "online": "आधार: myaadhaar.uidai.gov.in (हेल्पलाइन 1947) · मतदाता: voterportal.eci.gov.in · अन्य: संबंधित कार्यालय / जन सुविधा केंद्र",
        "helpline": "आधार 1947",
        "attachments": ["मूल दस्तावेज़ (गलत वाला)", "सही जानकारी का सबूत", "आधार कार्ड"],
        "subject_fn": lambda f: (f"{sv(f, 'doc', 'दस्तावेज़ चुनें')} (सं. {f['doc_no'].strip()}) में सुधार हेतु आवेदन" if f.get("doc_no", "").strip() else f"{sv(f, 'doc', 'दस्तावेज़ चुनें')} में सुधार हेतु आवेदन"),
        "subject_en": "Application for correction in a document",
        "facts": [
            lambda f: f"मेरे {sv(f, 'doc', 'दस्तावेज़ चुनें')} में जानकारी गलत दर्ज है — अभी '{sv(f, 'wrong', 'गलत जानकारी')}' लिखा है, जबकि सही '{sv(f, 'correct', 'सही जानकारी')}' है।",
            lambda f: _line(f, "doc_no", "दस्तावेज़ संख्या {v} है।"),
            lambda f: _line(f, "proof", "सही जानकारी का प्रमाण {v} है।"),
        ],
        "request": "कृपया उपरोक्त सुधार कराने की कृपा करें।",
        "tone": "very short; wrong vs correct must be quoted exactly",
        "outline": ["what is wrong and what it should be", "the proof that supports the correction"],
    },
    # 12 --------------------------------------------------------------- biodata
    {
        "id": "biodata",
        "emoji": "🧾",
        "label": "बायोडाटा (विवाह / नौकरी हेतु)",
        "blurb": "साफ़-सुथरा, तैयार बायोडाटा — 2 मिनट में",
        "style": "biodata",
        "fields": [
            {"id": "purpose", "type": "select", "label": "किस काम का बायोडाटा?", "options": ["विवाह हेतु बायोडाटा", "नौकरी हेतु बायोडाटा"], "required": True},
            {"id": "name", "type": "text", "label": "नाम", "ph": "पूरा नाम", "required": True},
            {"id": "dob", "type": "text", "label": "जन्म तिथि (व समय, यदि पता हो)", "ph": "जैसे: 14 अगस्त 1999, सुबह 5:20 बजे", "required": True},
            {"id": "address", "type": "text", "label": "पूरा पता", "ph": "गाँव/मोहल्ला, पोस्ट, थाना", "required": True},
            {"id": "mobile", "type": "text", "label": "मोबाइल नंबर", "ph": "संपर्क नंबर", "required": False},
            {"id": "education", "type": "textarea", "label": "शिक्षा — हर लाइन में एक (परीक्षा, बोर्ड/संस्था, वर्ष, प्रतिशत)", "ph": "जैसे:\nहाईस्कूल, यू.पी. बोर्ड, 2015, 78%\nइंटर, यू.पी. बोर्ड, 2017, 82%", "required": True},
            {"id": "work", "type": "textarea", "label": "कार्य / अनुभव / व्यवसाय (वैकल्पिक)", "ph": "जैसे: 2 वर्ष ट्यूशन पढ़ाता रहा", "required": False},
            {"id": "family", "type": "textarea", "label": "परिवार — पिता, माता, भाई-बहन (नाम व कार्य)", "ph": "जैसे:\nपिता — श्री सुरेश यादव, किसान\nमाता — श्रीमती गीता देवी, गृहिणी", "required": True},
            {"id": "extra", "type": "textarea", "label": "अन्य जानकारी (वैकल्पिक — जाति/गोत्र, रक्त समूह, रुचि…)", "ph": "जो भी जोड़ना हो, हर लाइन में एक", "required": False},
        ],
        "addressee": [],
        "legal": "",
        "fee": "",
        "time_limit": "",
        "online": "",
        "helpline": "",
        "attachments": [],
        "subject_fn": lambda f: sv(f, "purpose", "बायोडाटा"),
        "subject_en": "Bio-data",
        "facts": [],
        "request": "",
        "tone": "warm and respectful; a short introduction of the person",
        "outline": ["a 3–4 line introduction: who they are, their nature and strengths — ONLY from the given facts"],
    },
]

BY_ID: Dict[str, dict] = {m["id"]: m for m in MATTERS}


def get_matter(matter_id: str) -> dict:
    if matter_id not in BY_ID:
        raise KeyError(f"अनजान मामला: {matter_id}")
    return BY_ID[matter_id]


def addressee_lines(matter: dict, fields: Dict[str, str], district: str) -> List[str]:
    """The correct office for this matter — resolved from templates, never by the model."""
    fn: Optional[Callable] = matter.get("addressee_fn")
    if fn:
        return [ln.format(district=district, **{k: v for k, v in fields.items()}) for ln in fn(fields, district)]
    out = []
    for ln in matter.get("addressee", []):
        for key, val in fields.items():
            ln = ln.replace("{" + key + "}", val.strip() or f"[{key}]")
        out.append(ln.replace("{district}", district))
    return out


def mock_body(matter: dict, fields: Dict[str, str]) -> List[str]:
    """Deterministic narrative paragraphs used in mock mode (and as the fallback if the model fails)."""
    out = []
    for fn in matter.get("facts", []):
        try:
            s = fn(fields)
        except Exception:  # noqa: BLE001 — a template that doesn't fit must never crash a letter
            s = None
        if s and s.strip():
            out.append(s.strip())
    return out


def verify() -> None:
    """Sanity checks run by the tests."""
    ids = [m["id"] for m in MATTERS]
    assert len(ids) == len(set(ids)) == 12
    pool = {"text": 10, "textarea": 4, "select": 3}
    for m in MATTERS:
        used = {"text": 0, "textarea": 0, "select": 0}
        fids = set()
        for fld in m["fields"]:
            assert fld["type"] in pool, (m["id"], fld)
            used[fld["type"]] += 1
            assert fld["id"] not in fids, f"duplicate field {fld['id']} in {m['id']}"
            fids.add(fld["id"])
            if fld["type"] == "select":
                assert fld.get("options"), (m["id"], fld["id"])
        for t, n in used.items():
            assert n <= pool[t], f"{m['id']} uses {n} {t} fields, pool has {pool[t]}"
        if m.get("style") != "biodata":
            assert m.get("addressee") or m.get("addressee_fn"), m["id"]
            assert callable(m["subject_fn"]), m["id"]


verify()
