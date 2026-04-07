"""
AI processing module using Groq API (free tier, no credit card needed).
Model: llama-3.3-70b-versatile — fast, strong Hebrew support.
Handles:
  1. Structured data extraction from scraped content
  2. Client card generation (for the Zap account manager)
  3. Personalized onboarding call script generation
"""

import json
import os
from groq import Groq

MODEL = "llama-3.3-70b-versatile"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def _chat(prompt: str, max_tokens: int = 2000) -> str:
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def extract_client_data(raw_content: str) -> dict:
    """
    Extract structured client data from scraped content.
    Returns a dict with business details, contacts, and services.
    """
    prompt = f"""You are an expert data extractor for Zap Group, an Israeli digital marketing company.
You are given raw scraped text from a business client's digital assets (website + Dapei Zahav listing).
Extract all relevant information and return it as a valid JSON object.

Raw content:
<content>
{raw_content[:12000]}
</content>

Return ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{{
  "business_name": "string or null",
  "owner_name": "string or null",
  "phone": "string or null",
  "secondary_phone": "string or null",
  "email": "string or null",
  "website_url": "string or null",
  "dapei_zahav_url": "string or null",
  "address": "string or null",
  "city": "string or null",
  "region": "string or null",
  "business_type": "string (e.g. 'טכנאי מזגנים')",
  "services": ["list", "of", "services"],
  "brands_handled": ["list", "of", "AC", "brands"],
  "service_areas": ["list", "of", "areas"],
  "years_in_business": "string or null",
  "certifications": ["list", "of", "certifications"],
  "working_hours": "string or null",
  "social_media": {{"facebook": null, "instagram": null, "whatsapp": null}},
  "unique_selling_points": ["notable", "differentiators"],
  "notes": "any other relevant details as a single string"
}}"""

    raw = _chat(prompt)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # AI occasionally returns slightly malformed JSON — try to extract the object
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise ValueError(f"AI returned non-JSON response: {raw[:200]}")

    # Flag missing critical fields so the account manager knows what to ask
    critical = ["phone", "email", "business_name", "services", "working_hours"]
    missing = [f for f in critical if not data.get(f)]
    if missing:
        data["missing_fields"] = missing
        data["notes"] = (data.get("notes") or "") + (
            f"\n⚠️ לא נמצא אוטומטית — יש לברר בשיחה: {', '.join(missing)}"
        )

    return data


def generate_client_card(client_data: dict) -> str:
    """
    Generate a formatted client card (כרטיס לקוח) for the Zap account manager.
    Returns a Hebrew-language markdown document.
    """
    prompt = f"""אתה מומחה ב-Onboarding לקוחות של חברת זאפ גרופ.
בהתבסס על הנתונים שחולצו מהנכסים הדיגיטליים של הלקוח, צור 'כרטיס לקוח' מפורט ומסודר.

נתוני הלקוח:
{json.dumps(client_data, ensure_ascii=False, indent=2)}

צור כרטיס לקוח בפורמט Markdown הכולל את הסעיפים הבאים:
1. **פרטי העסק** - שם, סוג עסק, אזור
2. **פרטי קשר** - טלפון, אימייל, כתובת
3. **שירותים ומוצרים** - רשימת שירותים, מותגים שמטפלים בהם
4. **אזורי פעילות**
5. **נכסים דיגיטליים** - אתר אינטרנט, דפי זהב, רשתות חברתיות
6. **יתרונות ייחודיים** - מה מבדל את הלקוח
7. **הערות למפיק** - המלצות לנקודות דגש בשיחת האונבורדינג
8. **סטטוס** - "לקוח חדש | ממתין לאונבורדינג"

כתוב בעברית, בטון מקצועי. הכרטיס צריך להיות קריא, ברור, ושמיש מיידית לנציג הזאפ."""

    return _chat(prompt, max_tokens=2000)


def generate_onboarding_script(client_data: dict) -> str:
    """
    Generate a personalized onboarding call script for the client.
    Returns a Hebrew-language call script.
    """
    business_name = client_data.get("business_name", "העסק שלך")
    owner_name = client_data.get("owner_name", "")
    services = ", ".join(client_data.get("services", []))
    region = client_data.get("region") or client_data.get("city", "הקריות")

    missing = client_data.get("missing_fields", [])
    missing_note = (
        f"\n\n⚠️ שדות שלא נמצאו אוטומטית ויש לברר בשיחה: {', '.join(missing)}\n"
        "חובה להכניס שאלה ספציפית לגבי כל שדה חסר בחלק 'שאלות לאיסוף מידע', "
        "וסמן אותה ב-**❗חובה לברר** בתוך התסריט (בדיוק כך, עם כוכביות)."
        if missing else ""
    )

    prompt = f"""אתה מומחה בחווית לקוח ואונבורדינג של חברת זאפ גרופ.
צור תסריט שיחת אונבורדינג מותאם אישית ללקוח הבא:

שם העסק: {business_name}
שם הבעלים: {owner_name or "לא ידוע"}
שירותים: {services or "טכנאי מזגנים"}
אזור: {region}
כל נתוני הלקוח: {json.dumps(client_data, ensure_ascii=False, indent=2)}{missing_note}

צור תסריט שיחה בעברית הכולל:

## פתיחה
הצגה חמה, אישור זהות, הכרת תודה על הרכישה.

## הצגת הערך
הסבר קצר מה כולל החבילה שרכש (אתר 5 עמודים + מיניסייט דפי זהב).

## שאלות לאיסוף מידע
5-7 שאלות ממוקדות שיעזרו להשלים את הפרופיל:
- אימות פרטי קשר
- שעות פעילות
- אזורי שירות מועדפים
- מותגי מזגנים שמתמחים בהם
- תמונות/לוגו קיימים

## הצגת שלבי ההקמה
לוח זמנים צפוי (מה קורה בשבוע הקרוב).

## סיכום וצעדים הבאים
מה קורה אחרי השיחה, מי מדבר עם מי.

## סגירה
נימה חמה, פרטי קשר ישירים.

---
הוסף הנחיות למפיק רק בפורמט הזה בדיוק: [הנחיות למפיק: טקסט ההנחיה]
אל תוסיף סוגריים מרובעים בשום מקום אחר בתסריט.
הטון צריך להיות מקצועי אך חם ונגיש."""

    return _chat(prompt, max_tokens=2500)
