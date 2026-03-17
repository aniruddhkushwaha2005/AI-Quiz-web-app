from flask import Flask, render_template, request, redirect, session
from ai_generator import generate_questions
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key="secret"

def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT NOT NULL,
            topic TEXT,
            difficulty TEXT,
            question_count INTEGER,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    db.commit()

def get_db():
    conn=sqlite3.connect("quiz.db")
    conn.row_factory=sqlite3.Row
    return conn

init_db()

@app.route("/")
def home():
    return redirect("/login")


# LOGIN
@app.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form["email"]
        password=request.form["password"]

        db=get_db()

        user=db.execute(
        "SELECT * FROM students WHERE email=? AND password=?",
        (email,password)
        ).fetchone()

        if user:

            session["user"]=email

            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid email or password.")

    return render_template("login.html")
# REGISTER
@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        name=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]

        db=get_db()

        try:
            db.execute(
            "INSERT INTO students(name,email,password) VALUES(?,?,?)",
            (name,email,password)
            )
            db.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return render_template("register.html", error="That email is already registered. Try logging in.")

    return render_template("register.html")





# TRAINER
@app.route("/trainer",methods=["GET","POST"])
def trainer():
    if "user" not in session:
        return redirect("/login")

    if request.method=="POST":

        topic=request.form["topic"]
        difficulty=request.form["difficulty"]
        count=request.form["count"]

        questions=generate_questions(topic,difficulty,count)
        session["questions"] = questions
        session["quiz_meta"] = {"topic": topic, "difficulty": difficulty, "count": int(count)}

        return render_template("quiz.html",questions=questions)

    return render_template("trainer.html")


# SUBMIT QUIZ
@app.route("/submit",methods=["POST"])
def submit():
    if "user" not in session:
        return redirect("/login")

    questions = session.get("questions", [])

    score = 0
    user_answers = []

    for i,q in enumerate(questions):

        user_answer = request.form.get(str(i))

        user_answers.append(user_answer)

        if user_answer == q["options"][q["answer_index"]]:
            score += 1

    meta = session.get("quiz_meta", {})
    db = get_db()
    db.execute(
        """
        INSERT INTO quiz_attempts(student_email, topic, difficulty, question_count, score, total, created_at)
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            session["user"],
            meta.get("topic"),
            meta.get("difficulty"),
            meta.get("count"),
            score,
            len(questions),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    db.commit()

    session.pop("questions", None)
    session.pop("quiz_meta", None)

    return render_template(
        "result.html",
        score=score,
        questions=questions,
        user_answers=user_answers
    )

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    db = get_db()
    rows = db.execute(
        """
        SELECT id, topic, difficulty, question_count, score, total, created_at
        FROM quiz_attempts
        WHERE student_email=?
        ORDER BY datetime(created_at) DESC
        """,
        (session["user"],),
    ).fetchall()

    attempts = [dict(r) for r in rows]

    # Group by month (YYYY-MM) + compute month averages
    monthly = []
    buckets = {}
    for a in attempts:
        month_key = (a.get("created_at") or "")[:7]  # YYYY-MM
        buckets.setdefault(month_key, []).append(a)

    for month_key, month_attempts in buckets.items():
        month_total = sum((x.get("total") or 0) for x in month_attempts)
        month_score = sum((x.get("score") or 0) for x in month_attempts)
        month_avg = round((month_score / month_total) * 100, 1) if month_total else 0
        monthly.append(
            {
                "key": month_key,
                "attempts": month_attempts,
                "avg_percent": month_avg,
            }
        )

    total_quizzes = len(attempts)
    avg_percent = round(
        (sum((a["score"] / a["total"]) * 100 for a in attempts if a["total"]) / total_quizzes),
        1,
    ) if total_quizzes else 0
    best_percent = round(
        max(((a["score"] / a["total"]) * 100 for a in attempts if a["total"]), default=0),
        1,
    )

    return render_template(
        "dashboard.html",
        user_email=session["user"],
        monthly=monthly,
        total_quizzes=total_quizzes,
        avg_percent=avg_percent,
        best_percent=best_percent,
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__=="__main__":
    app.run(debug=True)