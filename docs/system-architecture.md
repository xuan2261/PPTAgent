# System Architecture

## Overview

PPTAgent implements two distinct presentation generation pipelines:

1. **Template-Based Generation** (PPTAgent) - Two-stage edit-based approach
2. **Freeform Generation** (DeepPresenter) - Multi-agent system with research capabilities

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web UI (Gradio)                         │
│                          webui.py                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    Template Mode        │     │    Freeform Mode        │
│      (PPTAgent)         │     │    (DeepPresenter)      │
│                         │     │                         │
│  ┌───────────────────┐  │     │  ┌───────────────────┐  │
│  │  SlideInducter    │  │     │  │    AgentLoop      │  │
│  │   (Stage I)       │  │     │  │                   │  │
│  └─────────┬─────────┘  │     │  └─────────┬─────────┘  │
│            │            │     │            │            │
│  ┌─────────▼─────────┐  │     │  ┌─────────▼─────────┐  │
│  │     PPTGen        │  │     │  │   Research Agent  │  │
│  │   (Stage II)      │  │     │  │   Design Agent    │  │
│  └───────────────────┘  │     │  └─────────┬─────────┘  │
│                         │     │            │            │
└─────────────────────────┘     │  ┌─────────▼─────────┐  │
                                │  │    AgentEnv       │  │
                                │  │   (MCP Servers)   │  │
                                │  └───────────────────┘  │
                                └─────────────────────────┘
```

## Template-Based Pipeline (PPTAgent)

### Stage I: Template Induction

The SlideInducter analyzes reference presentations to extract reusable patterns.

```
┌──────────────────────────────────────────────────────────┐
│                    SlideInducter                         │
│                                                          │
│  source.pptx ──► category_split() ──► Functional Types  │
│       │                                    │             │
│       │         layout_split() ◄───────────┘             │
│       │              │                                   │
│       │              ▼                                   │
│       └────► content_induct() ──► slide_induction.json  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Process Flow:**
1. `category_split()` - Classify slides by functional type (title, content, summary)
2. `layout_split()` - Group slides by visual layout patterns
3. `content_induct()` - Extract content schemas for each layout

**Output:** `slide_induction.json` containing:
- Slide categories and layouts
- Content placeholders and schemas
- Visual element specifications

### Stage II: Presentation Generation

PPTGen creates new presentations using extracted templates.

```
┌──────────────────────────────────────────────────────────┐
│                        PPTGen                            │
│                                                          │
│  Document ──► generate_outline() ──► Slide Outline      │
│                     │                     │              │
│                     │    ┌────────────────┘              │
│                     │    │                               │
│                     ▼    ▼                               │
│              generate_slide() ──► Draft Slides          │
│                     │                  │                 │
│                     │    ┌─────────────┘                 │
│                     │    │                               │
│                     ▼    ▼                               │
│               edit_slide() ──► Final PPTX               │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Roles Involved:**

| Role | Function |
|------|----------|
| doc_extractor | Extract key content from source document |
| planner | Create presentation outline and structure |
| layout_selector | Choose appropriate template layout per slide |
| content_organizer | Organize content for each slide |
| editor | Refine slide content |
| coder | Generate edit actions |

### Slide Edit APIs

The CodeExecutor applies edit actions to slides:

```python
# Available edit operations
replace_paragraph(slide, placeholder, new_text)
clone_paragraph(slide, source, target)
del_paragraph(slide, placeholder)
replace_image(slide, placeholder, image_path)
del_image(slide, placeholder)
```

## Freeform Pipeline (DeepPresenter)

### Agent Loop Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       AgentLoop                             │
│                       (main.py)                             │
│                                                             │
│  User Query ──────────────────────────────────────────┐     │
│       │                                               │     │
│       ▼                                               │     │
│  ┌─────────────────┐                                  │     │
│  │ Research Agent  │──► Web Search ──────────────┐    │     │
│  │                 │    Paper Search             │    │     │
│  │ (Claude Sonnet) │    Document Parse           │    │     │
│  └────────┬────────┘                             │    │     │
│           │                                      │    │     │
│           ▼                                      │    │     │
│      manuscript.md ◄─────────────────────────────┘    │     │
│           │                                           │     │
│           ▼                                           │     │
│  ┌─────────────────┐                                  │     │
│  │  Design Agent   │──► HTML Generation ─────────┐    │     │
│  │                 │    Image Generation         │    │     │
│  │ (Gemini Pro)    │    Quality Check            │    │     │
│  └────────┬────────┘                             │    │     │
│           │                                      │    │     │
│           ▼                                      │    │     │
│      HTML Slides (1280x720) ◄────────────────────┘    │     │
│           │                                           │     │
│           ▼                                           │     │
│       PPTX Export                                     │     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Environment

```
┌─────────────────────────────────────────────────────────────┐
│                      AgentEnv (env.py)                      │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Document   │  │    Search    │  │    Vision    │       │
│  │    Tools     │  │    Tools     │  │    Tools     │       │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤       │
│  │ convert_to_  │  │ search_web   │  │ image_gen    │       │
│  │   markdown   │  │ search_images│  │ image_caption│       │
│  │ fetch_url    │  │ search_papers│  │ doc_analyze  │       │
│  │ download_file│  │ get_authors  │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  Management  │  │   Control    │                         │
│  │    Tools     │  │    Tools     │                         │
│  ├──────────────┤  ├──────────────┤                         │
│  │ todo_create  │  │ thinking     │                         │
│  │ todo_update  │  │ finalize     │                         │
│  │ todo_list    │  │              │                         │
│  └──────────────┘  └──────────────┘                         │
│                                                             │
│                    ┌──────────────┐                         │
│                    │    Docker    │                         │
│                    │   Sandbox    │                         │
│                    └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### MCP Integration

Model Context Protocol servers provide tool capabilities:

```
┌───────────────────────────────────────────────────────────┐
│                     MCP Architecture                      │
│                                                           │
│  Agent ◄──────────────────────────────────────────────►   │
│    │                                                      │
│    │ JSON-RPC                                             │
│    │                                                      │
│    ▼                                                      │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    MCP Server                       │  │
│  │                                                     │  │
│  │  Tools: [search_web, search_images, ...]           │  │
│  │  Resources: [documents, templates, ...]            │  │
│  │  Prompts: [research_prompt, design_prompt, ...]    │  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                               │
│                           ▼                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              External Services                      │  │
│  │                                                     │  │
│  │  - MinerU API (document parsing)                   │  │
│  │  - Tavily API (web/image search)                   │  │
│  │  - arXiv API (paper search)                        │  │
│  │  - Semantic Scholar (paper metadata)               │  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

## Docker Sandbox Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    Host System                            │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │        desktop-commander-deeppresenter              │  │
│  │                  (Docker)                           │  │
│  │                                                     │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐   │  │
│  │  │   Node.js   │  │  Chromium   │  │ Playwright │   │  │
│  │  │             │  │             │  │            │   │  │
│  │  └─────────────┘  └─────────────┘  └────────────┘   │  │
│  │                                                     │  │
│  │  ┌─────────────┐  ┌─────────────────────────────┐   │  │
│  │  │  CJK Fonts  │  │   Isolated Execution Env    │   │  │
│  │  │             │  │                             │   │  │
│  │  └─────────────┘  └─────────────────────────────┘   │  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                               │
│                           │ Volume Mounts                 │
│                           ▼                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Shared File System                     │  │
│  │                                                     │  │
│  │  - /workspace (project files)                      │  │
│  │  - /outputs (generated presentations)              │  │
│  │  - /templates (presentation templates)             │  │
│  │                                                     │  │
│  └─────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Template Mode Flow

```
                    Document Input
                          │
                          ▼
              ┌───────────────────────┐
              │   Document Parsing    │
              │      (MinerU)         │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Outline Generation  │
              │     (LLM + Planner)   │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Template Selection  │
              │   (Layout Selector)   │
              └───────────┬───────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│  Content Fill    │            │  Image Handling  │
│  (Editor/Coder)  │            │  (APIs)          │
└────────┬─────────┘            └────────┬─────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │    PPTX Assembly      │
              │   (CodeExecutor)      │
              └───────────┬───────────┘
                          │
                          ▼
                    Final PPTX
```

### Freeform Mode Flow

```
                     User Query
                          │
                          ▼
              ┌───────────────────────┐
              │    Research Phase     │
              │   (Research Agent)    │
              │                       │
              │   - Web Search        │
              │   - Paper Search      │
              │   - Doc Analysis      │
              └───────────┬───────────┘
                          │
                          ▼
                   manuscript.md
                          │
                          ▼
              ┌───────────────────────┐
              │     Design Phase      │
              │    (Design Agent)     │
              │                       │
              │   - Layout Design     │
              │   - Image Generation  │
              │   - Quality Check     │
              └───────────┬───────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌──────────────────┐            ┌──────────────────┐
│   HTML Slides    │            │   PPTX Export    │
│   (1280x720)     │            │                  │
└──────────────────┘            └──────────────────┘
```

## Model Recommendations

| Agent | Recommended Model | Purpose |
|-------|------------------|---------|
| Research Agent | Claude Sonnet | Deep research and content synthesis |
| Design Agent | Gemini Pro | Visual design and layout |
| Vision Model | GPT-4V / Gemini | Image analysis |
| T2I Model | DALL-E 3 / Imagen | Image generation |
| Long Context | Claude / Gemini | Large document processing |

## Scalability Considerations

### Horizontal Scaling
- Stateless agents enable multiple instances
- MCP servers can be distributed across nodes
- Docker containers support orchestration (K8s)

### Performance Optimization
- Async LLM calls with batching
- Image caching for repeated assets
- Template pre-compilation

### Rate Limiting
- Per-user request queuing
- API call throttling with tenacity
- Graceful degradation on limits

---

*Last updated: 2026-01-19*
