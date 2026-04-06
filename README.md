# Zap Group – AI-Powered Client Onboarding Automation

פתרון אוטומציה מבוסס AI לתהליך Onboarding והקמה של לקוח עסקי חדש בזאפ גרופ.

---

## הרקע

חברת זאפ מנהלת נוכחות דיגיטלית ללקוחות עסקיים דרך אתרי האינדקס שלה, ביניהם **דפי זהב**.
המשימה: בניית אוטומציה שסורקת את הנכסים הדיגיטליים של לקוח חדש, מחלצת מידע רלוונטי, ומייצרת כרטיס לקוח ותסריט אונבורדינג — הכל אוטומטית.

**לקוח לדוגמה:** טכנאי מזגנים באיזור הקריות — אתר 5 עמודים + מיניסייט בדפי זהב.

---

## הגישה

```
Digital Assets (Website + Dapei Zahav)
         │
         ▼
  [1] Web Scraper
   requests + BeautifulSoup
   זיהוי אוטומטי של אתרי JS → Playwright fallback
         │
         ▼
  [2] AI Extraction  (Groq / llama-3.3-70b)
   חילוץ מובנה: פרטי קשר, שירותים, מותגים, אזורי פעילות
   זיהוי שדות חסרים + התראה למפיק
         │
         ├──────────────────────────┐
         ▼                          ▼
  [3] כרטיס לקוח               [4] תסריט אונבורדינג
   Markdown מפורט                תסריט שיחה מותאם אישית
   למפיק הזאפ                   עם הנחיות למפיק
         │                          │
         └──────────┬───────────────┘
                    ▼
           [5] CRM + אימייל
            רישום אוטומטי במערכת
            שליחת אימייל ללקוח
```

---

## הרצה

### התקנה

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### הגדרת API Key

קבלת מפתח חינמי (ללא כרטיס אשראי) מ-[console.groq.com](https://console.groq.com):

```bash
echo 'GROQ_API_KEY=your-key-here' > .env
```

### Demo Mode

```bash
python main.py --demo
```

### Live Mode (URLs אמיתיים)

```bash
python main.py \
  --website https://example-client.co.il \
  --dapei-zahav "https://www.d.co.il/..."
```

---

## קבצי פלט

כל הפלטים נשמרים אוטומטית בתיקיית `output/`:

| קובץ | תוכן |
|------|------|
| `client_data.json` | נתוני הלקוח המובנים |
| `client_card.md` | כרטיס הלקוח למפיק |
| `onboarding_script.md` | תסריט שיחת האונבורדינג |
| `email_*.txt` | האימייל שנשלח ללקוח |
| `crm_records.json` | רשומות ה-CRM |

---

## מבנה הפרויקט

```
├── main.py                      # Orchestrator — כל הזרימה מכאן
├── requirements.txt
├── src/
│   ├── scraper.py               # סריקת אתרים + Playwright fallback
│   ├── ai_processor.py          # חילוץ נתונים, כרטיס לקוח, תסריט שיחה
│   ├── crm.py                   # רישום CRM + סימולציית אימייל
│   └── results_viewer.py        # דף תוצאות HTML (נפתח אוטומטית)
├── data/
│   └── demo_data.py             # נתוני דמו — טכנאי מזגנים ריאליסטי
└── screenshots/                 # צילומי מסך לתיעוד
```

---

## חיבור שליחת מייל אמיתית

כרגע המערכת **מסמלצת** שליחת מייל — שומרת את תוכן האימייל לקובץ `output/email_*.txt`.
לחיבור ספק מייל אמיתי, יש לעדכן את `simulate_send_email()` ב-`src/crm.py`.

| ספק | חבילה | משתנה סביבה |
|-----|-------|-------------|
| **SendGrid** | `pip install sendgrid` | `SENDGRID_API_KEY` |
| **SMTP** (Gmail / Outlook) | מובנה ב-Python | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` |
| **Mailchimp Transactional** | `pip install mailchimp-transactional` | `MANDRILL_API_KEY` |

דוגמאות קוד מלאות לכל אפשרות נמצאות בתוך הפונקציה עצמה (docstring של `simulate_send_email`).

לחיבור CRM אמיתי (HubSpot / Salesforce) — יש להחליף את קריאות `_save_records()` ב-`crm.py` בקריאות REST API של ה-CRM הרלוונטי.

---

## Results Viewer

בסיום הריצה נפתח אוטומטית דף HTML בדפדפן המציג את כל הפלטים בצורה ויזואלית:
כרטיס לקוח, תסריט אונבורדינג, אימייל ללקוח ורשומת CRM.

> **הערה:** דף התוצאות נוצר לצורכי הצגה בלבד ואינו חלק מהמערכת עצמה.

---

## דוגמת פלט

### כרטיס לקוח
![Client Card](screenshots/screenshot_tab_card.png)

### תסריט שיחת אונבורדינג
![Onboarding Script](screenshots/screenshot_tab_script.png)

### אימייל אוטומטי ללקוח
![Email](screenshots/screenshot_tab_email.png)

### רשומת CRM
![CRM](screenshots/screenshot_tab_crm.png)

---

*Built by Or Dahan*
