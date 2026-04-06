"""
Generates a visual HTML results page and opens it in the browser.
Called automatically at the end of main.py after the pipeline completes.
"""

import json
import os
import webbrowser
from datetime import datetime


def generate_and_open(client_data: dict, client_card: str, onboarding_script: str, record_id: str):
    html = _build_html(client_data, client_card, onboarding_script, record_id)
    path = os.path.abspath("output/results.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(f"file://{path}")


def _md_to_html(text: str) -> str:
    import re
    lines = text.splitlines()
    out = []
    for line in lines:
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        line = re.sub(r'\[הנחיות למפיק:?\s*([^\]]+)\]',
                      r'<span class="producer-note">📋 \1</span>', line)
        if line.startswith("## "):
            out.append(f'<h3>{line[3:]}</h3>')
        elif line.startswith("# "):
            out.append(f'<h2>{line[2:]}</h2>')
        elif line.startswith("- ") or line.startswith("* "):
            out.append(f'<li>{line[2:]}</li>')
        elif line.strip() == "---":
            out.append('<hr>')
        elif line.strip():
            out.append(f'<p>{line}</p>')
    return "\n".join(out)


def _build_html(client_data: dict, client_card: str, onboarding_script: str, record_id: str) -> str:
    d = client_data
    services_tags = "".join(f'<span class="tag">{s}</span>' for s in d.get("services", []))
    brands_tags   = "".join(f'<span class="tag tag-blue">{b}</span>' for b in d.get("brands_handled", []))
    areas_tags    = "".join(f'<span class="tag tag-green">{a}</span>' for a in d.get("service_areas", []))
    missing       = d.get("missing_fields", [])
    missing_html  = (f'<div class="alert">⚠️ שדות חסרים — יש לברר בשיחה: <strong>{", ".join(missing)}</strong></div>'
                     if missing else "")
    script_html   = _md_to_html(onboarding_script)
    now           = datetime.now().strftime("%d/%m/%Y %H:%M")
    sm            = d.get("social_media") or {}
    whatsapp      = sm.get("whatsapp") or "—"
    facebook      = sm.get("facebook") or "—"
    instagram     = sm.get("instagram") or "—"

    crm_json = json.dumps({
        "record_id": record_id,
        "status": "onboarding_email_sent",
        "created_at": now,
        "business_name": d.get('business_name'),
        "owner": d.get('owner_name'),
        "phone": d.get('phone'),
        "email": d.get('email'),
        "city": d.get('city'),
        "services": d.get('services'),
        "brands_handled": d.get('brands_handled'),
        "service_areas": d.get('service_areas'),
    }, ensure_ascii=False, indent=2)

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>דוח אונבורדינג – {d.get('business_name','')}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:       #0f1117;
      --surface:  #1a1d27;
      --surface2: #22263a;
      --border:   #2e3347;
      --accent:   #e63946;
      --accent2:  #ff6b6b;
      --text:     #e8eaf0;
      --muted:    #7b82a0;
      --green:    #22c55e;
      --blue:     #60a5fa;
      --gold:     #f59e0b;
    }}

    body {{
      font-family: 'Heebo', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
    }}

    /* ── TOPBAR ── */
    .topbar {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 48px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 64px;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .topbar-left {{ display: flex; align-items: center; gap: 20px; }}
    .logo {{
      font-size: 18px;
      font-weight: 800;
      color: var(--accent);
      letter-spacing: 1px;
      text-transform: lowercase;
    }}
    .sep {{ width: 1px; height: 24px; background: var(--border); }}
    .page-title {{ font-size: 14px; font-weight: 500; color: var(--muted); }}
    .topbar-right {{ display: flex; align-items: center; gap: 16px; }}
    .crm-id {{
      font-size: 11px;
      font-weight: 600;
      color: var(--muted);
      background: var(--surface2);
      border: 1px solid var(--border);
      padding: 5px 12px;
      border-radius: 6px;
      letter-spacing: 0.5px;
    }}
    .status-pill {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(34, 197, 94, 0.12);
      border: 1px solid rgba(34, 197, 94, 0.3);
      color: var(--green);
      font-size: 12px;
      font-weight: 600;
      padding: 5px 14px;
      border-radius: 20px;
    }}
    .dot {{
      width: 7px; height: 7px;
      background: var(--green);
      border-radius: 50%;
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.4; }}
    }}

    /* ── TABS ── */
    .tabs-bar {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 48px;
      display: flex;
      gap: 4px;
    }}
    .tab {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 14px 20px;
      font-size: 13px;
      font-weight: 600;
      color: var(--muted);
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.18s;
      user-select: none;
      white-space: nowrap;
    }}
    .tab:hover {{ color: var(--text); }}
    .tab.active {{ color: var(--text); border-bottom-color: var(--accent); }}
    .tab-icon {{ font-size: 15px; }}

    /* ── CONTENT ── */
    .tab-content {{ display: none; padding: 36px 48px; max-width: 900px; margin: 0 auto; }}
    .tab-content.active {{ display: block; }}

    /* ── SECTION LABEL ── */
    .section-label {{
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 1.2px;
      text-transform: uppercase;
      color: var(--muted);
      margin: 28px 0 10px;
    }}
    .section-label:first-child {{ margin-top: 0; }}

    /* ── FIELD GRID ── */
    .field-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
    .field {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 16px;
      transition: border-color 0.15s;
    }}
    .field:hover {{ border-color: #3e4460; }}
    .field .lbl {{
      font-size: 10px;
      font-weight: 600;
      letter-spacing: 0.8px;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 5px;
    }}
    .field .val {{
      font-size: 14px;
      font-weight: 500;
      color: var(--text);
    }}

    /* ── TAGS ── */
    .tags {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .tag {{
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 5px 13px;
      font-size: 12px;
      font-weight: 500;
      color: var(--text);
    }}
    .tag-blue {{
      background: rgba(96, 165, 250, 0.1);
      border-color: rgba(96, 165, 250, 0.25);
      color: var(--blue);
    }}
    .tag-green {{
      background: rgba(34, 197, 94, 0.1);
      border-color: rgba(34, 197, 94, 0.25);
      color: var(--green);
    }}

    /* ── STATUS ── */
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(34, 197, 94, 0.1);
      border: 1px solid rgba(34, 197, 94, 0.3);
      color: var(--green);
      border-radius: 20px;
      padding: 8px 18px;
      font-size: 13px;
      font-weight: 600;
      margin-top: 28px;
    }}

    /* ── ALERT ── */
    .alert {{
      background: rgba(245, 158, 11, 0.1);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 10px;
      padding: 12px 16px;
      font-size: 13px;
      color: var(--gold);
      margin-bottom: 20px;
    }}

    /* ── SCRIPT ── */
    .md-content h3 {{
      font-size: 14px;
      font-weight: 700;
      color: var(--text);
      margin: 28px 0 10px;
      padding-right: 12px;
      border-right: 2px solid var(--accent);
    }}
    .md-content p, .md-content li {{
      font-size: 14px;
      line-height: 1.9;
      color: #a8aec8;
    }}
    .md-content li {{ margin-right: 20px; list-style: disc; margin-bottom: 4px; }}
    .md-content hr {{ border: none; border-top: 1px solid var(--border); margin: 24px 0; }}
    .producer-note {{
      display: block;
      background: rgba(245, 158, 11, 0.08);
      border-right: 2px solid var(--gold);
      padding: 8px 14px;
      margin: 10px 0;
      font-size: 12px;
      color: #d4a017;
      border-radius: 0 8px 8px 0;
    }}

    /* ── EMAIL ── */
    .email-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
    }}
    .email-header {{
      background: var(--surface2);
      border-bottom: 1px solid var(--border);
      padding: 20px 28px;
    }}
    .email-row {{
      display: flex;
      align-items: baseline;
      gap: 14px;
      font-size: 13px;
      margin-bottom: 10px;
    }}
    .email-row:last-child {{ margin-bottom: 0; }}
    .email-row .lbl {{ color: var(--muted); min-width: 48px; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }}
    .email-row .val {{ color: var(--text); font-weight: 500; }}
    .sent-pill {{
      display: inline-flex; align-items: center; gap: 5px;
      background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.25);
      color: var(--green); border-radius: 12px; padding: 3px 10px;
      font-size: 11px; font-weight: 600;
    }}
    .email-body {{
      padding: 32px 28px;
      font-size: 14px;
      line-height: 2.1;
      color: #a8aec8;
      white-space: pre-wrap;
    }}

    /* ── CRM ── */
    .crm-card {{
      background: #0d1117;
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
    }}
    .crm-titlebar {{
      background: var(--surface2);
      border-bottom: 1px solid var(--border);
      padding: 12px 20px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .crm-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    .crm-code {{
      padding: 24px 28px;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.9;
      white-space: pre-wrap;
      direction: ltr;
      text-align: left;
      color: #8b949e;
    }}
    .crm-code .key   {{ color: #79b8ff; }}
    .crm-code .str   {{ color: #9ecbff; }}
    .crm-code .num   {{ color: #f8c555; }}
    .crm-code .null  {{ color: #f97583; }}
    .crm-code .bool  {{ color: #79b8ff; }}

    /* ── DIVIDER ── */
    hr.light {{ border: none; border-top: 1px solid var(--border); margin: 24px 0; }}
  </style>
</head>
<body>

<!-- TOPBAR -->
<div class="topbar">
  <div class="topbar-left">
    <span class="logo">zap group</span>
    <div class="sep"></div>
    <span class="page-title">דוח אונבורדינג — {d.get('business_name','')}</span>
  </div>
  <div class="topbar-right">
    <span class="crm-id">{record_id}</span>
    <span class="status-pill"><span class="dot"></span>הכנות הושלמו | ממתין לשיחה</span>
  </div>
</div>

<!-- TABS -->
<div class="tabs-bar">
  <div class="tab active" onclick="showTab('card', this)"><span class="tab-icon">👤</span>כרטיס לקוח</div>
  <div class="tab" onclick="showTab('script', this)"><span class="tab-icon">📞</span>תסריט אונבורדינג</div>
  <div class="tab" onclick="showTab('email', this)"><span class="tab-icon">📧</span>אימייל ללקוח</div>
  <div class="tab" onclick="showTab('crm', this)"><span class="tab-icon">🗃️</span>רשומת CRM</div>
</div>

<!-- TAB: CARD -->
<div id="tab-card" class="tab-content active">
  {missing_html}

  <div class="section-label">פרטי עסק ובעלים</div>
  <div class="field-grid">
    <div class="field"><div class="lbl">שם העסק</div><div class="val">{d.get('business_name','—')}</div></div>
    <div class="field"><div class="lbl">בעלים</div><div class="val">{d.get('owner_name','—')}</div></div>
    <div class="field"><div class="lbl">סוג עסק</div><div class="val">{d.get('business_type','—')}</div></div>
    <div class="field"><div class="lbl">ניסיון</div><div class="val">{d.get('years_in_business','—')} שנים</div></div>
  </div>

  <div class="section-label">פרטי קשר</div>
  <div class="field-grid">
    <div class="field"><div class="lbl">טלפון</div><div class="val">{d.get('phone','—')}</div></div>
    <div class="field"><div class="lbl">טלפון נוסף</div><div class="val">{d.get('secondary_phone') or '—'}</div></div>
    <div class="field"><div class="lbl">אימייל</div><div class="val">{d.get('email','—')}</div></div>
    <div class="field"><div class="lbl">כתובת</div><div class="val">{d.get('address','—')}</div></div>
    <div class="field"><div class="lbl">שעות פעילות</div><div class="val">{d.get('working_hours') or '—'}</div></div>
    <div class="field"><div class="lbl">וואטסאפ</div><div class="val">{whatsapp}</div></div>
  </div>

  <div class="section-label">נכסים דיגיטליים</div>
  <div class="field-grid">
    <div class="field"><div class="lbl">אתר אינטרנט</div><div class="val">{d.get('website_url','—')}</div></div>
    <div class="field"><div class="lbl">דפי זהב</div><div class="val">{d.get('dapei_zahav_url','—')}</div></div>
    <div class="field"><div class="lbl">פייסבוק</div><div class="val">{facebook}</div></div>
    <div class="field"><div class="lbl">אינסטגרם</div><div class="val">{instagram}</div></div>
  </div>

  <div class="section-label">שירותים</div>
  <div class="tags">{services_tags}</div>

  <div class="section-label">מותגים</div>
  <div class="tags">{brands_tags}</div>

  <div class="section-label">אזורי פעילות</div>
  <div class="tags">{areas_tags}</div>

  <div class="status-badge">✓ לקוח חדש | ממתין לאונבורדינג</div>
</div>

<!-- TAB: SCRIPT -->
<div id="tab-script" class="tab-content">
  <div class="md-content">{script_html}</div>
</div>

<!-- TAB: EMAIL -->
<div id="tab-email" class="tab-content">
  <div class="email-card">
    <div class="email-header">
      <div class="email-row">
        <span class="lbl">אל</span>
        <span class="val">{d.get('email','')}</span>
        <span class="sent-pill">✓ נשלח</span>
      </div>
      <div class="email-row">
        <span class="lbl">נושא</span>
        <span class="val">ברוכים הבאים לזאפ! הכל מוכן לתחילת הקמת {d.get('business_name','')} 🚀</span>
      </div>
    </div>
    <div class="email-body">שלום {d.get('owner_name', d.get('business_name',''))},

ברוכים הבאים למשפחת זאפ! אנחנו שמחים שבחרתם בנו לניהול הנוכחות הדיגיטלית של {d.get('business_name','')}.

החבילה שרכשתם כוללת:
✓ אתר אינטרנט מקצועי בן 5 עמודים
✓ מיניסייט מוביל בדפי זהב באזור {d.get('region') or d.get('city','')}

מה הלאה?
אחד מנציגינו ייצור איתכם קשר בקרוב לשיחת היכרות קצרה שבה נתאם את כל הפרטים.

לשאלות ותיאום מהיר: info@zapgroup.co.il | 1-700-XXX-XXX

בברכה,
צוות זאפ גרופ</div>
  </div>
</div>

<!-- TAB: CRM -->
<div id="tab-crm" class="tab-content">
  <div class="crm-card">
    <div class="crm-titlebar">
      <div class="crm-dot" style="background:#ff5f56"></div>
      <div class="crm-dot" style="background:#ffbd2e"></div>
      <div class="crm-dot" style="background:#27c93f"></div>
    </div>
    <div class="crm-code" id="crm-code"></div>
  </div>
</div>

<script>
  const CRM_DATA = {json.dumps(crm_json)};

  function syntaxHighlight(json) {{
    return json
      .replace(/("(\\u[a-zA-Z0-9]{{4}}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {{
        let cls = 'num';
        if (/^"/.test(match)) {{
          if (/:$/.test(match)) cls = 'key';
          else cls = 'str';
        }} else if (/true|false/.test(match)) cls = 'bool';
        else if (/null/.test(match)) cls = 'null';
        return '<span class="' + cls + '">' + match + '</span>';
      }});
  }}

  document.getElementById('crm-code').innerHTML = syntaxHighlight(CRM_DATA);

  function showTab(name, el) {{
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    el.classList.add('active');
  }}
</script>

</body>
</html>"""
