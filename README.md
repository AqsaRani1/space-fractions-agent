# Space Fractions Code Agent

A Python-based **Code Agent** that automatically generates a complete microservices project from architectural documentation using Claude AI.

Built as part of an evaluation task for Prof. Peng Liang's research group at Wuhan University.

---

## What is a Code Agent?

A Code Agent is a program that uses AI to automate software development tasks. Instead of a developer manually reading an architecture document and writing code files one by one, the agent does this automatically:

```
Architecture Documentation (.md)  →  [Code Agent]  →  Complete Project Files
```

This agent reads the Space Fractions system architecture, understands it, and generates all starter files — services, database schemas, Docker configuration, tests, and documentation.

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT PIPELINE                        │
│                                                          │
│  1. READ         Architecture_Documentation.md           │
│                  Architecture_View.md                    │
│       ↓                                                  │
│  2. PARSE        Extract components, tech stack,         │
│                  architecture style → JSON               │
│       ↓                                                  │
│  3. GENERATE     For each required file:                 │
│                  → Build prompt describing the file      │
│                  → Call Claude AI via OpenRouter API     │
│                  → Save generated content to disk        │
│       ↓                                                  │
│  4. OUTPUT       18 files forming a complete             │
│                  microservices project                   │
└─────────────────────────────────────────────────────────┘
```

---

## Input Files

| File | Description |
|------|-------------|
| `Architecture_Documentation.md` | Full architectural specification for Space Fractions system |
| `Architecture_View.md` | 13 UML diagrams (Use Case, Class, Sequence, Deployment, etc.) |

These files were provided by Prof. Peng Liang as part of Task 1.

---

## Generated Output

The agent produces a complete `generated_project/` folder:

```
generated_project/
├── README.md                        ← Project overview
├── requirements.txt                 ← Python dependencies
├── docker-compose.yml               ← Run all services locally
├── openapi.yaml                     ← API documentation (OpenAPI 3.0)
├── traceability_matrix.csv          ← Requirements traceability
├── AGENT_REPORT.md                  ← Technical report
├── game-component/
│   ├── app.py                       ← Flask service (game logic)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── question-component/
│   ├── app.py                       ← Flask service (fraction questions)
│   └── requirements.txt
├── user-component/
│   ├── app.py                       ← Flask service (authentication)
│   └── requirements.txt
├── sql/
│   ├── game_ddl.sql                 ← Games & scores tables
│   └── question_ddl.sql             ← Questions & answers tables
└── tests/
    ├── test_game.py                 ← Unit tests for GameComponent
    └── test_questions.py            ← Unit tests for QuestionComponent
```

---

## About Space Fractions

Space Fractions is an educational web game for 6th grade students to practice fraction-solving skills. The system follows a **microservices architecture** with three independent services:

| Service | Port | Responsibility |
|---------|------|----------------|
| GameComponent | 3000 | Game logic, scoring, session management |
| QuestionComponent | 3001 | Fraction questions, answer checking |
| UserComponent | 3002 | Student registration and login |

---

## Setup and Running

### Prerequisites
- Python 3.8 or higher
- An OpenRouter API key (free at openrouter.ai)

### Install dependencies
```bash
pip install requests python-dotenv
```

### Configure API key
Create a `.env` file in the project root:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Run the agent
```bash
python agent.py
```

The agent will:
1. Read both architecture files
2. Parse them into structured JSON
3. Call Claude AI 18 times — once per file
4. Save all generated files to `generated_project/`

Total runtime: approximately 3–5 minutes.

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Agent language | Python 3.12 |
| AI model | Claude 3 Haiku (via OpenRouter) |
| API library | requests |
| Generated services | Python Flask |
| Generated database | PostgreSQL 14 |
| Generated cache | Redis 6 |
| Generated containers | Docker |

---

## Connection to Research

This project relates directly to Prof. Peng Liang's paper:

> **"Design, Monitoring, and Testing of Microservices Systems: The Practitioners' Perspective"**
> Journal of Systems and Software, 2021

The Space Fractions system exemplifies the microservices architecture challenges studied in that paper — service decomposition, inter-service communication, and distributed data management. This Code Agent demonstrates **Intelligent Software Engineering**: using AI to automate the translation from architecture documentation into working code.

---

## Author

**Aqsa Rani**
University of Lahore, Pakistan | CGPA 3.54/4.0
aqsarani33442@gmail.com | [GitHub](https://github.com/AqsaRani1)

*Submitted for evaluation — Prof. Peng Liang's Research Group, Wuhan University*
