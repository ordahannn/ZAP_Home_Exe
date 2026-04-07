<div dir="rtl">

# אוטומציית אונבורדינג לקוחות – זאפ גרופ

פתרון שבניתי למשימת הבית של זאפ גרופ — אוטומציה שסורקת את הנכסים הדיגיטליים של לקוח חדש, שולפת ממנו מידע, ומייצרת כרטיס לקוח, תסריט שיחה, ורישום CRM — הכל אוטומטי.

**לקוח לדוגמה:** טכנאי מזגנים באזור הקריות — אתר 5 עמודים + מיניסייט בדפי זהב.

---

## איך זה עובד

1. **סריקת נכסים דיגיטליים** — אתר הלקוח + דפי זהב. זיהוי אוטומטי של אתרי JS עם מעבר ל-Playwright
2. **חילוץ נתונים עם AI** — מודל llama-3.3-70b דרך Groq: פרטי קשר, שירותים, מותגים, אזורי פעילות. שדות חסרים מסומנים אוטומטית
3. **כרטיס לקוח** — מסמך מפורט למפיק זאפ
4. **תסריט אונבורדינג** — שיחה מותאמת אישית עם הנחיות למפיק
5. **רישום CRM + אימייל** — תיעוד הלקוח ושליחת אימייל פתיחה
6. **דף תוצאות** — עמוד עם 4 טאבים שנפתח אוטומטית בדפדפן בסוף הריצה

---

## התקנה והרצה

<div dir="ltr">

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

</div>

מפתח Groq חינמי (ללא כרטיס אשראי) מ-[console.groq.com](https://console.groq.com):

<div dir="ltr">

```bash
echo 'GROQ_API_KEY=your-key-here' > .env
```

</div>

### מצב Demo

<div dir="ltr">

```bash
python main.py --demo
```

</div>

### מצב Live

<div dir="ltr">

```bash
python main.py --website https://example-client.co.il --dapei-zahav "https://www.d.co.il/..."
```

</div>

---

## קבצי פלט

כל הקבצים נשמרים בתיקיית `output/`:

| תוכן | קובץ |
|------|------|
| נתוני הלקוח המובנים | `client_data.json` |
| כרטיס הלקוח למפיק | `client_card.md` |
| תסריט שיחת האונבורדינג | `onboarding_script.md` |
| האימייל שנשלח ללקוח | `email_*.txt` |

---

## מגבלות ידועות

- **Groq (חינמי)** — מגביל 100,000 טוקנים ליום. אם נגמרה המכסה, ממתינים עד למחרת
- **דפי זהב** — חוסמת סורקים (403/429). מצב ה-Demo משתמש בנתוני mock ריאליסטיים
- **שליחת מייל** — כרגע מסומלצת ונשמרת לקובץ. לחיבור אמיתי ראו הוראות בקובץ crm.py

---

## חיבור מייל אמיתי

קובץ crm.py מכיל הוראות מפורטות לחיבור עם:
- SendGrid
- SMTP רגיל (Gmail / Outlook)
- Mailchimp Transactional

---

## מבנה הפרויקט

<div dir="ltr">

```
├── main.py                 # main pipeline orchestrator
├── requirements.txt
├── src/
│   ├── scraper.py          # web scraper + Playwright fallback
│   ├── ai_processor.py     # AI extraction, client card, script
│   ├── crm.py              # CRM logging + email simulation
│   └── results_viewer.py   # HTML results page
├── data/
│   └── demo_data.py        # realistic mock data for demo mode
└── screenshots/
```

</div>

---

## דוגמת פלט

### כרטיס לקוח
![Client Card](screenshots/screenshot_tab_card.png)

### תסריט שיחת אונבורדינג
![Onboarding Script](screenshots/screenshot_tab_script.png)

### אימייל ללקוח
![Email](screenshots/screenshot_tab_email.png)

### רשומת CRM
![CRM](screenshots/screenshot_tab_crm.png)

---

*אור דהן*

</div>
