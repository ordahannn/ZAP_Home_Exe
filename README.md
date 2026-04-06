# Zap Group – AI-Powered Client Onboarding Automation

פתרון אוטומציה מבוסס AI לתהליך Onboarding והקמה של לקוח עסקי חדש בזאפ גרופ.

---

## הרקע

חברת זאפ מנהלת נוכחות דיגיטלית ללקוחות עסקיים דרך אתרי האינדקס שלה, ביניהם **דפי זהב**.
המשימה: בניית אוטומציה שסורקת את הנכסים הדיגיטליים של לקוח חדש, מחלצת מידע רלוונטי, ומייצרת כרטיס לקוח ותסריט אונבורדינג – הכל אוטומטית.

**לקוח לדוגמה:** יוסי כהן, טכנאי מזגנים באיזור הקריות – אתר 5 עמודים + מיניסייט בדפי זהב.

---

## הגישה שנבחרה

```
Digital Assets (Website + Dapei Zahav)
         │
         ▼
  [1] Web Scraper
   requests + BeautifulSoup
   Multi-page crawl, clean text extraction
         │
         ▼
  [2] AI Extraction (Gemini 2.0 Flash)
   Structured JSON: contact info, services,
   brands, service areas, USPs
         │
         ├──────────────────────────┐
         ▼                          ▼
  [3] Client Card Generator   [4] Onboarding Script Generator
   Hebrew Markdown card         Personalized call script
   for Zap account manager      with producer instructions
         │                          │
         └──────────┬───────────────┘
                    ▼
           [5] CRM Logger + Email
            JSON-based mock CRM
            Simulated email dispatch
            (SendGrid-ready in production)
```

### למה Google Gemini 2.0 Flash?
- **חינמי לגמרי** – 1,500 בקשות ביום, ללא כרטיס אשראי
- הבנת עברית מצוינת
- מהיר וקל לשימוש
- API key חינמי מ-[Google AI Studio](https://aistudio.google.com)

---

## הרצה מהירה

### דרישות מוקדמות

```bash
pip install -r requirements.txt
```

הגדרת API key (חינמי מ-[aistudio.google.com](https://aistudio.google.com)):
```bash
export GEMINI_API_KEY="your-key-here"
# או צרו קובץ .env:
echo 'GEMINI_API_KEY=your-key-here' > .env
```

### Demo Mode (מומלץ לראיון)
מריץ את כל הזרימה עם נתוני מזגנים ריאליסטיים – ללא צורך ב-URLs חיים:

```bash
python main.py --demo
```

### Live Mode (URLs אמיתיים)
```bash
python main.py \
  --website https://www.cool-krayot.co.il \
  --dapei-zahav "https://www.d.co.il/קריות/טכנאי-מזגנים/קול-קריות"
```

### Load from file (ללא סריקה חוזרת)
```bash
python main.py --from-file output/scraped_content.txt
```

---

## קבצי פלט

כל הפלטים נשמרים בתיקיית `output/`:

| קובץ | תוכן |
|------|------|
| `client_data.json` | נתוני הלקוח המובנים (JSON) |
| `client_card.md` | כרטיס הלקוח למפיק (Markdown) |
| `onboarding_script.md` | תסריט שיחת האונבורדינג |
| `email_*.txt` | האימייל שנשלח ללקוח (סימולציה) |
| `scraped_content.txt` | התוכן הגולמי שנסרק |
| `crm_records.json` | רשומות ה-CRM (JSON) |

---

## מבנה הפרויקט

```
├── main.py              # Orchestrator – כל הזרימה מכאן
├── scraper.py           # Web scraping (website + Dapei Zahav)
├── ai_processor.py      # Claude API: extraction, card, script
├── crm.py               # Mock CRM logger + email simulation
├── demo_data.py         # Mock data – טכנאי מזגנים ריאליסטי
├── requirements.txt
├── .env.example
└── output/              # נוצר אוטומטית
```

---

## הרחבות לפרודקשן

1. **CRM אמיתי** – החלפת `crm.py` ב-API calls לסיילספורס / HubSpot
2. **שליחת אימייל** – חיבור ל-SendGrid / Mailchimp
3. **webhook trigger** – הפעלה אוטומטית עם הרישום של לקוח חדש במערכת
4. **Dashboard** – ממשק צפייה בכרטיסי הלקוחות
5. **Multi-language** – תמיכה בלקוחות דוברי ערבית / רוסית

---

## דוגמת פלט

### כרטיס לקוח (קטע)

> **שם העסק:** קול קריות
> **בעלים:** יוסי כהן | **טלפון:** 052-3456789
> **שירותים:** התקנה, תיקון, ניקוי, טעינת גז
> **מותגים:** LG, Samsung, Mitsubishi, Tadiran
> **אזורי פעילות:** קריות, חיפה, עכו

### תסריט אונבורדינג (קטע)

> "שלום יוסי, מדבר/ת [שם] מזאפ גרופ – אנחנו שמחים שבחרת בנו לניהול הנוכחות הדיגיטלית של קול קריות!"

---

*Built by: Or Dahan | HomeAssignment for Zap Group GenAI Exploration Lead*
