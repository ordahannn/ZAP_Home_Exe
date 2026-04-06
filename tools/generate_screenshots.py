"""
Generates PNG screenshots of the actual outputs for the README.
"""

import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

STYLE = """
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    direction: rtl;
    background: #f5f6fa;
    padding: 32px;
    margin: 0;
    color: #222;
  }
  .card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.10);
    padding: 32px 40px;
    max-width: 720px;
    margin: 0 auto;
  }
  .header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    border-bottom: 2px solid #e8eaf0;
    padding-bottom: 16px;
  }
  .logo { font-size: 22px; font-weight: 800; color: #e63946; letter-spacing: -1px; }
  .badge {
    background: #fff3cd;
    color: #856404;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid #ffc107;
  }
  .badge.sent { background: #d1e7dd; color: #0a3622; border-color: #a3cfbb; }
  h1 { font-size: 20px; margin: 0 0 20px 0; color: #1a1a2e; }
  h2 { font-size: 14px; color: #555; text-transform: uppercase;
       letter-spacing: 0.5px; margin: 20px 0 8px; border-right: 3px solid #e63946;
       padding-right: 8px; }
  .row { display: flex; gap: 8px; margin: 5px 0; font-size: 14px; }
  .label { color: #888; min-width: 110px; }
  .value { color: #222; font-weight: 500; }
  .tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
  .tag {
    background: #f0f1f5; border-radius: 6px;
    padding: 3px 10px; font-size: 13px; color: #444;
  }
  .status {
    display: inline-block; margin-top: 20px;
    background: #fff3cd; color: #856404;
    padding: 6px 14px; border-radius: 20px;
    font-size: 13px; font-weight: 600;
    border: 1px solid #ffc107;
  }
  pre {
    background: #1e1e2e; color: #cdd6f4; border-radius: 8px;
    padding: 20px; font-size: 13px; line-height: 1.7;
    white-space: pre-wrap; font-family: 'Courier New', monospace;
  }
  .script-section { margin-bottom: 18px; }
  .script-section h2 { color: #1a1a2e; border-right-color: #457b9d; }
  .script-text { font-size: 14px; line-height: 1.8; color: #333; }
  .note { color: #888; font-style: italic; font-size: 13px; }
  .email-box {
    background: #f8f9fa; border: 1px solid #dee2e6;
    border-radius: 8px; padding: 20px; font-size: 14px; line-height: 1.9;
  }
  .email-header { font-size: 13px; color: #666; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
  .email-header span { font-weight: 600; color: #333; }
"""

def screenshot(html: str, output_path: str, width: int = 800):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 100})
        page.set_content(html)
        page.wait_for_timeout(300)
        height = page.evaluate("document.body.scrollHeight")
        page.set_viewport_size({"width": width, "height": height + 20})
        page.screenshot(path=output_path, full_page=True)
        browser.close()
    print(f"  Saved → {output_path}")


def make_client_card():
    with open("output/client_data.json", encoding="utf-8") as f:
        d = json.load(f)

    services_html = "".join(f'<span class="tag">{s}</span>' for s in d.get("services", []))
    brands_html   = "".join(f'<span class="tag">{b}</span>' for b in d.get("brands_handled", []))
    areas_html    = "".join(f'<span class="tag">{a}</span>' for a in d.get("service_areas", []))

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>{STYLE}</style></head><body>
    <div class="card">
      <div class="header">
        <span class="logo">zap group</span>
        <span class="badge">לקוח חדש</span>
      </div>
      <h1>כרטיס לקוח: {d.get('business_name', '')}</h1>

      <h2>פרטי העסק</h2>
      <div class="row"><span class="label">שם העסק</span><span class="value">{d.get('business_name','')}</span></div>
      <div class="row"><span class="label">בעלים</span><span class="value">{d.get('owner_name','')}</span></div>
      <div class="row"><span class="label">סוג עסק</span><span class="value">{d.get('business_type','')}</span></div>
      <div class="row"><span class="label">ניסיון</span><span class="value">{d.get('years_in_business','')} שנים</span></div>

      <h2>פרטי קשר</h2>
      <div class="row"><span class="label">טלפון</span><span class="value">{d.get('phone','')}</span></div>
      <div class="row"><span class="label">טלפון נוסף</span><span class="value">{d.get('secondary_phone','')}</span></div>
      <div class="row"><span class="label">אימייל</span><span class="value">{d.get('email','')}</span></div>
      <div class="row"><span class="label">כתובת</span><span class="value">{d.get('address','')}</span></div>

      <h2>שירותים</h2>
      <div class="tags">{services_html}</div>

      <h2>מותגים</h2>
      <div class="tags">{brands_html}</div>

      <h2>אזורי פעילות</h2>
      <div class="tags">{areas_html}</div>

      <h2>נכסים דיגיטליים</h2>
      <div class="row"><span class="label">אתר</span><span class="value">{d.get('website_url','')}</span></div>
      <div class="row"><span class="label">דפי זהב</span><span class="value">{d.get('dapei_zahav_url','')}</span></div>
      <div class="row"><span class="label">פייסבוק</span><span class="value">{d.get('social_media',{}).get('facebook','')}</span></div>
      <div class="row"><span class="label">אינסטגרם</span><span class="value">{d.get('social_media',{}).get('instagram','')}</span></div>

      <div class="status">לקוח חדש | ממתין לאונבורדינג</div>
    </div>
    </body></html>"""

    screenshot(html, "output/screenshot_client_card.png")


def make_onboarding_script():
    with open("output/onboarding_script.md", encoding="utf-8") as f:
        raw = f.read()

    # Parse sections
    sections = []
    current_title = None
    current_lines = []
    for line in raw.splitlines():
        if line.startswith("## "):
            if current_title:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:]
            current_lines = []
        elif not line.startswith("[הנחיות") or current_title:
            current_lines.append(line)
    if current_title:
        sections.append((current_title, "\n".join(current_lines).strip()))

    sections_html = ""
    for title, body in sections:
        body_escaped = body.replace("<","&lt;").replace(">","&gt;")
        # Style producer notes differently
        import re
        body_html = re.sub(
            r'\[הנחיות למפיק:([^\]]+)\]',
            r'<span class="note">📋 הנחיה למפיק:\1</span>',
            body_escaped
        )
        sections_html += f"""
        <div class="script-section">
          <h2>{title}</h2>
          <div class="script-text">{body_html}</div>
        </div>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>{STYLE}</style></head><body>
    <div class="card">
      <div class="header">
        <span class="logo">zap group</span>
        <span style="font-size:14px;color:#555;">תסריט שיחת אונבורדינג</span>
      </div>
      <h1>תסריט אונבורדינג — קול קריות</h1>
      {sections_html}
    </div>
    </body></html>"""

    screenshot(html, "output/screenshot_onboarding_script.png")


def make_email():
    with open("output/email_20260406_133725.txt", encoding="utf-8") as f:
        lines = f.read().splitlines()

    to_line      = lines[0].replace("TO: ", "")
    subject_line = lines[1].replace("SUBJECT: ", "")
    body         = "\n".join(lines[4:])
    body_escaped = body.replace("<","&lt;").replace(">","&gt;")

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <style>{STYLE}</style></head><body>
    <div class="card">
      <div class="header">
        <span class="logo">zap group</span>
        <span class="badge sent">נשלח ✓</span>
      </div>
      <h1>אימייל אוטומטי ללקוח</h1>
      <div class="email-box">
        <div class="email-header">
          <div><span>אל: </span>{to_line}</div>
          <div><span>נושא: </span>{subject_line}</div>
        </div>
        <div style="white-space:pre-wrap">{body_escaped}</div>
      </div>
    </div>
    </body></html>"""

    screenshot(html, "output/screenshot_email.png")


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    print("Generating screenshots...")
    make_client_card()
    make_onboarding_script()
    make_email()
    print("Done.")
