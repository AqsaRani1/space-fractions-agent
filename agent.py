"""
Generic Architecture-Driven Code Agent
=======================================
Author:      Aqsa Rani
University:  University of Lahore, Pakistan

Description:
    A generic Code Agent that works for ANY software architecture.
    It reads architecture documentation and UML diagrams, deeply understands
    the system, then autonomously decides what files to generate and generates them.

    This agent is:
    - Architecture-aware: understands component relationships, not just names
    - Dynamic: determines file list, tech stack, APIs from the docs themselves
    - Adaptive: works for any architecture doc, not just Space Fractions
    - Traceable: every generated file links back to a requirement

Input:
    - Architecture_Documentation.md  (any architecture document)
    - Architecture_View.md           (any UML view file)

Output:
    - architecture_parsed.json       (structured input for the agent)
    - uml_parsed.json                (structured UML input)
    - generated_project/             (complete project, structure decided by AI)

    Root-level files (standard project conventions):
    - .gitignore
    - architecture_parsed.json
    - uml_parsed.json
    - generation_plan.json

Usage:
    pip install requests python-dotenv
    Set OPENROUTER_API_KEY in .env
    python agent.py
"""

import os
import re
import json
import time
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
OUTPUT_DIR = "generated_project"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-3-haiku"
DEFAULT_LANG = "python"  # used only when no language is specified in docs
RATE_LIMIT_DELAY = 2  # seconds between API calls

# Token limits — kept conservative so the agent runs on a free/low-credit account.
# claude-3-haiku pricing: $0.25 / 1M input tokens, $1.25 / 1M output tokens.
# Raise these values if you have more credits.
MAX_TOKENS_JSON = 2000  # Step 2: architecture → JSON
MAX_TOKENS_UML = 1500  # Step 3: UML extraction
MAX_TOKENS_PLAN = 2000  # Step 4: project planning
MAX_TOKENS_FILE = 1500  # Step 5: each generated file
MAX_TOKENS_TRACE = 1000  # Step 6: traceability CSV


def header(text):
    print(f"\n{'='*60}\n  {text}\n{'='*60}")


# ── STEP 1: READ INPUT FILES ────────────────────────────────────────────────────
def read_input_files():
    """Read Architecture_Documentation.md and Architecture_View.md."""

    print("\n[1/5] Reading input files...")

    missing = [
        f
        for f in ["Architecture_Documentation.md", "Architecture_View.md"]
        if not os.path.exists(f)
    ]
    if missing:
        raise FileNotFoundError(
            f"Required file(s) not found in {os.getcwd()}: {', '.join(missing)}"
        )

    with open("Architecture_Documentation.md", "r", encoding="utf-8") as f:
        doc = f.read()
    with open("Architecture_View.md", "r", encoding="utf-8") as f:
        view = f.read()

    print(f"  ✓ Architecture_Documentation.md ({len(doc):,} chars)")
    print(f"  ✓ Architecture_View.md          ({len(view):,} chars)")
    return doc, view


# ── STEP 2: BUILD STRUCTURED JSON FROM DOCUMENTATION ──────────────────────────
def build_architecture_json(doc, ai_call):
    """
    Convert Architecture_Documentation.md into structured JSON.

    Uses AI to deeply understand the document — not just regex parsing.
    The AI reads the entire document and extracts:
      - system identity
      - all components with their relationships
      - technology decisions (languages, frameworks, databases)
      - requirements (FR, NFR, ASR) with traceability
      - API contracts between components
      - deployment topology

    This JSON becomes Input 1 for all subsequent file generation.
    Saved to: architecture_parsed.json  (root directory)
    """

    print("\n[2/5] Converting documentation to structured JSON (AI-assisted)...")

    prompt = f"""You are analyzing a software architecture document.
Read this document carefully and extract ALL information into structured JSON.

DOCUMENT:
{doc}

Return a JSON object with this exact structure (fill ALL fields from the document,
use null only if genuinely not mentioned):

{{
  "system": {{
    "name": "exact system name from document",
    "purpose": "what the system does in one sentence",
    "architectural_style": "e.g. Microservices / Monolith / Layered",
    "deployment": "e.g. Cloud / On-premise / Hybrid",
    "language_default": "primary language mentioned, or null if not specified"
  }},
  "components": [
    {{
      "name": "exact component name",
      "purpose": "what this component is responsible for",
      "language": "language from doc, or null if not specified",
      "framework": "framework from doc, or null",
      "database": "database from doc, or null",
      "cache": "cache system from doc, or null",
      "port": "port number from doc, or null",
      "exposes_apis": ["list of API endpoints this component exposes"],
      "calls": ["list of other components this component calls"],
      "owns_data": ["list of data entities this component owns"],
      "requirements_served": ["list of FR/NFR/ASR IDs this component serves"]
    }}
  ],
  "requirements": [
    {{
      "id": "e.g. FR-1",
      "type": "FR or NFR or ASR",
      "description": "requirement text",
      "component": "which component fulfils this",
      "test_type": "unit/integration/e2e/load/security",
      "artifact": "which generated file should implement/test this"
    }}
  ],
  "interactions": [
    {{
      "from_component": "caller",
      "to_component": "callee",
      "protocol": "REST/gRPC/message queue/etc",
      "purpose": "why this call happens"
    }}
  ],
  "deliverables": [
    {{
      "filename": "exact filename from deliverables section",
      "type": "code/config/schema/test/doc",
      "component": "which component or root"
    }}
  ],
  "quality_attributes": {{
    "performance": "any performance requirements mentioned",
    "security": "any security requirements mentioned",
    "availability": "any availability requirements mentioned",
    "scalability": "any scalability requirements mentioned"
  }}
}}

Return ONLY the JSON object. No explanation. No markdown."""

    response = ai_call(prompt, max_tokens=MAX_TOKENS_JSON)

    try:
        clean = re.sub(r"^```[\w]*\n?", "", response.strip())
        clean = re.sub(r"\n?```$", "", clean)
        arch_json = json.loads(clean)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            arch_json = json.loads(match.group())
        else:
            print("  WARNING: Could not parse AI JSON response, using basic extraction")
            arch_json = basic_json_extraction(doc)

    # Saved to root directory — it is an agent artefact, not project output
    with open("architecture_parsed.json", "w", encoding="utf-8") as f:
        json.dump(arch_json, f, indent=2)

    n_comp = len(arch_json.get("components", []))
    n_req = len(arch_json.get("requirements", []))
    n_int = len(arch_json.get("interactions", []))
    sname = arch_json.get("system", {}).get("name", "Unknown")
    sstyle = arch_json.get("system", {}).get("architectural_style", "Unknown")

    print(f"  ✓ System:       {sname}")
    print(f"  ✓ Style:        {sstyle}")
    print(f"  ✓ Components:   {n_comp} found")
    print(f"  ✓ Requirements: {n_req} found")
    print(f"  ✓ Interactions: {n_int} found")
    print(f"  ✓ Saved:        architecture_parsed.json  (root)")

    return arch_json


def basic_json_extraction(doc):
    """Fallback: basic regex extraction if AI JSON parsing fails."""
    style_m = re.search(r"architectural style:\s*([^\n]+)", doc, re.IGNORECASE)
    name_m = re.search(r"#\s+(.+)", doc)
    return {
        "system": {
            "name": name_m.group(1).strip() if name_m else "Unknown System",
            "architectural_style": style_m.group(1).strip() if style_m else "Unknown",
            "language_default": None,
        },
        "components": [],
        "requirements": [],
        "interactions": [],
        "deliverables": [],
        "quality_attributes": {},
    }


# ── STEP 3: EXTRACT UML DIAGRAMS ────────────────────────────────────────────────
def extract_uml_diagrams(view, ai_call):
    """
    Extract structured UML diagram data from Architecture_View.md.

    Two-stage process:
    1. Extract raw PlantUML blocks (syntax parsing)
    2. Use AI to understand what each diagram shows (semantic understanding)

    Saved to: uml_parsed.json  (root directory)
    """

    print("\n[3/5] Extracting UML diagrams (Architecture_View.md)...")

    raw_diagrams = []
    blocks = re.findall(r"@startuml\s*(\w*)(.*?)@enduml", view, re.DOTALL)

    for name, syntax in blocks:
        raw_diagrams.append(
            {
                "name": (
                    name.strip() if name.strip() else f"diagram_{len(raw_diagrams) + 1}"
                ),
                "syntax": syntax.strip(),
            }
        )

    print(f"  ✓ Found {len(raw_diagrams)} PlantUML diagrams")

    if raw_diagrams:
        diagrams_text = "\n\n".join(
            f"=== {d['name']} ===\n{d['syntax']}" for d in raw_diagrams
        )

        prompt = f"""Analyze these UML diagrams and extract structured information.

{diagrams_text}

Return a JSON object:
{{
  "diagrams": [
    {{
      "name": "diagram name",
      "type": "UseCase/Class/Sequence/State/Activity/Component/Deployment/Container",
      "shows": "one sentence: what this diagram shows",
      "actors": ["list of actors/participants"],
      "relationships": ["list of key relationships shown"],
      "syntax": "the original PlantUML syntax"
    }}
  ],
  "system_insights": {{
    "actors": ["all external actors in the system"],
    "main_flows": ["key interaction flows between components"],
    "component_dependencies": ["component A depends on component B", ...],
    "deployment_nodes": ["list of deployment nodes/servers"]
  }}
}}

Return ONLY the JSON object."""

        response = ai_call(prompt, max_tokens=MAX_TOKENS_UML)
        try:
            clean = re.sub(r"^```[\w]*\n?", "", response.strip())
            clean = re.sub(r"\n?```$", "", clean)
            uml_data = json.loads(clean)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"  WARNING: UML parse failed ({e}), using raw diagram fallback")
            uml_data = {
                "diagrams": raw_diagrams,
                "system_insights": {
                    "actors": [],
                    "main_flows": [],
                    "component_dependencies": [],
                    "deployment_nodes": [],
                },
            }
    else:
        uml_data = {"diagrams": [], "system_insights": {}}

    # Saved to root directory — agent artefact
    with open("uml_parsed.json", "w", encoding="utf-8") as f:
        json.dump(uml_data, f, indent=2)

    for d in uml_data.get("diagrams", []):
        print(
            f"      - {d.get('name','?')} ({d.get('type','?')}): "
            f"{d.get('shows','')[:60]}"
        )

    print(f"  ✓ Saved: uml_parsed.json  (root)")
    return uml_data


# ── STEP 4: PLAN THE PROJECT STRUCTURE ─────────────────────────────────────────
def plan_project(arch_json, uml_data, ai_call):
    """
    Use AI to decide WHAT files to generate based on the architecture.

    All generated files are placed under OUTPUT_DIR (generated_project/).
    The file plan itself is saved as generation_plan.json in the root directory.

    Returns a list of file plans: [{path, purpose, component, requirements}]
    """

    print("\n[4/5] Planning project structure (AI decides what to build)...")

    arch_summary = json.dumps(arch_json, indent=2)
    uml_summary = json.dumps(uml_data.get("system_insights", {}), indent=2)
    default_lang = arch_json.get("system", {}).get("language_default") or DEFAULT_LANG

    prompt = f"""You are planning the implementation of a software system.
You have two inputs:

=== INPUT 1: ARCHITECTURE JSON (from Architecture_Documentation.md) ===
{arch_summary}

=== INPUT 2: UML SYSTEM INSIGHTS (from Architecture_View.md) ===
{uml_summary}

Based on these inputs, decide what files should be generated for this project.

Rules:
1. ALL files must be placed under the "{OUTPUT_DIR}/" prefix.
2. Use the language specified for each component in the architecture JSON.
   If a component has no language specified, use: {default_lang}
3. Determine file extensions from the language (Python → .py, Node.js → .js, Java → .java, etc.)
4. Create one service folder per component under {OUTPUT_DIR}/
5. Every requirement must be traceable to at least one file
6. Include: service code, dependency files, Dockerfile, SQL/schema, tests, API spec, README
7. Do NOT hardcode Space Fractions specific names — read everything from the architecture

Return a JSON array of files to generate:
[
  {{
    "path": "{OUTPUT_DIR}/relative/path/to/file.ext",
    "purpose": "what this file does",
    "component": "which component this belongs to, or 'root'",
    "language": "exact language to use",
    "requirements_traced": ["FR-1", "NFR-1"],
    "depends_on_components": ["ComponentB"],
    "uml_diagrams_used": ["DiagramName"],
    "generation_prompt_hint": "key things to include when generating this file"
  }}
]

Return ONLY the JSON array. Be thorough — include all necessary files."""

    response = ai_call(prompt, max_tokens=MAX_TOKENS_PLAN)

    try:
        clean = re.sub(r"^```[\w]*\n?", "", response.strip())
        clean = re.sub(r"\n?```$", "", clean)
        if clean.strip().startswith("["):
            file_plan = json.loads(clean)
        else:
            parsed = json.loads(clean)
            file_plan = parsed if isinstance(parsed, list) else parsed.get("files", [])
    except Exception as e:
        print(f"  WARNING: Could not parse file plan ({e}), using fallback")
        file_plan = build_fallback_plan(arch_json, default_lang)

    # Guarantee every path starts with OUTPUT_DIR/
    for fp in file_plan:
        if not fp.get("path", "").startswith(OUTPUT_DIR + "/"):
            fp["path"] = f"{OUTPUT_DIR}/{fp['path'].lstrip('/')}"

    print(f"  ✓ Agent planned {len(file_plan)} files to generate")
    for fp in file_plan:
        req_ids = ", ".join(fp.get("requirements_traced", []))
        print(f"      {fp['path']}  [{req_ids}]")

    # Saved to root directory — agent artefact
    with open("generation_plan.json", "w", encoding="utf-8") as f:
        json.dump(file_plan, f, indent=2)
    print(f"  ✓ Saved: generation_plan.json  (root)")

    return file_plan


def build_fallback_plan(arch_json, default_lang):
    """Build a minimal file plan (inside OUTPUT_DIR) if AI planning fails."""

    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "java": ".java",
        "go": ".go",
        "ruby": ".rb",
        "php": ".php",
    }
    ext = ext_map.get(default_lang.lower(), ".py")

    plan = [
        {
            "path": f"{OUTPUT_DIR}/README.md",
            "purpose": "Project overview",
            "component": "root",
            "language": "markdown",
            "requirements_traced": [],
            "generation_prompt_hint": "full project README",
        },
        {
            "path": f"{OUTPUT_DIR}/docker-compose.yml",
            "purpose": "Local dev setup",
            "component": "root",
            "language": "yaml",
            "requirements_traced": [],
            "generation_prompt_hint": "docker compose for all services",
        },
    ]

    lang_ext = {
        "node.js": ".js",
        "python": ".py",
        "java": ".java",
        "flask": ".py",
        "express.js": ".js",
        "spring boot": ".java",
    }

    for comp in arch_json.get("components", []):
        cname = comp["name"].lower().replace(" ", "-")
        lang = comp.get("language") or default_lang
        real_ext = lang_ext.get(lang.lower(), ext)

        dep_file = (
            f"{OUTPUT_DIR}/{cname}/requirements.txt"
            if "python" in lang.lower()
            else f"{OUTPUT_DIR}/{cname}/package.json"
        )

        plan += [
            {
                "path": f"{OUTPUT_DIR}/{cname}/app{real_ext}",
                "purpose": f"Main service for {comp['name']}",
                "component": comp["name"],
                "language": lang,
                "requirements_traced": comp.get("requirements_served", []),
                "generation_prompt_hint": comp.get("purpose", ""),
            },
            {
                "path": dep_file,
                "purpose": "Dependencies",
                "component": comp["name"],
                "language": lang,
                "requirements_traced": [],
                "generation_prompt_hint": f"dependency file for {lang}",
            },
            {
                "path": f"{OUTPUT_DIR}/{cname}/Dockerfile",
                "purpose": "Container definition",
                "component": comp["name"],
                "language": "dockerfile",
                "requirements_traced": [],
                "generation_prompt_hint": f"Dockerfile for {lang} service",
            },
        ]

    return plan


# ── STEP 5: GENERATE EACH FILE ──────────────────────────────────────────────────
def generate_files(file_plan, arch_json, uml_data, ai_call):
    """
    Generate each planned file using AI.

    For every file:
    - Pass the full architecture JSON as Input 1
    - Pass the relevant UML diagrams as Input 2
    - Include specific requirements this file must trace
    - Include component relationships this file must respect
    - Let AI generate the content based on these inputs

    All files are written inside OUTPUT_DIR (generated_project/).
    """

    header("GENERATING PROJECT FILES")

    arch_context = json.dumps(arch_json, indent=2)

    uml_index = {
        d.get("name", ""): d.get("syntax", "") for d in uml_data.get("diagrams", [])
    }
    uml_insights = json.dumps(uml_data.get("system_insights", {}), indent=2)

    success = 0
    failed = 0

    for i, file_spec in enumerate(file_plan, 1):

        filepath = file_spec.get("path", "")
        purpose = file_spec.get("purpose", "")
        component = file_spec.get("component", "root")
        language = file_spec.get("language", DEFAULT_LANG)
        req_ids = file_spec.get("requirements_traced", [])
        hint = file_spec.get("generation_prompt_hint", "")
        dep_comps = file_spec.get("depends_on_components", [])
        uml_names = file_spec.get("uml_diagrams_used", [])

        if not filepath:
            continue

        print(f"\n  [{i:02d}/{len(file_plan)}] {filepath}")
        print(f"    Component: {component} | Language: {language}")
        if req_ids:
            print(f"    Traces:    {', '.join(req_ids)}")

        # Collect relevant UML syntax for this file
        relevant_uml = ""
        for uml_name in uml_names:
            if uml_name in uml_index:
                relevant_uml += f"\n=== {uml_name} ===\n{uml_index[uml_name]}\n"
        if not relevant_uml:
            relevant_uml = uml_insights

        comp_data = next(
            (c for c in arch_json.get("components", []) if c.get("name") == component),
            {},
        )
        traced_reqs = [
            r for r in arch_json.get("requirements", []) if r.get("id") in req_ids
        ]
        interactions = [
            ix
            for ix in arch_json.get("interactions", [])
            if ix.get("from_component") == component
            or ix.get("to_component") == component
        ]

        prompt = f"""Generate the file: {filepath}
Purpose: {purpose}
Language: {language}
{f"Additional hints: {hint}" if hint else ""}

=== INPUT 1: ARCHITECTURE JSON (from Architecture_Documentation.md) ===
SYSTEM:
{json.dumps(arch_json.get("system", {}), indent=2)}

THIS COMPONENT ({component}):
{json.dumps(comp_data, indent=2)}

COMPONENT INTERACTIONS:
{json.dumps(interactions, indent=2)}

REQUIREMENTS THIS FILE MUST SATISFY:
{json.dumps(traced_reqs, indent=2)}

QUALITY ATTRIBUTES:
{json.dumps(arch_json.get("quality_attributes", {}), indent=2)}

=== INPUT 2: UML DIAGRAM SYNTAX (from Architecture_View.md) ===
{relevant_uml}

=== GENERATION RULES ===
1. Use {language} as the programming language
2. Implement all functionality implied by the component's purpose and requirements
3. Respect all component interactions shown in the architecture and UML
4. Include proper error handling
5. Add comments referencing requirements (e.g. # FR-1: Play game)
6. Do NOT use hardcoded values — read everything from the architecture context above
7. If this is a service file, implement ALL endpoints listed in the component's exposes_apis
8. If this is a test file, write tests for ALL requirements in requirements_traced

Return ONLY the file content. No markdown code blocks. No explanations."""

        try:
            content = ai_call(prompt, max_tokens=MAX_TOKENS_FILE)
            content = re.sub(r"^```[\w]*\n?", "", content.strip())
            content = re.sub(r"\n?```$", "", content)
            write_file(filepath, content)
            print(f"    ✓ Generated successfully")
            success += 1
        except Exception as e:
            print(f"    ✗ Failed: {e}")
            failed += 1

        time.sleep(RATE_LIMIT_DELAY)

    return success, failed


# ── FILE I/O HELPERS ────────────────────────────────────────────────────────────
def write_file(filepath, content):
    """Write content to filepath, creating parent directories as needed."""
    folder = os.path.dirname(filepath)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


# ── GENERATE TRACEABILITY REPORT ────────────────────────────────────────────────
def generate_traceability_report(arch_json, file_plan, ai_call):
    """
    Generate a traceability matrix CSV showing every requirement is covered.
    Saved inside OUTPUT_DIR as part of the project deliverables.
    """
    print("\n  Generating traceability report...")

    prompt = f"""Generate a traceability matrix CSV for this system.

Architecture requirements:
{json.dumps(arch_json.get("requirements", []), indent=2)}

Generated files and what they trace:
{json.dumps(
    [{"file": f["path"], "traces": f.get("requirements_traced", [])} for f in file_plan],
    indent=2
)}

Columns: Requirement ID, Type, Description, Component, Implementation File, Test File, Status
Every requirement from the architecture JSON must appear.
Return CSV content only."""

    content = ai_call(prompt, max_tokens=MAX_TOKENS_TRACE)
    content = re.sub(r"^```[\w]*\n?", "", content.strip())
    content = re.sub(r"\n?```$", "", content)

    dest = f"{OUTPUT_DIR}/traceability_matrix.csv"
    write_file(dest, content)
    print(f"    ✓ {dest}")


# ── CREATE ROOT-LEVEL .GITIGNORE ────────────────────────────────────────────────
def create_gitignore():
    """
    Write .gitignore to the project root (not inside generated_project/).
    This is standard convention: .gitignore belongs at the repo root.
    """
    content = (
        "# API keys — never commit\n"
        ".env\n"
        "*.env\n\n"
        "# Python cache\n"
        "__pycache__/\n"
        "*.pyc\n\n"
        "# Virtual environments\n"
        "venv/\n"
        "env/\n\n"
        "# IDE\n"
        ".vscode/\n"
        ".idea/\n\n"
        "# OS\n"
        ".DS_Store\n"
        "Thumbs.db\n\n"
        "# Agent intermediary files (root)\n"
        "architecture_parsed.json\n"
        "uml_parsed.json\n"
        "generation_plan.json\n"
    )
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(content)
    print("    ✓ .gitignore  (root)")


# ── OPENROUTER API CALLER ──────────────────────────────────────────────────────
def make_ai_caller():
    """
    Returns a reusable callable that sends prompts to OpenRouter / Claude.
    Raises EnvironmentError immediately if the API key is missing.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "OPENROUTER_API_KEY is not set. Add it to your .env file."
        )

    def call(prompt, max_tokens=1500):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Architecture-Driven Code Agent",
        }
        body = {
            "model": MODEL,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert software architect and developer. "
                        "You receive structured architecture JSON and UML diagrams as input. "
                        "You generate production-quality code that is fully consistent with "
                        "the architecture. Return ONLY file content — no markdown, no explanation."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        response = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=90)
        if response.status_code != 200:
            raise RuntimeError(
                f"API error {response.status_code}: {response.text[:300]}"
            )
        return response.json()["choices"][0]["message"]["content"]

    return call


# ── MAIN ────────────────────────────────────────────────────────────────────────
def main():

    header("ARCHITECTURE-DRIVEN CODE AGENT")
    print("  Generic: works for ANY architecture document")
    print("  Input 1: Architecture_Documentation.md → structured JSON")
    print("  Input 2: Architecture_View.md           → UML diagram syntax")
    print(f"  Output:  {OUTPUT_DIR}/  (structure decided by AI)")
    print(f"  Model:   {MODEL} via OpenRouter")

    # Create AI caller — raises EnvironmentError if key is missing
    try:
        ai_call = make_ai_caller()
    except EnvironmentError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    api_key = os.environ["OPENROUTER_API_KEY"]
    print(f"\n  ✓ API key (...{api_key[-8:]})")
    print(f"  ✓ Working directory: {os.getcwd()}")

    # Test connection
    print("\n  Testing API connection...")
    try:
        test = ai_call("Reply with the single word: ready", max_tokens=5)
        print(f"  ✓ Connected: {test.strip()}")
    except RuntimeError as e:
        print(f"  ✗ Connection failed: {e}")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # ── Pipeline ────────────────────────────────────────────────────────────────

    # Step 1: Read both input files
    try:
        doc, view = read_input_files()
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

    # Step 2: Convert Architecture_Documentation.md → structured JSON  [root]
    arch_json = build_architecture_json(doc, ai_call)

    # Step 3: Extract UML diagrams from Architecture_View.md           [root]
    uml_data = extract_uml_diagrams(view, ai_call)

    # Step 4: AI plans the project structure                           [root]
    file_plan = plan_project(arch_json, uml_data, ai_call)

    # Step 5: Generate all files inside OUTPUT_DIR
    success, failed = generate_files(file_plan, arch_json, uml_data, ai_call)

    # Step 6: Traceability report inside OUTPUT_DIR
    generate_traceability_report(arch_json, file_plan, ai_call)

    # Step 7: .gitignore at project root
    create_gitignore()

    # ── Summary ─────────────────────────────────────────────────────────────────
    header("COMPLETED")

    system_name = arch_json.get("system", {}).get("name", "Unknown")
    n_comp = len(arch_json.get("components", []))
    n_req = len(arch_json.get("requirements", []))

    print(f"\n  System analysed:    {system_name}")
    print(f"  Components found:   {n_comp}")
    print(f"  Requirements found: {n_req}")
    print(f"  Files generated:    {success}")
    if failed:
        print(f"  Files failed:       {failed}")

    print(f"\n  Root-level files (agent artefacts + config):")
    print(f"    .gitignore")
    print(f"    architecture_parsed.json")
    print(f"    uml_parsed.json")
    print(f"    generation_plan.json")
    print(f"\n  Project output: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
