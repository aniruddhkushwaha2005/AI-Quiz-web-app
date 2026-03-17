# AI Quiz App (Flask) — Student Dashboard + Monthly Results

A Flask web app that generates AI MCQ quizzes, lets students submit answers, and saves each attempt to SQLite so they can view **monthly quiz history** and stats on a **student dashboard**.

## Features

- **Login / Register** (SQLite)
- **AI quiz generator** (Groq LLM)
- **Quiz attempts are saved** (score, total, topic, difficulty, timestamp)
- **Student dashboard**
  - Monthly grouped results table
  - Quick stats: total quizzes, average %, best %
- **Modern cold-color UI** + lightweight SVG graphics

## Project structure

- `app.py` — Flask app + routes + saving quiz attempts
- `ai_generator.py` — calls Groq to generate MCQs
- `templates/` — Jinja templates (`base.html`, `dashboard.html`, etc.)
- `static/style.css` — styles
- `static/graphics/` — SVG décor assets
- `quiz.db` — SQLite database (auto-created on first run)

## Requirements

- Python 3.10+ recommended
- Packages:
  - `flask`
  - `groq`

Install:

```bash
pip install flask groq
```

## Configure the Groq API key (important)

Right now `ai_generator.py` contains an API key directly in the code. **You should remove it and load it from an environment variable**.

Recommended (PowerShell):

```powershell
$env:GROQ_API_KEY="YOUR_KEY_HERE"
```

Then update `ai_generator.py` to use:

```python
import os
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
```

## Run the app

From the project folder:

```bash
python app.py
```

Open the site, register/login, generate a quiz, submit it, then check **Dashboard** for your monthly history.

## Pages / Routes

- `/login` — login
- `/register` — register
- `/dashboard` — student dashboard (monthly attempts + stats)
- `/trainer` — generate quiz
- `/submit` — submit quiz answers (saves attempt)
- `/logout` — logout

## Notes / Troubleshooting

- **Template error after changes**: restart Flask and hard refresh browser (`Ctrl+F5`).
- **Database**: `quiz.db` is created automatically if missing.
- **If AI quiz generation fails**: confirm your Groq key is valid and that you installed `groq`.

