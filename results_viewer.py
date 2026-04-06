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
    brands_tags   = "".join(f'<span class="tag brand">{b}</span>' for b in d.get("brands_handled", []))
    areas_tags    = "".join(f'<span class="tag area">{a}</span>' for a in d.get("service_areas", []))
    missing       = d.get("missing_fields", [])
    missing_html  = (f'<div class="alert">⚠️ שדות חסרים — יש לברר בשיחה: <strong>{", ".join(missing)}</strong></div>'
                     if missing else "")
    script_html   = _md_to_html(onboarding_script)
    now           = datetime.now().strftime("%d/%m/%Y %H:%M")

    crm_data = json.dumps({
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
  <title>דוח אונבורדינג – {d.get('business_name','')}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f5f7; color: #222; }}

    /* HEADER */
    .header {{
      background: #1a1a2e;
      color: white;
      padding: 18px 48px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 3px solid #e63946;
    }}
    .header-left {{ display: flex; align-items: center; gap: 16px; }}
    .logo {{ font-size: 20px; font-weight: 800; color: #e63946; letter-spacing: -0.5px; }}
    .divider {{ color: #444; font-size: 20px; }}
    .page-title {{ font-size: 16px; font-weight: 600; color: #ddd; }}
    .header-right {{ font-size: 12px; color: #888; text-align: left; line-height: 1.8; }}
    .header-right strong {{ color: #ccc; }}

    /* TABS */
    .tabs-bar {{
      background: white;
      border-bottom: 1px solid #e0e0e0;
      padding: 0 48px;
      display: flex;
      gap: 0;
    }}
    .tab {{
      padding: 16px 28px;
      font-size: 14px;
      font-weight: 600;
      color: #888;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      transition: all 0.2s;
      user-select: none;
    }}
    .tab:hover {{ color: #1a1a2e; }}
    .tab.active {{ color: #e63946; border-bottom-color: #e63946; }}

    /* CONTENT */
    .tab-content {{ display: none; padding: 40px 48px; max-width: 860px; margin: 0 auto; }}
    .tab-content.active {{ display: block; }}

    /* CLIENT CARD */
    .section-title {{
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: #999;
      margin: 28px 0 10px;
    }}
    .section-title:first-child {{ margin-top: 0; }}
    .field-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .field {{
      background: white;
      border-radius: 8px;
      padding: 12px 16px;
      border: 1px solid #e8e8e8;
    }}
    .field .lbl {{ font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
    .field .val {{ font-size: 15px; font-weight: 600; color: #1a1a2e; }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .tag {{
      background: #f0f2f8;
      border-radius: 6px;
      padding: 5px 12px;
      font-size: 13px;
      color: #444;
      border: 1px solid #e0e2ea;
    }}
    .tag.brand {{ background: #eef4ff; color: #1d4ed8; border-color: #bfdbfe; }}
    .tag.area  {{ background: #f0fdf4; color: #166534; border-color: #bbf7d0; }}

    /* STATUS BADGE */
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #f0fdf4;
      color: #166534;
      border: 1px solid #bbf7d0;
      border-radius: 20px;
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 600;
      margin-top: 24px;
    }}

    /* ALERT */
    .alert {{
      background: #fffbeb;
      border: 1px solid #fcd34d;
      border-radius: 8px;
      padding: 12px 16px;
      font-size: 13px;
      color: #92400e;
      margin-bottom: 20px;
    }}

    /* SCRIPT */
    .md-content h3 {{
      font-size: 15px;
      font-weight: 700;
      color: #1a1a2e;
      margin: 24px 0 8px;
      padding-right: 12px;
      border-right: 3px solid #e63946;
    }}
    .md-content p, .md-content li {{
      font-size: 14px;
      line-height: 1.9;
      color: #444;
    }}
    .md-content li {{ margin-right: 20px; list-style: disc; margin-bottom: 4px; }}
    .md-content hr {{ border: none; border-top: 1px solid #eee; margin: 20px 0; }}
    .producer-note {{
      display: block;
      background: #fffbeb;
      border-right: 3px solid #f59e0b;
      padding: 7px 12px;
      margin: 8px 0;
      font-size: 13px;
      color: #78350f;
      border-radius: 0 6px 6px 0;
    }}

    /* EMAIL */
    .email-wrapper {{
      background: white;
      border-radius: 10px;
      border: 1px solid #e0e0e0;
      overflow: hidden;
    }}
    .email-meta {{
      background: #f8f9fa;
      border-bottom: 1px solid #e0e0e0;
      padding: 16px 24px;
    }}
    .email-meta-row {{ display: flex; gap: 12px; font-size: 13px; margin-bottom: 6px; }}
    .email-meta-row:last-child {{ margin-bottom: 0; }}
    .email-meta-row .lbl {{ color: #888; min-width: 50px; }}
    .email-meta-row .val {{ font-weight: 600; color: #222; }}
    .email-body {{ padding: 28px 24px; font-size: 14px; line-height: 2; color: #333; white-space: pre-wrap; }}
    .sent-badge {{
      display: inline-flex; align-items: center; gap: 6px;
      background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;
      border-radius: 20px; padding: 4px 12px; font-size: 12px; font-weight: 600;
      margin-right: 12px;
    }}

    /* CRM */
    .crm-box {{
      background: #1e1e2e;
      color: #cdd6f4;
      border-radius: 10px;
      padding: 28px;
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.8;
      white-space: pre-wrap;
      direction: ltr;
      text-align: left;
    }}
  </style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <span class="logo">zap group</span>
    <span class="divider">|</span>
    <span class="page-title">דוח אונבורדינג לקוח — {d.get('business_name','')}</span>
  </div>
  <div class="header-right">
    <div>רשומת CRM: <strong>{record_id}</strong></div>
    <div>תאריך: <strong>{now}</strong></div>
  </div>
</div>

<div class="tabs-bar">
  <div class="tab active" onclick="showTab('card')">👤 כרטיס לקוח</div>
  <div class="tab" onclick="showTab('script')">📞 תסריט אונבורדינג</div>
  <div class="tab" onclick="showTab('email')">📧 אימייל ללקוח</div>
  <div class="tab" onclick="showTab('crm')">🗃️ רשומת CRM</div>
</div>

<!-- TAB: CLIENT CARD -->
<div id="tab-card" class="tab-content active">
  {missing_html}
  <div class="section-title">פרטי עסק ובעלים</div>
  <div class="field-grid">
    <div class="field"><div class="lbl">שם העסק</div><div class="val">{d.get('business_name','—')}</div></div>
    <div class="field"><div class="lbl">בעלים</div><div class="val">{d.get('owner_name','—')}</div></div>
    <div class="field"><div class="lbl">סוג עסק</div><div class="val">{d.get('business_type','—')}</div></div>
    <div class="field"><div class="lbl">ניסיון</div><div class="val">{d.get('years_in_business','—')} שנים</div></div>
  </div>

  <div class="section-title">פרטי קשר</div>
  <div class="field-grid">
    <div class="field"><div class="lbl">טלפון</div><div class="val">{d.get('phone','—')}</div></div>
    <div class="field"><div class="lbl">טלפון נוסף</div><div class="val">{d.get('secondary_phone','—') or '—'}</div></div>
    <div class="field"><div class="lbl">אימייל</div><div class="val">{d.get('email','—')}</div></div>
    <div class="field"><div class="lbl">כתובת</div><div class="val">{d.get('address','—')}</div></div>
    <div class="field"><div class="lbl">שעות פעילות</div><div class="val">{d.get('working_hours','—') or '—'}</div></div>
    <div class="field"><div class="lbl">וואטסאפ</div><div class="val">{d.get('social_media',{}).get('whatsapp','—') or '—'}</div></div>
  </div>

  <div class="section-title">נכסים דיגיטליים</div>
  <div class="field-grid">
    <div class="field"><div class="lbl">אתר אינטרנט</div><div class="val">{d.get('website_url','—')}</div></div>
    <div class="field"><div class="lbl">דפי זהב</div><div class="val">{d.get('dapei_zahav_url','—')}</div></div>
    <div class="field"><div class="lbl">פייסבוק</div><div class="val">{d.get('social_media',{}).get('facebook','—') or '—'}</div></div>
    <div class="field"><div class="lbl">אינסטגרם</div><div class="val">{d.get('social_media',{}).get('instagram','—') or '—'}</div></div>
  </div>

  <div class="section-title">שירותים</div>
  <div class="tags">{services_tags}</div>

  <div class="section-title">מותגים</div>
  <div class="tags">{brands_tags}</div>

  <div class="section-title">אזורי פעילות</div>
  <div class="tags">{areas_tags}</div>

  <div class="status-badge">✓ לקוח חדש | ממתין לאונבורדינג</div>
</div>

<!-- TAB: ONBOARDING SCRIPT -->
<div id="tab-script" class="tab-content">
  <div class="md-content">{script_html}</div>
</div>

<!-- TAB: EMAIL -->
<div id="tab-email" class="tab-content">
  <div class="email-wrapper">
    <div class="email-meta">
      <div class="email-meta-row">
        <span class="lbl">אל</span>
        <span class="val">{d.get('email','')}</span>
        <span class="sent-badge">✓ נשלח</span>
      </div>
      <div class="email-meta-row">
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
  <div class="crm-box">{crm_data}</div>
</div>

<script>
  function showTab(name) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    event.target.classList.add('active');
  }}
</script>

</body>
</html>"""
