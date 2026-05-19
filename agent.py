"""
Space Fractions Code Agent
==========================
Author: Aqsa Rani
University of Lahore, Pakistan

Uses OpenRouter API (free) to call Claude AI
OpenRouter = a website that gives you access to many AI models for free/cheap

How to run:
  1. pip install requests python-dotenv
  2. Create .env file with: OPENROUTER_API_KEY=sk-or-v1-your-key-here
  3. Run: D:\python.exe agent.py
"""

import os
import re
import json
import time
import requests          # requests = send HTTP calls to OpenRouter API
import sys

sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()   # reads .env file → puts OPENROUTER_API_KEY into os.environ

# ── CONFIGURATION ─────────────────────────────────────────────────────────────

OUTPUT_DIR = "generated_project"

# OpenRouter API URL — this is where we send our requests
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Free model on OpenRouter — Claude Haiku is cheap/free tier
MODEL = "anthropic/claude-3-haiku"


# ── HELPER ────────────────────────────────────────────────────────────────────
def header(text):
    print(f"\n{'='*55}")
    print(f"  {text}")
    print(f"{'='*55}")


# ── STEP 1: READ ARCHITECTURE FILES ───────────────────────────────────────────
def read_architecture_files():
    print("\n[1/5] Reading architecture documents...")

    if not os.path.exists("Architecture_Documentation.md"):
        print("ERROR: Architecture_Documentation.md not found in this folder!")
        print(f"Current folder: {os.getcwd()}")
        print("Copy the .md files to the same folder as agent.py")
        exit(1)

    if not os.path.exists("Architecture_View.md"):
        print("ERROR: Architecture_View.md not found!")
        exit(1)

    with open("Architecture_Documentation.md", "r", encoding="utf-8") as f:
        doc_content = f.read()

    with open("Architecture_View.md", "r", encoding="utf-8") as f:
        view_content = f.read()

    print(f"    ✓ Architecture_Documentation.md ({len(doc_content)} characters)")
    print(f"    ✓ Architecture_View.md ({len(view_content)} characters)")

    return {
        "documentation": doc_content,
        "views": view_content
    }


# ── STEP 2: PARSE INTO STRUCTURED DATA ────────────────────────────────────────
def parse_architecture(files):
    print("\n[2/5] Parsing architecture documents...")

    doc  = files["documentation"]
    view = files["views"]

    system_desc = ""
    exec_match = re.search(r"# A\. Executive Summary\n(.*?)# B\.", doc, re.DOTALL)
    if exec_match:
        system_desc = exec_match.group(1).strip()[:500]

    components = ["GameComponent", "QuestionComponent", "UserComponent"]

    arch_style = "Microservices"
    style_match = re.search(r"Chosen architectural style:\s*([^\n]+)", doc)
    if style_match:
        arch_style = style_match.group(1).strip()

    diagram_count = len(re.findall(r"@startuml", view))

    tech_stack = {}
    for comp in components:
        section = re.search(rf"## {comp}(.*?)(?=## |\Z)", doc, re.DOTALL)
        if section:
            text = section.group(1)
            lang  = re.search(r"Language/runtime:\s*([^\n(]+)", text)
            fw    = re.search(r"Web framework:\s*([^\n(]+)", text)
            db    = re.search(r"Persistence:\s*([^\n(]+)", text)
            tech_stack[comp] = {
                "language":  lang.group(1).strip() if lang else "Python/Flask",
                "framework": fw.group(1).strip()   if fw   else "Flask",
                "database":  db.group(1).strip()   if db   else "PostgreSQL 14"
            }

    parsed = {
        "system_name":        "Space Fractions",
        "description":        system_desc,
        "architecture_style": arch_style,
        "components":         components,
        "tech_stack":         tech_stack,
        "diagram_count":      diagram_count,
        "raw_documentation":  doc,
        "raw_views":          view
    }

    # save JSON (for inspection)
    json_safe = {k: v for k, v in parsed.items()
                 if k not in ["raw_documentation", "raw_views"]}
    with open("architecture_parsed.json", "w", encoding="utf-8") as f:
        json.dump(json_safe, f, indent=2)

    print(f"    ✓ System:     {parsed['system_name']}")
    print(f"    ✓ Style:      {parsed['architecture_style']}")
    print(f"    ✓ Components: {', '.join(components)}")
    print(f"    ✓ Diagrams:   {diagram_count}")
    print(f"    ✓ Saved architecture_parsed.json")

    return parsed


# ── STEP 3: CALL OPENROUTER API ───────────────────────────────────────────────
def ask_ai(prompt, max_tokens=2000):
    """
    Sends a prompt to OpenRouter and returns the AI response text.

    OpenRouter works with standard HTTP POST requests.
    We do NOT use the anthropic library here — just the requests library.

    How it works:
      1. Build headers with our API key
      2. Build the message body (what we want to ask)
      3. Send POST request to OpenRouter URL
      4. Read the response and return the text
    """

    api_key = os.environ.get("OPENROUTER_API_KEY")

    # Headers tell the server who we are and what format we send
    headers = {
        "Authorization": f"Bearer {api_key}",   # our API key
        "Content-Type":  "application/json",     # we are sending JSON
        "HTTP-Referer":  "http://localhost",      # required by OpenRouter
        "X-Title":       "Space Fractions Agent" # name of our app
    }

    # The message body — what we send to the AI
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert software architect and developer. "
                    "Generate clean, well-commented, production-quality code. "
                    "When asked to generate a file, return ONLY the file content "
                    "with no extra explanation and no markdown code blocks."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    # Send the POST request to OpenRouter
    # timeout=60 means give up after 60 seconds if no response
    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=body,
        timeout=60
    )

    # Check if request succeeded
    # status_code 200 = success
    # status_code 401 = wrong API key
    # status_code 429 = too many requests (slow down)
    if response.status_code != 200:
        raise Exception(
            f"API error {response.status_code}: {response.text[:300]}"
        )

    # Parse the JSON response
    data = response.json()

    # Extract the actual text from the response
    # OpenRouter response structure:
    # data["choices"][0]["message"]["content"] = the AI's reply text
    return data["choices"][0]["message"]["content"]


# ── STEP 4: WRITE FILE TO DISK ────────────────────────────────────────────────
def create_file(filepath, content):
    """Create a file and all parent folders if they don't exist."""

    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"    ✓ {filepath}")


# ── STEP 5: GENERATE ALL FILES ────────────────────────────────────────────────
def generate_project(parsed):

    header("GENERATING PROJECT FILES")

    name  = parsed["system_name"]
    arch  = parsed["architecture_style"]
    comps = ", ".join(parsed["components"])

    files_to_generate = [

        # 1 ── README
        (
            f"{OUTPUT_DIR}/README.md",
            f"""Write a complete README.md for the {name} project.
This is an educational web game for 6th grade students to practice fractions.
Architecture: {arch} with three services: {comps}
Include: project title, description, architecture overview, components table,
technology stack, prerequisites, setup steps, how to run, API endpoints table,
how to run tests, and a section explaining that this project was generated by a Code Agent.
Write professional Markdown."""
        ),

        # 2 ── requirements.txt (root)
        (
            f"{OUTPUT_DIR}/requirements.txt",
            """Write a requirements.txt for a Python project.
Include: requests, python-dotenv, anthropic
One package per line with version pinning. Return only the file content."""
        ),

        # 3 ── docker-compose.yml
        (
            f"{OUTPUT_DIR}/docker-compose.yml",
            f"""Write a docker-compose.yml for the {name} {arch} system.
Services: game-service (port 3000), question-service (port 3001),
user-service (port 3002), postgres (PostgreSQL 14), redis (Redis 6).
Include environment variables, volumes, health checks.
Return only valid YAML."""
        ),

        # 4 ── openapi.yaml
        (
            f"{OUTPUT_DIR}/openapi.yaml",
            f"""Write an OpenAPI 3.0 specification for the {name} system.
GameComponent (port 3000): GET /api/play, POST /api/answer, GET /api/score
QuestionComponent (port 3001): GET /api/questions, GET /api/questions/random, POST /api/questions/{{id}}/check
UserComponent (port 3002): POST /api/auth/register, POST /api/auth/login, GET /api/auth/verify
Include schemas and example responses. Return only valid YAML."""
        ),

        # 5 ── sql/game_ddl.sql
        (
            f"{OUTPUT_DIR}/sql/game_ddl.sql",
            """Write PostgreSQL DDL to create:
- games table: id, game_state (JSONB), student_id, created_at, updated_at
- scores table: id, game_id, student_id, final_score, completed_at
Add indexes and comments. Return only SQL."""
        ),

        # 6 ── sql/question_ddl.sql
        (
            f"{OUTPUT_DIR}/sql/question_ddl.sql",
            """Write PostgreSQL DDL to create:
- questions: id, prompt, difficulty, category_id, created_at
- answers: id, question_id, answer_text, is_correct, display_order
- categories: id, name
Include foreign keys, indexes, and 5 sample fraction questions as INSERT statements.
Return only SQL."""
        ),

        # 7 ── traceability_matrix.csv
        (
            f"{OUTPUT_DIR}/traceability_matrix.csv",
            f"""Create a CSV traceability matrix for {name}.
Columns: Requirement ID, Type, Description, Component, Test Type, Status
Rows: FR-1 (Play game), FR-2 (View score), FR-3 (Update questions),
NFR-1 (Performance <200ms), NFR-2 (99.9% uptime),
ASR-1 (Data durability), ASR-2 (Auth security).
Return only CSV content."""
        ),

        # 8 ── game-component/app.py
        (
            f"{OUTPUT_DIR}/game-component/app.py",
            f"""Write a complete Python Flask app for the GameComponent of {name}.
Include:
- Flask app with CORS
- PostgreSQL connection with psycopg2
- Redis cache with redis library
- GET /health → returns {{"status":"healthy","service":"GameComponent"}}
- GET /api/play → create new game in DB, get first question from QuestionComponent at http://localhost:3001
- POST /api/answer → body: gameId, questionId, answer. Check answer via QuestionComponent, update score in Redis and DB, return result and next question
- GET /api/score → query: gameId, return score from Redis or DB
- JWT token verification middleware
- Full try/except error handling
- Detailed comments on every function and important line
Write clean Python Flask code."""
        ),

        # 9 ── game-component/requirements.txt
        (
            f"{OUTPUT_DIR}/game-component/requirements.txt",
            """requirements.txt for Python Flask microservice.
Include: flask==2.3.3, flask-cors==4.0.0, psycopg2-binary==2.9.7,
redis==5.0.1, requests==2.31.0, PyJWT==2.8.0, python-dotenv==1.0.0, gunicorn==21.2.0
Return only the file content."""
        ),

        # 10 ── game-component/Dockerfile
        (
            f"{OUTPUT_DIR}/game-component/Dockerfile",
            """Production Dockerfile for Python Flask app.
Base: python:3.11-slim. Include: WORKDIR, copy requirements.txt, pip install,
copy app code, create non-root user, EXPOSE 3000, HEALTHCHECK, CMD gunicorn.
Return only Dockerfile content."""
        ),

        # 11 ── game-component/.env.example
        (
            f"{OUTPUT_DIR}/game-component/.env.example",
            """Write .env.example for GameComponent Flask service.
Variables: DATABASE_URL, REDIS_URL, SECRET_KEY, QUESTION_SERVICE_URL,
USER_SERVICE_URL, PORT, DEBUG, JWT_SECRET
Use placeholder values with comments. Return only file content."""
        ),

        # 12 ── question-component/app.py
        (
            f"{OUTPUT_DIR}/question-component/app.py",
            f"""Write a complete Python Flask app for the QuestionComponent of {name}.
Include:
- Flask app with CORS
- PostgreSQL connection with psycopg2
- GET /health → health check
- GET /api/questions → return all questions from DB as JSON
- GET /api/questions/random → return one random question with its answer options
- POST /api/questions/<int:id>/check → body: {{"answer":"3/4"}}, check if correct, return {{"is_correct":true/false,"correct_answer":"..."}}
- POST /api/questions → add new question (admin)
- Hardcoded sample fraction questions as fallback if DB is empty
- Full error handling and detailed comments
Write clean Python."""
        ),

        # 13 ── question-component/requirements.txt
        (
            f"{OUTPUT_DIR}/question-component/requirements.txt",
            """requirements.txt for Python Flask microservice with PostgreSQL.
Include: flask==2.3.3, flask-cors==4.0.0, psycopg2-binary==2.9.7,
python-dotenv==1.0.0, gunicorn==21.2.0
Return only file content."""
        ),

        # 14 ── user-component/app.py
        (
            f"{OUTPUT_DIR}/user-component/app.py",
            f"""Write a complete Python Flask app for the UserComponent of {name}.
Include:
- Flask with CORS
- PostgreSQL connection
- GET /health → health check
- POST /api/auth/register → validate input, hash password with bcrypt, save to DB, return success
- POST /api/auth/login → find user, verify password with bcrypt, return JWT token
- GET /api/auth/verify → verify JWT token (called by other services), return user info
- Input validation for all routes
- Full error handling and detailed comments
Write clean Python Flask code."""
        ),

        # 15 ── user-component/requirements.txt
        (
            f"{OUTPUT_DIR}/user-component/requirements.txt",
            """requirements.txt for Python Flask auth service.
Include: flask==2.3.3, flask-cors==4.0.0, psycopg2-binary==2.9.7,
PyJWT==2.8.0, bcrypt==4.0.1, python-dotenv==1.0.0, gunicorn==21.2.0
Return only file content."""
        ),

        # 16 ── tests/test_game.py
        (
            f"{OUTPUT_DIR}/tests/test_game.py",
            f"""Write pytest unit tests for the {name} GameComponent.
Test: health check returns 200, start game returns gameId and question,
correct answer increases score, wrong answer keeps score, get score works,
invalid gameId returns 404, missing fields returns 400.
Use Flask test client and mock data (no real DB needed).
Add comments explaining each test. Return only Python test code."""
        ),

        # 17 ── tests/test_questions.py
        (
            f"{OUTPUT_DIR}/tests/test_questions.py",
            f"""Write pytest unit tests for the {name} QuestionComponent.
Test: get all questions returns list, random question has correct format,
correct answer returns is_correct=true, wrong answer returns is_correct=false,
question has required fields (id, prompt, options).
Add comments. Return only Python test code."""
        ),

        # 18 ── AGENT_REPORT.md
        (
            f"{OUTPUT_DIR}/AGENT_REPORT.md",
            f"""Write a technical report (700-900 words) about this Code Agent.

The Code Agent built by Aqsa Rani:
- Reads Architecture_Documentation.md and Architecture_View.md as input
- Parses them into structured JSON using Python regex
- Calls OpenRouter AI API (Claude Haiku model) to generate each file
- Automatically writes 17+ files forming a complete microservices project

Connect to Prof. Peng Liang's research at Wuhan University:
- Paper: "Design, Monitoring, and Testing of Microservices Systems: The Practitioners' Perspective" (JSS 2021)
- The Space Fractions system exemplifies the microservices challenges studied in that paper
- The agent automates the translation from architecture documentation to code
- This represents Intelligent Software Engineering: AI assisting the software development process

Report sections:
1. Introduction: what is a Code Agent and why it matters
2. System architecture of the agent itself
3. How it works step by step
4. Connection to microservices research
5. Challenges faced and how they were solved
6. Limitations and future work
7. Conclusion

Write genuinely and thoughtfully in academic English."""
        ),

    ]

    print(f"\n[3/5] Generating {len(files_to_generate)} files...\n")

    success_count = 0
    fail_count    = 0

    for i, (filepath, prompt) in enumerate(files_to_generate, 1):

        filename = os.path.basename(filepath)
        print(f"  [{i:02d}/{len(files_to_generate)}] {filename}...", end=" ", flush=True)

        try:
            content = ask_ai(prompt, max_tokens=2500)
            create_file(filepath, content)
            success_count += 1
            time.sleep(2)   # 2-second pause between calls — avoids rate limits

        except Exception as e:
            print(f"\n    ✗ FAILED: {e}")
            fail_count += 1
            time.sleep(3)   # wait longer after an error

    return success_count, fail_count


# ── CREATE .GITIGNORE ─────────────────────────────────────────────────────────
def create_gitignore():
    content = """# NEVER upload these to GitHub
.env
*.env

# Python cache
__pycache__/
*.pyc

# Virtual environment
venv/
env/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Auto-generated
architecture_parsed.json
"""
    with open(".gitignore", "w") as f:
        f.write(content)
    print("    ✓ .gitignore")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():

    header("SPACE FRACTIONS CODE AGENT")
    print("  Architecture docs  →  Complete microservices project")
    print("  Powered by OpenRouter API (Claude Haiku)")

    # Check API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("\nERROR: OPENROUTER_API_KEY not found!")
        print("Your .env file must contain:")
        print("  OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        exit(1)
    print(f"\n  ✓ API key found  (...{api_key[-8:]})")
    print(f"  ✓ Working folder: {os.getcwd()}")

    # Quick test — call API with a tiny prompt before generating everything
    print("\n  Testing API connection...")
    try:
        test_response = ask_ai("Say only: API connection successful", max_tokens=10)
        print(f"  ✓ API test passed: {test_response.strip()}")
    except Exception as e:
        print(f"\n  ✗ API test FAILED: {e}")
        print("\n  Check:")
        print("  1. Your API key in .env is correct")
        print("  2. You have internet connection")
        print("  3. Your OpenRouter account has credits")
        exit(1)

    # Create output folder
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"  ✓ Output folder: {OUTPUT_DIR}/")

    # Run all steps
    files  = read_architecture_files()
    parsed = parse_architecture(files)
    success, fail = generate_project(parsed)

    print("\n[4/5] Creating .gitignore...")
    create_gitignore()

    # Summary
    header("COMPLETED")
    print(f"\n  Files generated: {success}")
    if fail:
        print(f"  Files failed:    {fail}")

    print("\n  Generated project structure:")
    for root, dirs, files_list in os.walk(OUTPUT_DIR):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        level   = root.replace(OUTPUT_DIR, "").count(os.sep)
        indent  = "  " * (level + 1)
        print(f"{indent}📁 {os.path.basename(root)}/")
        for fn in sorted(files_list):
            print(f"{indent}  📄 {fn}")

    print("\n" + "="*55)
    print("  NEXT: upload to GitHub and send link to Prof. Liang")
    print("="*55)


if __name__ == "__main__":
    main()