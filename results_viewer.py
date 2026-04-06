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
    """Minimal markdown → HTML converter."""
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

    card_html   = _md_to_html(client_card)
    script_html = _md_to_html(onboarding_script)
    now         = datetime.now().strftime("%d/%m/%Y %H:%M")

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>תוצאות אונבורדינג – {d.get('business_name','')}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f8; color: #222; }}

    /* TOP BAR */
    .topbar {{ background: #1a1a2e; color: white; padding: 14px 40px;
               display: flex; justify-content: space-between; align-items: center; }}
    .topbar .logo {{ font-size: 22px; font-weight: 800; color: #e63946; }}
    .topbar .meta {{ font-size: 13px; color: #aaa; }}
    .badge {{ background: #e63946; color: white; font-size: 12px; font-weight: 700;
              padding: 4px 12px; border-radius: 20px; margin-right: 10px; }}
    .badge.success {{ background: #2ecc71; }}

    /* LAYOUT */
    .container {{ max-width: 1100px; margin: 30px auto; padding: 0 20px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
    .full {{ grid-column: 1 / -1; }}

    /* CARDS */
    .card {{ background: white; border-radius: 14px; box-shadow: 0 2px 12px rgba(0,0,0,.08);
             overflow: hidden; }}
    .card-header {{ padding: 16px 24px; background: #1a1a2e; color: white;
                    display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 16px; }}
    .card-header .icon {{ font-size: 20px; }}
    .card-body {{ padding: 24px; }}

    /* SUMMARY ROW */
    .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }}
    .stat-box {{ background: white; border-radius: 12px; padding: 20px; text-align: center;
                 box-shadow: 0 2px 10px rgba(0,0,0,.07); }}
    .stat-box .num {{ font-size: 28px; font-weight: 800; color: #e63946; }}
    .stat-box .lbl {{ font-size: 13px; color: #888; margin-top: 4px; }}

    /* DATA ROWS */
    .row {{ display: flex; padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; }}
    .row:last-child {{ border-bottom: none; }}
    .row .lbl {{ color: #888; min-width: 120px; }}
    .row .val {{ font-weight: 600; color: #222; }}

    /* TAGS */
    .tags {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
    .tag {{ background: #f0f2f8; border-radius: 6px; padding: 4px 12px; font-size: 13px; }}
    .tag.brand {{ background: #e8f4fd; color: #1565c0; }}
    .tag.area  {{ background: #e8f5e9; color: #2e7d32; }}

    /* MARKDOWN CONTENT */
    .md-content h2 {{ font-size: 18px; color: #1a1a2e; margin: 20px 0 8px;
                      border-right: 3px solid #e63946; padding-right: 10px; }}
    .md-content h3 {{ font-size: 15px; color: #333; margin: 16px 0 6px; }}
    .md-content p, .md-content li {{ font-size: 14px; line-height: 1.8; color: #444; }}
    .md-content li {{ margin-right: 16px; list-style: disc; }}
    .md-content hr {{ border: none; border-top: 1px solid #eee; margin: 16px 0; }}
    .producer-note {{ display: block; background: #fff8e1; border-right: 3px solid #ffc107;
                      padding: 6px 12px; margin: 6px 0; font-size: 13px; color: #7a5c00; border-radius: 4px; }}

    /* ALERT */
    .alert {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px;
              padding: 12px 16px; margin-bottom: 16px; font-size: 14px; color: #856404; }}

    /* CRM */
    .crm-record {{ background: #1e1e2e; color: #cdd6f4; border-radius: 10px;
                   padding: 20px; font-family: monospace; font-size: 13px;
                   line-height: 1.7; white-space: pre-wrap; }}

    /* EMAIL */
    .email-box {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; padding: 20px; }}
    .email-meta {{ font-size: 13px; color: #666; border-bottom: 1px solid #ddd;
                   padding-bottom: 12px; margin-bottom: 14px; }}
    .email-meta span {{ font-weight: 700; color: #333; }}
    .email-body {{ font-size: 14px; line-height: 1.9; white-space: pre-wrap; }}
  </style>
</head>
<body>

<div class="topbar">
  <div class="logo">❄ zap group <span class="badge success">✓ אונבורדינג הושלם</span></div>
  <div class="meta">רשומת CRM: <strong>{record_id}</strong> &nbsp;|&nbsp; {now}</div>
</div>

<div class="container">

  <!-- SUMMARY STATS -->
  <div class="summary">
    <div class="stat-box"><div class="num">{d.get('years_in_business','?')}</div><div class="lbl">שנות ניסיון</div></div>
    <div class="stat-box"><div class="num">{len(d.get('services',[]))}</div><div class="lbl">שירותים זוהו</div></div>
    <div class="stat-box"><div class="num">{len(d.get('brands_handled',[]))}</div><div class="lbl">מותגים</div></div>
    <div class="stat-box"><div class="num">{len(d.get('service_areas',[]))}</div><div class="lbl">אזורי פעילות</div></div>
  </div>

  <div class="grid">

    <!-- CLIENT CARD -->
    <div class="card">
      <div class="card-header"><span class="icon">👤</span> כרטיס לקוח</div>
      <div class="card-body">
        {missing_html}
        <div class="row"><span class="lbl">שם העסק</span><span class="val">{d.get('business_name','')}</span></div>
        <div class="row"><span class="lbl">בעלים</span><span class="val">{d.get('owner_name','')}</span></div>
        <div class="row"><span class="lbl">סוג עסק</span><span class="val">{d.get('business_type','')}</span></div>
        <div class="row"><span class="lbl">טלפון</span><span class="val">{d.get('phone','')}</span></div>
        <div class="row"><span class="lbl">טלפון נוסף</span><span class="val">{d.get('secondary_phone','') or '—'}</span></div>
        <div class="row"><span class="lbl">אימייל</span><span class="val">{d.get('email','')}</span></div>
        <div class="row"><span class="lbl">כתובת</span><span class="val">{d.get('address','')}</span></div>
        <div class="row"><span class="lbl">שעות פעילות</span><span class="val">{d.get('working_hours','') or '—'}</span></div>
        <div class="row"><span class="lbl">אתר</span><span class="val">{d.get('website_url','')}</span></div>
        <div class="row"><span class="lbl">דפי זהב</span><span class="val">{d.get('dapei_zahav_url','')}</span></div>
        <br>
        <strong style="font-size:13px;color:#888;">שירותים</strong>
        <div class="tags">{services_tags}</div>
        <br>
        <strong style="font-size:13px;color:#888;">מותגים</strong>
        <div class="tags">{brands_tags}</div>
        <br>
        <strong style="font-size:13px;color:#888;">אזורי פעילות</strong>
        <div class="tags">{areas_tags}</div>
      </div>
    </div>

    <!-- ONBOARDING SCRIPT -->
    <div class="card">
      <div class="card-header"><span class="icon">📞</span> תסריט שיחת אונבורדינג</div>
      <div class="card-body md-content">{script_html}</div>
    </div>

    <!-- EMAIL -->
    <div class="card">
      <div class="card-header"><span class="icon">📧</span> אימייל ללקוח</div>
      <div class="card-body">
        <div class="email-box">
          <div class="email-meta">
            <div><span>אל: </span>{d.get('email','')}</div>
            <div><span>נושא: </span>ברוכים הבאים לזאפ! הכל מוכן לתחילת הקמת {d.get('business_name','')} 🚀</div>
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
    </div>

    <!-- CRM RECORD -->
    <div class="card">
      <div class="card-header"><span class="icon">🗃️</span> רשומת CRM</div>
      <div class="card-body">
        <div class="crm-record">{json.dumps({"record_id": record_id, "status": "onboarding_email_sent", "business_name": d.get('business_name'), "owner": d.get('owner_name'), "phone": d.get('phone'), "email": d.get('email'), "city": d.get('city'), "services": d.get('services'), "created_at": now}, ensure_ascii=False, indent=2)}</div>
      </div>
    </div>

  </div>
</div>

</body>
</html>"""
