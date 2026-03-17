
from groq import Groq
import json
import re

import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_questions(topic,difficulty,count):

    prompt = f"""
Generate {count} MCQ questions on {topic}.

Difficulty level: {difficulty}

Return ONLY JSON like:
s
[
 {{
  "question":"question text",
  "options":["option1","option2","option3","option4"],
  "answer_index":0
 }}
]

answer_index must be the index of the correct option (0-3).
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}]
    )

    text = response.choices[0].message.content

    match = re.search(r"\[.*\]", text, re.S)

    questions = json.loads(match.group())

    return questions