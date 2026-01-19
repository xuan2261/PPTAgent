# Codebase Summary

## Overview

PPTAgent consists of two main modules totaling ~17,000 lines of code:
- **pptagent/** (~9,600 LOC) - Core template-based generation library
- **deeppresenter/** (~6,500 LOC) - Multi-agent freeform generation system

## Directory Structure

```
PPTAgent/
├── pptagent/                    # Core library (Stage I & II)
│   ├── agent.py                 # Role-based agent with Jinja2 templates
│   ├── apis.py                  # Slide edit APIs (CodeExecutor)
│   ├── induct.py                # SlideInducter for template analysis
│   ├── llms.py                  # LLM/AsyncLLM wrapper
│   ├── pptgen.py                # PPTAgent/PPTGen main generator
│   ├── ppteval.py               # Evaluation framework
│   ├── roles/                   # YAML role definitions
│   │   ├── planner.yaml
│   │   ├── editor.yaml
│   │   ├── coder.yaml
│   │   ├── content_organizer.yaml
│   │   ├── layout_selector.yaml
│   │   ├── schema_extractor.yaml
│   │   └── doc_extractor.yaml
│   └── templates/               # Presentation templates
│       ├── beamer/
│       ├── cip/
│       ├── default/
│       ├── hit/
│       ├── thu/
│       └── ucas/
│           ├── source.pptx
│           └── slide_induction.json
│
├── deeppresenter/               # Multi-agent system
│   ├── deeppresenter/
│   │   ├── main.py              # AgentLoop orchestrator
│   │   ├── env.py               # AgentEnv with MCP integration
│   │   ├── agents/              # Agent implementations
│   │   │   ├── research.py      # Research Agent
│   │   │   └── design.py        # Design Agent
│   │   ├── mcp/                 # MCP server implementations
│   │   ├── utils/
│   │   │   └── constants.py     # Configurable variables
│   │   ├── config.yaml          # Model configuration
│   │   └── mcp.json             # MCP server configuration
│   └── docker/
│       ├── Dockerfile
│       └── build.sh
│
├── webui.py                     # Gradio web interface (~300 LOC)
├── package.json                 # Node.js dependencies
├── README.md                    # Project documentation
└── resource/                    # Demo images and assets
```

## Key Files and Roles

### PPTAgent Core

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `llms.py` | LLM API wrapper | `LLM`, `AsyncLLM` |
| `agent.py` | Role-based agent | `Agent` |
| `induct.py` | Template analysis | `SlideInducter`, `category_split()`, `layout_split()`, `content_induct()` |
| `pptgen.py` | Presentation generation | `PPTAgent`, `PPTGen`, `generate_outline()`, `generate_slide()`, `edit_slide()` |
| `apis.py` | Slide manipulation | `CodeExecutor`, `replace_paragraph()`, `clone_paragraph()`, `del_paragraph()`, `replace_image()`, `del_image()` |
| `ppteval.py` | Quality evaluation | `PPTEval` (Content, Design, Coherence) |

### DeepPresenter System

| File | Purpose | Key Classes/Functions |
|------|---------|----------------------|
| `main.py` | Agent orchestration | `AgentLoop` |
| `env.py` | Environment management | `AgentEnv` |
| `agents/research.py` | Research capabilities | Research Agent |
| `agents/design.py` | Visual design | Design Agent |
| `config.yaml` | Model settings | research_agent, design_agent, vision_model, t2i_model |
| `mcp.json` | MCP configuration | Tool server definitions |

### Root Level

| File | Purpose |
|------|---------|
| `webui.py` | Gradio chat interface with streaming |
| `package.json` | Node.js deps (pptxgenjs, playwright, sharp) |

## Module Relationships

```
                    ┌─────────────────┐
                    │    webui.py     │
                    │  (Gradio UI)    │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │  DeepPresenter  │           │    PPTAgent     │
    │   (Freeform)    │           │   (Template)    │
    └────────┬────────┘           └────────┬────────┘
             │                             │
    ┌────────┴────────┐           ┌────────┴────────┐
    │                 │           │                 │
    ▼                 ▼           ▼                 ▼
┌────────┐      ┌────────┐   ┌────────┐      ┌────────┐
│Research│      │ Design │   │ Slide  │      │ PPTGen │
│ Agent  │      │ Agent  │   │Inducter│      │        │
└────┬───┘      └────┬───┘   └────────┘      └────────┘
     │               │
     └───────┬───────┘
             ▼
    ┌─────────────────┐
    │    AgentEnv     │
    │  (MCP Servers)  │
    └─────────────────┘
```

## Data Flow

### Template Mode (PPTAgent)
```
Document → SlideInducter → Layout Analysis → PPTGen → PPTX
              │
              ├── category_split()
              ├── layout_split()
              └── content_induct()
```

### Freeform Mode (DeepPresenter)
```
User Query → AgentLoop → Research Agent → manuscript.md
                │
                └──────→ Design Agent → HTML Slides → PPTX
                              │
                              └── MCP Tools (20+)
```

## Template Structure

Each template in `pptagent/templates/` contains:
- `source.pptx` - PowerPoint template file
- `slide_induction.json` - Extracted slide schemas and layouts

Available templates: beamer, cip, default, hit, thu, ucas

## MCP Tools Categories

| Category | Tools |
|----------|-------|
| Document | convert_to_markdown |
| Web | fetch_url, download_file |
| Search | search_web, search_images (Tavily) |
| Academic | search_papers (arXiv), get_paper_authors |
| Vision | image_generation, image_caption, document_analyze |
| Management | todo_create, todo_update, todo_list |
| Control | thinking, finalize |

## Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| config.yaml | deeppresenter/deeppresenter/ | Model endpoints and API keys |
| mcp.json | deeppresenter/deeppresenter/ | MCP server configuration |
| constants.py | deeppresenter/deeppresenter/utils/ | Runtime constants |

## External Dependencies

### Python (requirements)
```
openai          # LLM API
oaib            # OpenAI batch processing
pptagent_pptx   # PPTX manipulation
jinja2          # Template rendering
pydantic        # Data validation
Pillow          # Image processing
pdf2image       # PDF conversion
tenacity        # Retry logic
gradio          # Web UI
```

### Node.js (package.json)
```
pptxgenjs       # PPTX generation
playwright      # Browser automation
sharp           # Image processing
fast-glob       # File matching
```

---

*Last updated: 2026-01-19*
