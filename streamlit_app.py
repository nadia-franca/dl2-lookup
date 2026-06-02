"""
streamlit_app.py — CIA DL2 Ticket Lookup
=========================================
Run locally:  streamlit run streamlit_app.py
Deploy free:  https://share.streamlit.io
"""
 
import streamlit as st
import sys, os, re, json, base64, ssl, datetime, collections
import urllib.request
 
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
    b      = f.get("customfield_11060") or f.get("customfield_11059") or f.get("description")
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
 
    # Metabase links — no pre-filled filters, open directly
    cid = uuids[0] if uuids else ""
    mb_links = []
    if cid:
        mb_links += [
            ("Client Profile — Darwin", f"https://darwin.wellhub.com/clients/{cid}/profile", ""),
            ("Staff Users — Darwin", f"https://darwin.wellhub.com/clients/{cid}/staff_users", ""),
            ("Subscription — Darwin", f"https://darwin.wellhub.com/clients/{cid}/subscription", ""),
            ("Billing History — Darwin", f"https://darwin.wellhub.com/clients/{cid}/billing-platform/billing-history", ""),
        ]
 
    # Metabase saved questions — open directly, filter manually inside
    mb_links += [
        ("CX Eligibility V4", "https://metabase.us.gympass.cloud/question/44902-cx-eligibility-v4", "Filter by client_id or employee email"),
        ("Notification Events", "https://metabase.us.gympass.cloud/question/44903", "Filter by employee email"),
        ("Neptune Batches Overview", "https://metabase.us.gympass.cloud/question/45100", "Filter by client_id"),
        ("EF Last 30 Client-Side Errors", "https://metabase.us.gympass.cloud/question/44901", "Filter by client_id"),
        ("EF Check Updated and Created", "https://metabase.us.gympass.cloud/question/44900", "Filter by client_id"),
        ("WH Details / Seat Usage", "https://metabase.us.gympass.cloud/question/44905", "Filter by client_id and billing period"),
        ("Group from Staff Users W4C", "https://metabase.us.gympass.cloud/question/44907", "Filter by email"),
    ]
 
    return {
        "key": key, "summary": summary, "status": status, "created": created,
        "squad": squad, "dl2": dl2, "desc": desc, "comments": comments_raw,
        "uuids": uuids, "invs": invs, "emails": emails,
        "category": category, "squad_hint": squad_hint,
        "explanation": explanation, "missing": missing, "mb_links": mb_links,
        "url": f"{JIRA_BASE}/browse/{key}",
    }
 
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
            st.markdown('<div class="card card-blue"><div class="card-title blue">📋 Issue description</div>', unsafe_allow_html=True)
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
 
        # Issue explanation
        expl = a["explanation"]
        if expl:
            st.markdown(f"""
            <div class="card card-accent">
              <div class="card-title blue">📖 Issue explanation — {a['category']}</div>
              <div style="font-size:13px;color:#94a3b8;line-height:1.7;margin-bottom:12px;">{expl.get('what','')}</div>
            """, unsafe_allow_html=True)
            if expl.get("why"):
                st.markdown('<div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:#475569;margin-bottom:6px;">Why this happens</div>', unsafe_allow_html=True)
                why_html = "".join(f'<div class="expl-item"><span class="expl-arrow">→</span>{w}</div>' for w in expl["why"])
                st.markdown(why_html, unsafe_allow_html=True)
            if expl.get("rules"):
                st.markdown('<div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:#475569;margin:10px 0 6px;">Key rules</div>', unsafe_allow_html=True)
                rules_html = "".join(f'<div class="expl-item"><span class="expl-check">✓</span>{r}</div>' for r in expl["rules"])
                st.markdown(rules_html, unsafe_allow_html=True)
            if expl.get("escalate"):
                st.markdown(f'<div class="escalate-box"><strong>When to escalate:</strong> {expl["escalate"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
 
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
 
        # Category + squad
        st.markdown(f"""
        <div class="card card-green">
          <div class="card-title green">🏷 Classification</div>
          <div style="margin-bottom:8px;">
            <div style="font-size:10px;color:#475569;margin-bottom:3px;">Category</div>
            <div style="font-size:13px;font-weight:600;color:#e2e8f0;">{a['category']}</div>
          </div>
          {f'<div><div style="font-size:10px;color:#475569;margin-bottom:3px;">Suggested squad</div><div style="font-size:13px;font-weight:600;color:#22c55e;">{a["squad_hint"]}</div></div>' if a["squad_hint"] else ''}
        </div>
        """, unsafe_allow_html=True)
 
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