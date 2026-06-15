"""
streamlit_app.py — CIA DL2 Ticket Lookup
=========================================
Run locally:  streamlit run streamlit_app.py
Deploy free:  https://share.streamlit.io
"""

import streamlit as st
import sys, os, re, json, base64, ssl, datetime, collections
import urllib.request

def esc(s):
    """Escape HTML special characters."""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DL2 Ticket Lookup — Wellhub",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .stApp { background: #080c12; color: #e2e8f0; }

  /* Hide streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1100px; }

  /* Header */
  .dash-header {
    background: #0d1117; border: 1px solid #1e2d3d; border-radius: 10px;
    padding: 20px 28px; margin-bottom: 24px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .dash-header h1 { font-size: 22px; font-weight: 700; color: #e2e8f0; margin: 0 }
  .dash-header h1 em { color: #38bdf8; font-style: normal }
  .dash-header p { font-size: 12px; color: #64748b; margin: 4px 0 0 }

  /* Search box */
  .stTextInput > div > div > input {
    background: #111827 !important; border: 1px solid #1e2d3d !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
    font-family: 'DM Mono', monospace !important; font-size: 16px !important;
    padding: 12px 16px !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important; box-shadow: 0 0 0 1px #38bdf8 !important;
  }
  .stButton > button {
    background: #38bdf8 !important; color: #000 !important;
    font-weight: 700 !important; border: none !important;
    border-radius: 8px !important; padding: 12px 28px !important;
    font-size: 14px !important; width: 100%;
  }
  .stButton > button:hover { opacity: 0.85 !important }

  /* Cards */
  .card {
    background: #0d1117; border: 1px solid #1e2d3d; border-radius: 10px;
    padding: 18px 20px; margin-bottom: 14px;
  }
  .card-blue  { border-left: 3px solid #3b82f6 }
  .card-orange{ border-left: 3px solid #f97316 }
  .card-green { border-left: 3px solid #22c55e }
  .card-red   { border-left: 3px solid #ef4444 }
  .card-purple{ border-left: 3px solid #a855f7 }
  .card-accent{ border-color: #1d4ed8 }

  .card-title {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .09em; color: #64748b; margin-bottom: 10px;
  }
  .card-title.blue   { color: #38bdf8 }
  .card-title.orange { color: #f97316 }
  .card-title.green  { color: #22c55e }
  .card-title.purple { color: #a855f7 }

  /* Ticket header */
  .ticket-header {
    background: #0d1117; border: 1px solid #1e2d3d; border-radius: 10px;
    padding: 22px 24px; margin-bottom: 20px;
  }
  .ticket-key {
    font-family: 'DM Mono', monospace; font-size: 13px;
    color: #38bdf8; font-weight: 600; margin-bottom: 6px;
  }
  .ticket-summary { font-size: 20px; font-weight: 700; margin-bottom: 10px; line-height: 1.3 }
  .ticket-meta { font-size: 12px; color: #64748b }
  .ticket-meta span { color: #94a3b8; margin-right: 16px }
  .status-badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600; background: #1a2232;
    border: 1px solid #2a3347; color: #94a3b8;
  }

  /* ID chips */
  .id-chip {
    display: inline-block; background: #1a2232; border: 1px solid #2a3347;
    border-radius: 6px; padding: 3px 10px; font-family: 'DM Mono', monospace;
    font-size: 11px; color: #94a3b8; margin: 3px 4px 3px 0;
  }
  .id-chip.uuid  { color: #38bdf8; border-color: #1d4ed8 }
  .id-chip.email { color: #22c55e; border-color: #166534 }
  .id-chip.inv   { color: #f97316; border-color: #7c2d12 }

  /* Links */
  .link-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid #111827;
  }
  .link-item:last-child { border-bottom: none }
  .link-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #38bdf8; margin-top: 6px; flex-shrink: 0;
  }
  .link-label { font-size: 13px; color: #38bdf8; font-weight: 500 }
  .link-hint  { font-size: 11px; color: #475569; margin-top: 2px }

  /* Issue explanation */
  .expl-item {
    padding: 6px 0; border-bottom: 1px solid #111827;
    font-size: 12px; color: #94a3b8; display: flex; gap: 8px;
  }
  .expl-item:last-child { border-bottom: none }
  .expl-arrow { color: #38bdf8; flex-shrink: 0 }
  .expl-check { color: #22c55e; flex-shrink: 0 }

  /* Escalation box */
  .escalate-box {
    background: #1c1a10; border: 1px solid #92400e;
    border-radius: 6px; padding: 10px 14px;
    font-size: 12px; color: #fde68a; margin-top: 8px;
  }

  /* Missing info */
  .missing-item {
    padding: 5px 0; font-size: 12px; color: #94a3b8;
    border-bottom: 1px solid #111827; display: flex; gap: 8px;
  }
  .missing-item:last-child { border-bottom: none }

  /* Similar tickets */
  .similar-item {
    padding: 5px 0; font-size: 11px; color: #64748b;
    font-family: 'DM Mono', monospace; border-bottom: 1px solid #111827;
    display: flex; gap: 6px;
  }
  .similar-item:last-child { border-bottom: none }

  /* History */
  .hist-chip {
    display: inline-block; background: #111827; border: 1px solid #1e2d3d;
    border-radius: 6px; padding: 4px 10px; font-family: 'DM Mono', monospace;
    font-size: 12px; color: #38bdf8; margin: 3px; cursor: pointer;
  }
</style>
""", unsafe_allow_html=True)

# ── JIRA + ANALYSIS LOGIC ─────────────────────────────────────────────────────

JIRA_EMAIL = "nadia.franca@gympass.com"
JIRA_TOKEN = st.secrets["JIRA_TOKEN"]
JIRA_BASE  = "https://gympass.atlassian.net"

_ssl = ssl.create_default_context()
_ssl.check_hostname = False
_ssl.verify_mode    = ssl.CERT_NONE

UUID_RE  = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)
INV_RE   = re.compile(r'\b(INBR|INMX)_\d+\b', re.I)
EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b')

CLASSIFIERS = [
    (["sftp","pgp","neptune","batch","encrypt","ssh","file upload","file format"],
     "SFTP / File delivery", "CIA-Integrations"),
    (["database_wipe","threshold","wipe","removal limit"], "EF Process / Upload","CIA-Client Journey"),
    (["ef_process","ef upload","eligibility file","conflict version","relocation"], "EF Process / Upload","CIA-Client Journey"),
    (["i2s","smart invite","invitation","convite","unexpected email"], "I2S / Invitation","CIA-Subscription boosters"),
    (["sign up","sign-up","cadastro","verification code","pin"], "Sign-up / Access","CIA-Wellbeing Access"),
    (["permission","role","permissão","access denied","staff user","admin"], "Roles / Permissions","CIA-Client Journey"),
    (["report","relatório","discrepancy","divergência","mismatch"], "Report / Data access","CIA-Data & Insights"),
    (["domain","domínio","email domain"], "Email / Domain","CIA-Wellbeing Access"),
    (["capri","blocked email","suppression"], "Email / Domain","CIA-Wellbeing Access"),
    (["api ","bulk api","auto remove"], "API / Integration","CIA-Integrations"),
    (["w4c","portal","dashboard"], "W4C / Portal","CIA-Experience"),
]

ISSUE_EXPLANATIONS = {
    "SFTP / File delivery": {
        "what": "Client unable to deliver eligibility files via SFTP. Usually caused by wrong PGP format, wrong directory (/all/ vs /new/ vs /leavers/), or SSH key misconfiguration.",
        "why": ["PGP file must have .xlsx.pgp or .csv.pgp extension",
                "Wrong directory: /all/ = full replacement, /new/ = add only, /leavers/ = remove only",
                "SSH key not registered in GsFTP — client needs to provide their public key",
                "File never appears in Neptune = client-side problem, not ours"],
        "rules": ["Default wipe threshold is 10% — uploads removing more are blocked",
                  "If file doesn't appear in Neptune, the problem is on the client side"],
        "escalate": "Escalate to CIA-Integrations with batch_id and confirmed error code",
    },
    "EF Process / Upload": {
        "what": "Error during eligibility file upload in the W4C portal. Usually a conflict version, relocation attempt, or multi-entity permission issue.",
        "why": ["Conflict version: two uploads processed simultaneously",
                "CLIENT_ERROR_WITH_RELOCATIONS: known bug — generic error, no specific UI",
                "Employee being relocated between different company groups (not supported via EF)",
                "Multi-entity admin missing group-level access"],
        "rules": ["Multi-entity admins need access at BOTH entity level AND group level",
                  "Employees cannot be relocated across different company groups via EF"],
        "escalate": "Escalate to CIA-Client Journey for errors not explained by client mistakes",
    },
    "I2S / Invitation": {
        "what": "Employee received an unexpected invitation email. Smart Invites fires automatically every time the eligibility base is updated for anyone not invited in 60+ days.",
        "why": ["Base was updated (SFTP, manual upload, or API) and some employees hadn't been invited in 60+ days",
                "Smart Invites setting was enabled at some point — check Darwin settings history tab",
                "Setting may show 'off' today but was active during the triggering event"],
        "rules": ["Smart Invites fires on every base update for anyone not invited in 60 days — working as designed",
                  "If setting was toggled off after the email was sent, no recall is possible"],
        "escalate": "Escalate to CIA-Subscription Boosters if email was sent with setting confirmed OFF",
    },
    "Sign-up / Access": {
        "what": "Employee unable to complete sign-up. Usually an eligibility issue, Capri suppression block, or verification code not being received.",
        "why": ["Email is in Capri's suppression list (previously bounced)",
                "Corporate IT is blocking no-reply@gympass.com",
                "Employee not in eligibility base or status is deleted/inactive",
                "Employee already has a Staff User account — should use login, not sign-up"],
        "rules": ["If employee has Staff User account, use login flow — not sign-up",
                  "Suppression blocks can be lifted via CIA-Wellbeing Access",
                  "Metabase data has D-1 delay — ask client to try again next day if recently added"],
        "escalate": "Escalate to CIA-Wellbeing Access for suppression blocks or persistent eligibility issues",
    },
    "Roles / Permissions": {
        "what": "HR admin missing portal access. Usually a role not assigned at entity or group level in multi-entity setups.",
        "why": ["Admin missing group-level access for multi-entity company",
                "User trying to delete another admin without being in 'All Companies' view",
                "Reports section requires reports/data-analysis role — accessed via Reports menu, not Dashboard"],
        "rules": ["Multi-entity uploads require admin at BOTH entity level AND group level",
                  "To delete a group admin, user must be in 'All Companies' view"],
        "escalate": "Escalate to CIA-Client Journey if roles appear correct but access still denied",
    },
    "Report / Data access": {
        "what": "Numbers in report don't match invoice or another report. Usually caused by billing period vs calendar month confusion.",
        "why": ["Subscriber Snapshot uses calendar month; Seat Usage uses billing period",
                "GDPR/data deletion removed user identity but they still count in invoice",
                "Report has up to 2-day delay — client may be comparing stale data"],
        "rules": ["Subscriber Snapshot = calendar month — NOT for invoice reconciliation",
                  "Seat Usage by Subscribers = billing period — use this for invoice reconciliation",
                  "Reports have up to 2-day delay"],
        "escalate": "Escalate to CIA-Data & Insights if discrepancy persists after ruling out period mismatch",
    },
}

def _text(node):
    if not node: return ""
    if isinstance(node, str): return node.strip()
    parts = []
    if node.get("type") == "text" and node.get("text"):
        parts.append(node["text"])
    for c in node.get("content", []):
        t = _text(c)
        if t: parts.append(t)
    return " ".join(parts).strip()

def _field(v):
    if not v: return ""
    if isinstance(v, str): return v.strip()
    if isinstance(v, dict): return v.get("value") or v.get("name","")
    if isinstance(v, list):
        parts = []
        for x in v:
            if isinstance(x, dict): parts.append(x.get("value") or x.get("name",""))
            elif isinstance(x, str): parts.append(x)
        return ", ".join(p for p in parts if p)
    return ""

@st.cache_data(ttl=300, show_spinner=False)
def fetch_ticket(key):
    key = key.strip().upper()
    if not key.startswith("MAIN-"):
        key = f"MAIN-{key}"
    creds = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
    headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}
    fields  = ["summary","description","status","created","assignee","comment",
               "customfield_15420","customfield_17153","customfield_11059","customfield_11060","customfield_10950"]
    url = f"{JIRA_BASE}/rest/api/3/issue/{key}?fields={','.join(fields)}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45, context=_ssl) as r:
            return json.loads(r.read()), key
    except urllib.request.HTTPError as e:
        if e.code == 404: return None, key
        return None, key
    except Exception:
        return None, key

def analyze(data, key):
    f      = data.get("fields", {})
    b      = f.get("customfield_11059") or f.get("customfield_11060") or f.get("description")
    desc   = _text(b)
    summary= f.get("summary","")
    status = f.get("status",{}).get("name","")
    created= (f.get("created","") or "")[:10]
    squad  = _field(f.get("customfield_15420")) or _field(f.get("customfield_10950"))
    dl2    = _field(f.get("customfield_17153"))
    comments_raw = [_text(c.get("body","")) for c in (f.get("comment") or {}).get("comments",[])]
    comments = "\n\n---\n\n".join(comments_raw)
    full   = (summary + " " + desc + " " + comments).lower()

    # Extract IDs
    uuids  = list(dict.fromkeys(UUID_RE.findall(desc + " " + comments)))[:3]
    invs   = list(dict.fromkeys(INV_RE.findall(desc + " " + comments)))[:3]
    emails = list(dict.fromkeys(EMAIL_RE.findall(desc + " " + comments)))
    emails = [e for e in emails if "gympass" not in e.lower() and "wellhub" not in e.lower()][:3]

    # Classify
    category, squad_hint, explanation = "Other", "", {}
    for kws, cat, sq in CLASSIFIERS:
        if any(k in full for k in kws):
            category, squad_hint = cat, sq
            explanation = ISSUE_EXPLANATIONS.get(cat, {})
            break

    # Missing info
    missing = []
    if not uuids:   missing.append("Client UUID — check Darwin or ask client")
    if not emails:  missing.append("Employee email — needed for Metabase lookup")
    if len(desc) < 80: missing.append("More detail on the issue — current description is very brief")

    # Darwin links (always first if UUID found)
    cid = uuids[0] if uuids else ""
    mb_links = []
    if cid:
        mb_links += [
            ("Client Profile — Darwin", f"https://darwin.wellhub.com/clients/{cid}/profile", ""),
            ("Staff Users — Darwin", f"https://darwin.wellhub.com/clients/{cid}/staff_users", ""),
            ("Subscription — Darwin", f"https://darwin.wellhub.com/clients/{cid}/subscription", ""),
            ("Billing History — Darwin", f"https://darwin.wellhub.com/clients/{cid}/billing-platform/billing-history", ""),
        ]

    # GChat search links — via Gmail search (in:chats operator)
    ticket_search = urllib.parse.quote(f"in:chats {key}")
    mb_links += [
        ("🔍 Search ticket in GChat", f"https://mail.google.com/chat/#search/{urllib.parse.quote(key)}", "Opens Chat search for this ticket number"),
    ]
    if cid:
        mb_links += [
            ("🔍 Search client UUID in GChat", f"https://mail.google.com/chat/#search/{urllib.parse.quote(cid)}", "Opens Chat search for this client"),
        ]
    if emails:
        mb_links += [
            ("🔍 Search employee email in GChat", f"https://mail.google.com/chat/#search/{urllib.parse.quote(emails[0])}", "Opens Chat search for this employee"),
        ]

    BASE = "https://metabase.data.prd.us.gympass.cloud/question#"

    # Direct table links (Tables tab) — shown first
    mb_links += [
        ("auditlog_service.events", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywibGliL3R5cGUiOiJtYnFsL3F1ZXJ5Iiwic3RhZ2VzIjpbeyJsaWIvdHlwZSI6Im1icWwuc3RhZ2UvbWJxbCIsInNvdXJjZS10YWJsZSI6OTkxNzZ9XX0sImRpc3BsYXkiOiJ0YWJsZSIsInZpc3VhbGl6YXRpb25fc2V0dGluZ3MiOnt9fQ==", "Filter by occurred_at"),
        ("data_store_clients.client_eligibility_methods", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjo5ODE1NX19LCJkaXNwbGF5IjoidGFibGUiLCJ2aXN1YWxpemF0aW9uX3NldHRpbmdzIjp7fX0=", "Eligibility identifier and methods"),
        ("data_store_clients.eligibility_attempt_events", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMDA1NDZ9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by client_id and date"),
        ("data_store_clients.signup_verify_eligibility", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMDYyNDd9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by client_id — verification status and errors"),
        ("data_store_clients.w4c_invoice_items", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMDYzNjZ9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by client_id and start_date"),
        ("data_store_clients.w4c_historical_subscriber_seats", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMDk4NzR9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by client_id and start_date — seats per period"),
        ("data_store_clients.w4c_eligible_members", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMDYyMzZ9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "All eligibles per client with status"),
        ("data_store_clients.w4c_client_paid_subscriber_seats", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMTAzNzV9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by invoice_number"),
        ("data_store_clients.w4c_upload_batches", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMjQ4MzR9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by client_id — error_category"),
        ("data_store_clients.w4c_report_client_flexible_rate_per_eligibles", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMTUxMTJ9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by invoice_number"),
        ("satya_dimension_store.clients", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjo1NDMwOX19LCJkaXNwbGF5IjoidGFibGUiLCJ2aXN1YWxpemF0aW9uX3NldHRpbmdzIjp7fX0=", "All clients — area and cancellation reason"),
        ("satya_exploration_store.eligibility_batches", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMjQ3MzZ9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by client_id — batch error_category"),
        ("satya_exploration_store.flat_client_invoice_items", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjo3ODE0NX19LCJkaXNwbGF5IjoidGFibGUiLCJ2aXN1YWxpemF0aW9uX3NldHRpbmdzIjp7fX0=", "Filter by client_id and start_date — flat rate only"),
        ("neptune.batch", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMDA3NDJ9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by entity_id — type, status, date, errors"),
        ("neptune.diff_result", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjo5NzQ0N319LCJkaXNwbGF5IjoidGFibGUiLCJ2aXN1YWxpemF0aW9uX3NldHRpbmdzIjp7fX0=", "Filter by batch_id — what changed"),
        ("neptune.batch_row_errors", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMDE0NDN9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Filter by batch_id — exact row errors"),
        ("neptune.batch_stats", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMDA3MzB9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Newcomers, keepers, leavers, threshold"),
        ("neptune.threshold", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMTE0Mzl9fSwiZGlzcGxheSI6InRhYmxlIiwidmlzdWFsaXphdGlvbl9zZXR0aW5ncyI6e319", "Client movement limits"),
        ("snowplow.events", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywidHlwZSI6InF1ZXJ5IiwicXVlcnkiOnsic291cmNlLXRhYmxlIjoxMTg5fX0sImRpc3BsYXkiOiJ0YWJsZSIsInZpc3VhbGl6YXRpb25fc2V0dGluZ3MiOnt9fQ==", "Platform events and errors"),
    ]

    # Saved questions — shown after table links
    mb_links += [
        ("CX Eligibility V4", "https://metabase.data.prd.us.gympass.cloud/question/44902-cx-eligibility-v4", "Filter by client_id or eligible_email"),
        ("Notification Events to Recipient", "https://metabase.data.prd.us.gympass.cloud/question/38552-notification-events-to-a-recipient", "Filter by email"),
        ("Group from Staff Users W4C", "https://metabase.data.prd.us.gympass.cloud/question/43295-group-from-staff-users-w4c", "Filter by email"),
        ("Eligibles not reassociated", "https://metabase.data.prd.us.gympass.cloud/question/52579-eligibles-not-reassociated", "Filter by client_id and start_date"),
        ("Case count eligible", "https://metabase.data.prd.us.gympass.cloud/question/79398-case-count-eligible", "Eligible_unique_id increment/decrement"),
        ("Eligibles blocked to update payroll", "https://metabase.data.prd.us.gympass.cloud/question/80825-eligibles-blocked-to-update-payroll", "Filter by client_id or email"),
        ("Olympus Snowplow Events", "https://metabase.data.prd.us.gympass.cloud/question/46765-olympus-snowplow-events", "Filter by eventCategory and client"),
        ("Check-ins / User activity", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImxpYi90eXBlIjoibWJxbC9xdWVyeSIsImRhdGFiYXNlIjoxMywic3RhZ2VzIjpbeyJsaWIvdHlwZSI6Im1icWwuc3RhZ2UvbWJxbCIsInNvdXJjZS10YWJsZSI6MTA5NTI4LCJvcmRlci1ieSI6W1siZGVzYyIseyJsaWIvdXVpZCI6IjE3ZjBiNjZiLWRiOGQtNDM5OC1iMDYyLTY1NDA1OTkyZTc0OSJ9LFsiZmllbGQiLHsiZWZmZWN0aXZlLXR5cGUiOiJ0eXBlL0RhdGUiLCJsaWIvdXVpZCI6ImJiOTlhOTk3LWFjMmQtNDlkZi1iNTE1LTdhOTgzZjQwZjJiYSIsImJhc2UtdHlwZSI6InR5cGUvRGF0ZSJ9LDM3MDI3NDBdXV19XX0sImRpc3BsYXkiOiJ0YWJsZSIsInZpc3VhbGl6YXRpb25fc2V0dGluZ3MiOnt9LCJvcmlnaW5hbF9jYXJkX2lkIjpudWxsLCJ0eXBlIjoicXVlc3Rpb24ifQ==", "Filter by email and date"),
        ("Staff users table (W4C)", BASE + "eyJkYXRhc2V0X3F1ZXJ5Ijp7ImRhdGFiYXNlIjoxMywibGliL3R5cGUiOiJtYnFsL3F1ZXJ5Iiwic3RhZ2VzIjpbeyJsaWIvdHlwZSI6Im1icWwuc3RhZ2UvbWJxbCIsInNvdXJjZS10YWJsZSI6MTA3MTEyfV19LCJkaXNwbGF5IjoidGFibGUiLCJ2aXN1YWxpemF0aW9uX3NldHRpbmdzIjp7fX0=", "W4C users and admins"),
    ]

    return {
        "key": key, "summary": summary, "status": status, "created": created,
        "squad": squad, "dl2": dl2, "desc": desc, "comments": comments_raw,
        "uuids": uuids, "invs": invs, "emails": emails,
        "category": category, "squad_hint": squad_hint,
        "explanation": explanation, "missing": missing, "mb_links": mb_links,
        "url": f"{JIRA_BASE}/browse/{key}",
    }

# ── PATTERN INSIGHTS — from All Jira Tickets sheet (1SKUjbXOxsc7fB3KFq9JsZGOz6UrAWgTFiZI28hHz_vM) ──
# Counts and resolution summaries from 2,725 tickets (Jira + Zendesk, May 2025 – present)
# To refresh: paste new sheet content in the next session and I'll update these counts.

PATTERN_INSIGHTS = {
    "EF Process / Upload": {
        "count":      47,
        "squad":      "CIA-Client Journey",
        "how_solved": "Most resolved by identifying the exact error in neptune.batch — common causes: employee with no email key, 10% wipe threshold exceeded, or sheet tab name over 31 characters. Client fixes the file and re-uploads.",
        "tip":        "Always get the batch_id first. The generic error message in W4C never tells the full story — Grafana or neptune.batch_row_errors does.",
    },
    "Report / Data access": {
        "count":      42,
        "squad":      "CIA-Data & Insights",
        "how_solved": "Majority resolved by explaining the billing period vs calendar month difference. Subscriber Snapshot ≠ Seat Usage. Once shown the correct Metabase query for their billing dates, most clients confirm the numbers match.",
        "tip":        "Ask for the invoice ID and billing period dates first. Never compare numbers without knowing which period each report covers.",
    },
    "Roles / Permissions": {
        "count":      19,
        "squad":      "CIA-Client Journey",
        "how_solved": "Almost always a multi-entity setup gap — admin has entity-level access but is missing group-level access. Resolved by asking the group admin to grant the role at group level in W4C.",
        "tip":        "Check both entity and group level in the staff users Metabase query. One missing role at group level blocks all uploads.",
    },
    "SFTP / File delivery": {
        "count":      24,  # SFTP + SFTP_EF_Process combined
        "squad":      "CIA-Integrations",
        "how_solved": "Most resolved by identifying the PGP encryption format error or wrong directory in Grafana. Client corrects the file format or delivery path and re-uploads. SSH key issues require IT coordination.",
        "tip":        "Always filter Grafana by batch_id, not client_id. The file format error is logged at batch level and won't appear in client-level queries.",
    },
    "I2S / Invitation": {
        "count":      12,
        "squad":      "CIA-Subscription boosters",
        "how_solved": "Most resolved by checking Darwin settings history tab — Smart Invites was active at the time of the base update. Clients confirmed the behavior is expected once explained. No recall possible after send.",
        "tip":        "Always check the history tab in Darwin, not just the current state. The setting is often toggled off after the emails go out.",
    },
    "Sign-up / Access": {
        "count":      33,
        "squad":      "CIA-Wellbeing Access",
        "how_solved": "Split between Capri blocks (domain flagged as unsafe) and employees not yet in eligibility base. Capri cases escalated to CIA-Wellbeing Access. Eligibility gaps resolved after client updates their file.",
        "tip":        "Check Capri real-time (question 62225) before anything else — it's instant and rules out the most common cause in seconds.",
    },
    "Email / Domain": {
        "count":      8,
        "squad":      "CIA-Wellbeing Access",
        "how_solved": "Resolved by confirming the domain is not configured in Darwin or is in Capri's suppression list. Client updates employee email or IT team whitelists the Wellhub sender domain.",
        "tip":        "Ask for the exact email address the employee is using — domain mismatches are easy to spot once you have it.",
    },
    "W4C / Portal": {
        "count":      4,
        "squad":      "CIA-Experience",
        "how_solved": "Most were D-1 delay issues — data looked wrong but resolved the next day. A few were portal display bugs escalated to CIA-Experience.",
        "tip":        "Always ask the client to check again the following day before escalating. The D-1 delay explains most W4C count discrepancies.",
    },
    "API / Integration": {
        "count":      3,
        "squad":      "CIA-Integrations",
        "how_solved": "Resolved by validating the API employee ID format and checking for duplicate IDs in the client's system.",
        "tip":        "Ask for the specific API error code and the employee_id being sent. Format mismatches are the most common cause.",
    },
}

def render_insights(category):
    """Render the pattern insight card for the current issue category."""
    insight = PATTERN_INSIGHTS.get(category)
    if not insight:
        return

    count    = insight["count"]
    squad    = insight["squad"]
    solved   = insight["how_solved"]
    tip      = insight["tip"]

    st.markdown(f"""
    <div style="background:#0d1117;border:1px solid #1e3a5f;border-left:3px solid #0ea5e9;
      border-radius:8px;padding:16px 20px;margin-bottom:14px;">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
        <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#0ea5e9;">
          📊 Pattern from {count} similar tickets
        </div>
        <div style="font-size:11px;color:#475569;">→ {esc(squad)}</div>
      </div>
      <div style="font-size:12px;color:#94a3b8;line-height:1.7;margin-bottom:10px;">
        <strong style="color:#e2e8f0;">How it's usually solved:</strong> {esc(solved)}
      </div>
      <div style="background:#061926;border:1px solid #0c2d45;border-radius:6px;
        padding:8px 12px;font-size:12px;color:#38bdf8;">
        💡 <strong>Tip:</strong> {esc(tip)}
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── CASE STUDIES KNOWLEDGE BASE ──────────────────────────────────────────────
# Source: "Case Studies" Google Doc (1roLDRm1_DEpe_vSOVhcQr5oc-uBhR12Xc9jTLvQL9NY)
# To update: paste new tab content here when you add a new case to the doc.

CASE_STUDIES = [
    {
        "ticket":     "MAIN-74306",
        "title":      "INTERNAL_SERVER_ERROR on batch upload — invalid eligibility key",
        "category":   "EF Process / Upload",
        "keywords":   ["internal_server_error", "sftp", "w4c", "batch", "upload", "eligibility key",
                       "invalid eligibility key", "ef", "neptune", "eligible"],
        "summary":    (
            "Client was getting INTERNAL_SERVER_ERROR on every batch upload attempt, "
            "both via SFTP and the W4C portal. The error message was completely generic "
            "with no specific detail shown in the UI."
        ),
        "steps": [
            "Checked EF last unsuccessful files in Metabase (question 49588), filtered by client_id",
            "Checked neptune.batch table in Metabase filtered by client_id to find the failed batch and get the batch_id",
            "Searched Grafana logs filtering by batch_id, app = neptune, and the date of the upload attempt",
            "Found the real error in Grafana: 'extracting eligibility key: invalid eligibility key'",
            "Searched w4c_eligible_members table filtered by client_id and status = ELIGIBLE_HAS_NO_EMAIL",
            "Found an eligible record with no email key — root cause confirmed",
        ],
        "root_cause": (
            "One eligible record in the client's base had no email key. "
            "Neptune failed when trying to extract the eligibility key from that record, "
            "causing all uploads to fail with a generic internal server error."
        ),
        "resolution": (
            "Client fixed the eligibility file to ensure all records have a valid email address. "
            "Re-uploading after the fix resolved the issue completely."
        ),
        "gchat": "https://chat.google.com/room/AAAA2xtyA8s/9AkjJtatYII/9AkjJtatYII?cls=10",
    },
    {
        "ticket":     "MAIN-73881",
        "title":      "Payroll enabled in eligibility file but not reflecting in W4C — blocked flag",
        "category":   "EF Process / Upload",
        "keywords":   ["payroll", "payroll enabled", "folha", "payment method", "payroll update",
                       "block_eligible_to_payroll_update", "hades", "blocked", "eligible to payroll",
                       "payment", "w4c", "attribute", "flag"],
        "summary":    (
            "Client was setting 'Payroll Enabled = Yes' in their eligibility file for an employee, "
            "but the change was not reflecting in W4C — the payroll option remained disabled "
            "in the Employees tab as a payment method."
        ),
        "steps": [
            "Checked the last batches related to the employee in Metabase (diff_result table), confirmed the 'eligible_to_payroll = True' attribute was present in the batch",
            "Confirmed the most recent batch was a successful one_by_one update on 08/06",
            "Searched the employee in the Hades query (CX Eligibility V4 / question 44902), filtered by employee_id — found the payroll attribute was still False in Hades",
            "Added the field 'h.block_eligible_to_payroll_update' to the Hades query to check for the blocked flag",
            "Confirmed the employee had the block flag active — silently preventing payroll from being set to True",
            "Checked Metabase question 80825 (eligibles-blocked-to-update-payroll) filtered by client_id to see all blocked eligibles",
        ],
        "root_cause": (
            "The employee was flagged with 'block_eligible_to_payroll_update'. "
            "When this flag is active, any attempt to set payroll = True is silently ignored — "
            "the system keeps it as False without any error message to the client."
        ),
        "resolution": (
            "Escalate to CIA-Client Journey to remove the block flag for the affected employee. "
            "To identify all blocked employees for a client, use Metabase question 80825 "
            "(eligibles-blocked-to-update-payroll) filtered by client_id or email. "
            "To verify if a specific employee is blocked, add the field "
            "'h.block_eligible_to_payroll_update' to the Hades query."
        ),
        "gchat": "",
    },
]

def find_kb_matches(a):
    """Find relevant case studies for the current ticket analysis."""
    matches = []
    ticket_text = (
        a.get("category","") + " " +
        a.get("summary","") + " " +
        a.get("desc","") + " " +
        a.get("dl2","")
    ).lower()

    for case in CASE_STUDIES:
        score = 0
        # Exact ticket match
        if case["ticket"] == a.get("key",""):
            score += 10
        # Category match
        if case["category"].lower() in ticket_text or \
           a.get("category","").lower() in case["category"].lower():
            score += 4
        # Keyword match
        for kw in case["keywords"]:
            if kw.lower() in ticket_text:
                score += 1
        if score >= 3:
            matches.append((score, case))

    matches.sort(key=lambda x: -x[0])
    return [c for _, c in matches[:3]]

def render_kb(a):
    """Render the KB / case studies section."""
    matches = find_kb_matches(a)
    if not matches:
        return

    st.markdown("---")
    st.markdown("""
    <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.09em;
      color:#64748b;margin-bottom:12px;">
      📚 From your Case Studies KB — similar cases
    </div>
    """, unsafe_allow_html=True)

    for case in matches:
        steps_html = "".join(
            f'<div style="display:flex;gap:8px;padding:4px 0;border-bottom:1px solid #1a2232;font-size:12px;color:#94a3b8;">'
            f'<span style="color:#38bdf8;flex-shrink:0;">{i+1}.</span>{esc(s)}</div>'
            for i, s in enumerate(case["steps"])
        )
        gchat_html = ""
        if case.get("gchat"):
            gchat_html = f'<a href="{case["gchat"]}" target="_blank" style="font-size:11px;color:#38bdf8;">💬 View GChat discussion</a>'

        st.markdown(f"""
        <div class="card card-accent" style="margin-bottom:12px;">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px;">
            <div>
              <span style="font-family:'DM Mono',monospace;font-size:12px;font-weight:600;
                color:#38bdf8;">{esc(case['ticket'])}</span>
              <span style="font-size:11px;color:#475569;margin-left:10px;">{esc(case['category'])}</span>
            </div>
            {gchat_html}
          </div>
          <div style="font-size:13px;font-weight:600;color:#e2e8f0;margin-bottom:8px;">{esc(case['title'])}</div>
          <div style="font-size:12px;color:#94a3b8;margin-bottom:12px;line-height:1.6;">{esc(case['summary'])}</div>
          <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;
            color:#475569;margin-bottom:6px;">Steps taken</div>
          {steps_html}
          <div style="margin-top:10px;padding:8px 12px;background:#061926;border:1px solid #0e3a52;
            border-radius:6px;">
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;
              color:#0ea5e9;margin-bottom:3px;">Root cause</div>
            <div style="font-size:12px;color:#94a3b8;">{esc(case['root_cause'])}</div>
          </div>
          <div style="margin-top:8px;padding:8px 12px;background:#052e16;border:1px solid #166534;
            border-radius:6px;">
            <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;
              color:#22c55e;margin-bottom:3px;">Resolution</div>
            <div style="font-size:12px;color:#94a3b8;">{esc(case['resolution'])}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── HISTORICAL KB DATA — from All Jira Tickets sheet ─────────────────────────
# Real resolution patterns extracted from 2,725 tickets (May 2025 – present)

HISTORICAL_KB = {
    "EF Process / Upload": {
        "count": 47, "squad": "CIA-Client Journey",
        "patterns": [
            "Relocation failed because the client did not meet all conditions — employee must belong to the same company group",
            "Wrong format error on national_id — client needs to correct the field in the eligibility file",
            "Wrong format on payroll field — file column format doesn't match expected values",
            "File tab/sheet name longer than 31 characters causes internal server error",
            "Employee with no email key causes INTERNAL_SERVER_ERROR on every batch — check neptune.batch_row_errors",
            "Payroll field blocked by block_eligible_to_payroll_update flag — silently ignored without error",
        ],
        "resolution": "Client corrects the eligibility file and re-uploads. For server errors, check Grafana by batch_id for the real error message.",
    },
    "Report / Data access": {
        "count": 42, "squad": "CIA-Data & Insights",
        "patterns": [
            "Client comparing Subscriber Snapshot (calendar month) vs Seat Usage (billing period) — different periods by design",
            "Intermittent report download failure — check Grafana for the error at the time of download attempt",
            "Payroll Deduction File not received — check if email was sent to staff user via Notification Events",
            "Report shows different numbers due to GDPR anonymisation — user still counted in invoice but identity removed",
            "Employee IDs updated after billing period — not reflected in deduction file for that period (expected behavior)",
        ],
        "resolution": "Explain the billing period vs calendar month difference using Metabase seat usage query. If genuinely wrong, notify OPS for invoice correction.",
    },
    "SFTP / File delivery": {
        "count": 24, "squad": "CIA-Integrations",
        "patterns": [
            "Client sending PGP encrypted file with wrong format — must use encrypt-only flow, not sign+encrypt",
            "File blocked before reaching Neptune — error appears in Grafana but not in Metabase client queries",
            "Wrong directory used — client uploading to /all/ instead of /new/ or /leavers/",
            "SSH key not registered or wrong PGP key format — check Grafana by batch_id",
        ],
        "resolution": "Filter Grafana by batch_id (not client_id) to find the real error. Most cases: client fixes the file format or directory and re-uploads.",
    },
    "Roles / Permissions": {
        "count": 19, "squad": "CIA-Client Journey",
        "patterns": [
            "Admin missing group-level role in multi-entity setup — has entity access but not group access",
            "Intermittent permission error — check staff users Metabase query for the exact role assignments",
            "Solution rejected by client — issue escalated back to WIP for re-evaluation",
        ],
        "resolution": "Check both entity and group level in Metabase question 43295. Group admin grants the missing role at group level in W4C All Companies view.",
    },
    "I2S / Invitation": {
        "count": 12, "squad": "CIA-Subscription boosters",
        "patterns": [
            "Employee email is invalid — DNS or email status inactive, Smart Invite failed to deliver",
            "Solution rejected — issue under WIP for re-evaluation",
            "Email marked as invalid due to inactive DNS — IT team needs to verify the domain",
            "Smart Invites triggered by base update — fires for all employees not invited in 60+ days",
        ],
        "resolution": "Check Darwin settings history tab (not current state). Verify notification events for the send timestamp. Cross-reference with last base update date.",
    },
    "Sign-up / Access": {
        "count": 33, "squad": "CIA-Wellbeing Access",
        "patterns": [
            "Employee email domain flagged by Capri as unsafe — check real-time Capri query",
            "Employee not in eligibility base — D-1 delay, check again next day",
            "Staff user account already exists — employee should use login, not sign-up",
        ],
        "resolution": "Check Capri real-time (question 62225) first. Then check eligibility status. For existing staff users, redirect to login flow.",
    },
    "Email / Domain": {
        "count": 8, "squad": "CIA-Wellbeing Access",
        "patterns": [
            "Domain not configured in Darwin — employee email domain not recognised during sign-up",
            "Email in Capri suppression list — previously bounced or marked unsafe",
        ],
        "resolution": "Confirm domain configuration in Darwin. For Capri blocks, escalate to CIA-Wellbeing Access to remove the suppression.",
    },
}

def generate_explanation(a):
    """Call Claude API to generate a dynamic explanation based on ticket text + historical KB."""
    import urllib.request, json as _json

    category = a.get("category", "")
    desc     = a.get("desc", "")[:600]
    summary  = a.get("summary", "")
    dl2      = a.get("dl2", "")
    hist     = HISTORICAL_KB.get(category, {})
    patterns = hist.get("patterns", [])
    resolution = hist.get("resolution", "")
    count    = hist.get("count", 0)

    if not desc and not summary:
        return None

    patterns_text = "\n".join(f"- {p}" for p in patterns) if patterns else "No historical patterns available."

    prompt = f"""You are a Wellhub CIA DL2 support analyst. Read this ticket and produce a concise analysis.

TICKET SUMMARY: {summary}
CURRENT BEHAVIOR (from Jira): {desc}
DL2 CATEGORY: {dl2}
CLASSIFIED AS: {category}

HISTORICAL CONTEXT ({count} similar tickets in our database):
Common patterns seen in similar tickets:
{patterns_text}
Typical resolution: {resolution}

Write a short analysis (3-5 sentences) in English that:
1. Summarises what the client is experiencing in plain language (1-2 sentences)
2. Based on the historical patterns above, identifies the most likely cause for THIS specific ticket (1-2 sentences)
3. Suggests the first concrete step to investigate (1 sentence)

Be specific to this ticket. Do not use bullet points. Do not add headers. Write in plain prose."""

    try:
        payload = _json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = _json.loads(r.read())
        blocks = data.get("content", [])
        return " ".join(b.get("text","") for b in blocks if b.get("type")=="text").strip()
    except Exception:
        # Fallback: return static explanation if API fails
        expl = a.get("explanation", {})
        return expl.get("what", "") if expl else None

def render_classification(a):
    """Render data-driven classification card."""
    category  = a.get("category", "Other")
    squad_hint= a.get("squad_hint", "")
    hist      = HISTORICAL_KB.get(category, {})
    hist_squad= hist.get("squad", "")
    count     = hist.get("count", 0)

    # Use historical squad if available, fallback to classifier hint
    display_squad = hist_squad or squad_hint

    # Confidence: high if category matches historical data, medium otherwise
    confidence     = "High" if hist else "Medium"
    conf_color     = "#22c55e" if confidence == "High" else "#eab308"
    conf_bg        = "#052e16" if confidence == "High" else "#1c1308"
    conf_border    = "#166534" if confidence == "High" else "#713f12"

    hist_note = ""
    if count:
        hist_note = f'<div style="font-size:11px;color:#475569;margin-top:6px;">Based on {count} similar tickets in your historical database</div>'

    st.markdown(f"""
    <div class="card card-green">
      <div class="card-title green">🏷 Classification</div>
      <div style="margin-bottom:10px;">
        <div style="font-size:10px;color:#475569;margin-bottom:3px;">Issue category</div>
        <div style="font-size:14px;font-weight:700;color:#e2e8f0;">{esc(category)}</div>
      </div>
      {f'''<div style="margin-bottom:10px;">
        <div style="font-size:10px;color:#475569;margin-bottom:3px;">Suggested squad</div>
        <div style="font-size:13px;font-weight:600;color:#22c55e;">{esc(display_squad)}</div>
      </div>''' if display_squad else ''}
      <div style="display:inline-block;background:{conf_bg};border:1px solid {conf_border};
        border-radius:20px;padding:3px 10px;font-size:10px;font-weight:700;
        letter-spacing:.07em;color:{conf_color};margin-top:4px;">
        {confidence} confidence
      </div>
      {hist_note}
    </div>
    """, unsafe_allow_html=True)

# ── RENDER ────────────────────────────────────────────────────────────────────

def render_result(a):
    # Ticket header
    st.markdown(f"""
    <div class="ticket-header">
      <div class="ticket-key">
        <a href="{a['url']}" target="_blank" style="color:#38bdf8;text-decoration:none;">
          🔗 {a['key']}
        </a>
      </div>
      <div class="ticket-summary">{a['summary']}</div>
      <div class="ticket-meta">
        <span class="status-badge">{a['status']}</span>
        <span>📅 {a['created']}</span>
        {"<span>🏷 " + a['squad'] + "</span>" if a['squad'] else ""}
        {"<span>📌 " + a['dl2'] + "</span>" if a['dl2'] else ""}
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        # Description
        if a["desc"]:
            st.markdown('<div class="card card-blue"><div class="card-title blue">📋 Current behavior</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:13px;color:#94a3b8;line-height:1.7;">{a["desc"][:800]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Extracted IDs
        id_html = '<div class="card card-orange"><div class="card-title orange">🔍 Extracted identifiers</div>'
        if a["uuids"]:
            for uid in a["uuids"]:
                id_html += f'<span class="id-chip uuid">UUID: {uid}</span>'
        if a["invs"]:
            for inv in a["invs"]:
                id_html += f'<span class="id-chip inv">INV: {inv}</span>'
        if a["emails"]:
            for em in a["emails"]:
                id_html += f'<span class="id-chip email">✉ {em}</span>'
        if not any([a["uuids"], a["invs"], a["emails"]]):
            id_html += '<span style="color:#475569;font-size:12px;">No identifiers found in ticket text</span>'
        id_html += '</div>'
        st.markdown(id_html, unsafe_allow_html=True)

        # Issue explanation — dynamic, generated from ticket text + historical KB
        with st.spinner("Analysing issue..."):
            dynamic_expl = generate_explanation(a)
        if dynamic_expl:
            st.markdown(f"""
            <div class="card card-accent">
              <div class="card-title blue">📖 Issue explanation — {esc(a['category'])}</div>
              <div style="font-size:13px;color:#94a3b8;line-height:1.8;">{dynamic_expl}</div>
            </div>
            """, unsafe_allow_html=True)

        # Comments
        if a["comments"]:
            with st.expander(f"💬 Comments ({len(a['comments'])})"):
                for i, c in enumerate(a["comments"], 1):
                    st.markdown(f"**Comment {i}**")
                    st.markdown(f'<div style="font-size:12px;color:#94a3b8;line-height:1.6;background:#0d1117;border:1px solid #1e2d3d;border-radius:6px;padding:10px;margin-bottom:8px;">{c[:500]}</div>', unsafe_allow_html=True)

    with col2:
        # Metabase + Darwin links
        if a["mb_links"]:
            st.markdown('<div class="card card-purple"><div class="card-title purple">🔗 Metabase & Darwin links</div>', unsafe_allow_html=True)
            for label, url, hint in a["mb_links"]:
                st.markdown(f"""
                <div class="link-item">
                  <div class="link-dot"></div>
                  <div>
                    <div class="link-label"><a href="{url}" target="_blank" style="color:#38bdf8;">{label}</a></div>
                    {f'<div class="link-hint">{hint}</div>' if hint else ''}
                  </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Missing info
        if a["missing"]:
            st.markdown('<div class="card card-red"><div class="card-title" style="color:#ef4444;">⚠ Missing info — request from client</div>', unsafe_allow_html=True)
            missing_html = "".join(f'<div class="missing-item"><span style="color:#ef4444;">⚠</span>{m}</div>' for m in a["missing"])
            st.markdown(missing_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Classification card — data-driven
        render_classification(a)

    # Pattern insights card
    render_insights(a["category"])

    # Case studies KB
    render_kb(a)

# ── MAIN APP ──────────────────────────────────────────────────────────────────

def main():
    # Header
    st.markdown("""
    <div class="dash-header">
      <div>
        <h1>DL2 <em>Ticket Lookup</em></h1>
        <p>Wellhub · CIA Support · Live Jira analysis</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Search input
    col_inp, col_btn = st.columns([5, 1])
    with col_inp:
        ticket_input = st.text_input(
            "Ticket number",
            placeholder="72589  or  MAIN-72589",
            label_visibility="collapsed",
            key="ticket_input",
        )
    with col_btn:
        search = st.button("Look up →", use_container_width=True)

    # Trigger on Enter or button click
    if search or (ticket_input and ticket_input != st.session_state.get("last_lookup","")):
        if ticket_input.strip():
            st.session_state["last_lookup"] = ticket_input.strip()

            with st.spinner(f"Fetching {ticket_input.strip().upper()}…"):
                data, key = fetch_ticket(ticket_input.strip())

            if data is None:
                st.error(f"❌ Ticket **{key}** not found in Jira. Check the ticket number and try again.")
            else:
                # Save to history
                hist = st.session_state.get("history", [])
                if key not in hist:
                    hist.insert(0, key)
                    st.session_state["history"] = hist[:8]

                a = analyze(data, key)
                st.divider()
                render_result(a)

    # History chips
    hist = st.session_state.get("history", [])
    if hist:
        st.markdown("---")
        st.markdown("**Recent lookups**")
        cols = st.columns(min(len(hist), 8))
        for i, h in enumerate(hist):
            with cols[i]:
                if st.button(h, key=f"hist_{h}"):
                    st.session_state["ticket_input"] = h
                    st.rerun()

if __name__ == "__main__":
    main()