# Architecture-Driven Code Agent

**Author:** Aqsa Rani · University of Lahore, Pakistan  
**Submitted to:** Prof. Peng Liang · Wuhan University  
**Task:** Task 1 — Build a simple Code Agent

---

## What This Is

A generic **Code Agent** written in Python that reads any software architecture document and automatically generates a complete, working project from it.

The agent is not specific to Space Fractions. It works for **any architecture document** — it reads the document, understands the system using AI, decides what files to create, and generates them.

---

## How It Works

```
Architecture_Documentation.md  ──┐
                                  ├──► Code Agent ──► generated_project/
Architecture_View.md          ──┘
```

The agent runs a 6-step pipeline:

| Step | Action | Output |
|------|--------|--------|
| 1 | Read both input files | raw text |
| 2 | AI reads Architecture_Documentation.md → structured JSON | `architecture_parsed.json` |
| 3 | AI extracts UML diagrams from Architecture_View.md | `uml_parsed.json` |
| 4 | AI decides what files to generate based on the architecture | `generation_plan.json` |
| 5 | For each file: AI generates content using JSON + UML as inputs | `generated_project/` |
| 6 | Generate traceability matrix | `generated_project/traceability_matrix.csv` |

---

## Agent Inputs

The task specifies two inputs:

**Input 1 — Architecture_Documentation.md**  
The AI reads this entirely and extracts a structured JSON object containing the system name, components, technology stack per component, requirements (FR/NFR/ASR), component interactions, and quality attributes. This JSON is saved as `architecture_parsed.json` and passed into every subsequent AI call.

**Input 2 — Architecture_View.md**  
The AI extracts all PlantUML diagram blocks and interprets what each one shows — component dependencies, interaction flows, deployment nodes, actors. This is saved as `uml_parsed.json` and used to give each generated file the correct structural context.

---

## Why This Is Generic

The agent has **no hardcoded component names, ports, languages, or file lists.**

- Component names come from the AI reading the document
- Languages come from the technology stack in the architecture
- The file list is decided by the AI based on what the architecture requires
- Folder names are derived from component names as the AI finds them

If you replace the two input `.md` files with a different system's architecture, the agent generates that system's project instead.

---

## Repository Structure

```
space-fractions-agent/
│
├── agent.py                        ← The Code Agent (this is what you run)
├── Architecture_Documentation.md   ← Input 1: system architecture
├── Architecture_View.md            ← Input 2: UML diagrams
├── .env                            ← Your API key (not committed)
├── .gitignore
│
├── architecture_parsed.json        ← Generated: structured JSON from Input 1
├── uml_parsed.json                 ← Generated: structured UML from Input 2
├── generation_plan.json            ← Generated: AI-decided file plan
│
└── generated_project/              ← Generated: complete project output
    ├── README.md
    ├── docker-compose.yml
    ├── openapi.yaml
    ├── traceability_matrix.csv
    ├── game-component/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── Dockerfile
    ├── question-component/
    │   ├── app.py
    │   └── requirements.txt
    ├── user-component/
    │   ├── app.py
    │   └── requirements.txt
    ├── sql/
    └── tests/
```

---

## Setup

**Requirements:**
- Python 3.8 or higher
- An OpenRouter API key (free at [openrouter.ai](https://openrouter.ai))

**Install dependencies:**
```bash
pip install requests python-dotenv
```

**Create `.env` file:**
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Run:**
```bash
python agent.py
```

---

## Example Run Output

```
============================================================
  ARCHITECTURE-DRIVEN CODE AGENT
============================================================
  Generic: works for ANY architecture document
  Input 1: Architecture_Documentation.md → structured JSON
  Input 2: Architecture_View.md           → UML diagram syntax
  Output:  generated_project/  (structure decided by AI)
  Model:   anthropic/claude-3-haiku via OpenRouter

  ✓ API key (...abc12345)
  ✓ Working directory: D:\Task1

  Testing API connection...
  ✓ Connected: ready

[1/5] Reading input files...
  ✓ Architecture_Documentation.md (10,140 chars)
  ✓ Architecture_View.md          (4,020 chars)

[2/5] Converting documentation to structured JSON (AI-assisted)...
  ✓ System:       Space Fractions
  ✓ Style:        Microservices
  ✓ Components:   3 found
  ✓ Requirements: 3 found
  ✓ Interactions: 4 found
  ✓ Saved:        architecture_parsed.json

[3/5] Extracting UML diagrams...
  ✓ Found 13 PlantUML diagrams
  ✓ Saved: uml_parsed.json

[4/5] Planning project structure (AI decides what to build)...
  ✓ Agent planned 18 files to generate

[5/5] Generating project files...
  [01/18] generated_project/README.md
  [02/18] generated_project/docker-compose.yml
  ...

============================================================
  COMPLETED
============================================================
  System analysed:    Space Fractions
  Components found:   3
  Requirements found: 3
  Files generated:    18
```

---

## Research Connection

This agent was built after studying:
- [claw-code](https://github.com/ultraworkers/claw-code) — open-source Claude Code implementation
- [how-claude-code-works](https://github.com/Windy3f3f3f3f/how-claude-code-works) — analysis of Claude Code internals
- [anthropics/claude-code](https://github.com/anthropics/claude-code) — official Claude Code repository

**Key insight from this research:** Claude Code operates as an agent loop — it receives a task description, uses AI to reason about what actions to take, executes those actions (file creation, code generation), and iterates. This agent implements a focused version of that loop for translating architecture documentation into working code.

This relates directly to Prof. Liang's research paper:

> *"Design, Monitoring, and Testing of Microservices Systems: The Practitioners' Perspective"*  
> Peng Liang et al. — Journal of Systems and Software, 2021

The Space Fractions system used as the test case is a microservices system — exactly the architectural style studied in that paper. The agent demonstrates **Intelligent Software Engineering**: using AI to automate the translation from architecture decisions into implementation, reducing the manual effort that software practitioners currently invest in this step.

---

## Traceability

Every generated file in `generated_project/` traces back to at least one requirement from the architecture document. The `traceability_matrix.csv` maps each FR/NFR/ASR requirement to the file that implements or tests it.

---

## Author

**Aqsa Rani**  
University of Lahore, Pakistan | CGPA 3.54/4.0  
[aqsarani33442@gmail.com](mailto:aqsarani33442@gmail.com) | [GitHub](https://github.com/AqsaRani1)