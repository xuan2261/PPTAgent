# Project Overview - Product Development Requirements

## Executive Summary

**PPTAgent** is an AI-powered presentation generation system that automatically creates professional PowerPoint presentations from documents. Published at EMNLP 2025, it represents a breakthrough in automated presentation generation by addressing content quality, visual appeal, and structural coherence simultaneously.

## Project Vision

Transform document-to-presentation workflows by providing an intelligent, autonomous system that generates publication-quality presentations with minimal human intervention.

## Goals

| Goal | Description | Priority |
|------|-------------|----------|
| Automated Generation | Generate complete presentations from documents | P0 |
| Visual Quality | Produce visually appealing slides matching professional standards | P0 |
| Content Coherence | Maintain logical flow and structural consistency | P0 |
| Multi-mode Support | Support both template-based and freeform generation | P1 |
| Research Integration | Enable deep research for content enrichment | P1 |
| Offline Capability | Support offline mode with local services | P2 |

## Target Users

1. **Researchers & Academics** - Generate conference/paper presentations
2. **Business Professionals** - Create reports and pitch decks
3. **Educators** - Develop course materials and lectures
4. **Content Creators** - Produce visual content from written materials

## Key Features

### Core Capabilities

1. **Two-Stage Pipeline (PPTAgent)**
   - Stage I: Template analysis via SlideInducter
   - Stage II: Content generation via PPTGen

2. **Multi-Agent System (DeepPresenter)**
   - Research Agent: Web/paper search, document parsing
   - Design Agent: HTML slide generation with quality checks
   - 20+ MCP tools for autonomous asset creation

3. **Template Support**
   - Built-in templates: beamer, cip, default, hit, thu, ucas
   - Custom template induction from existing presentations

4. **Output Formats**
   - PowerPoint (.pptx) export
   - HTML slides (1280x720)

### Advanced Features

- Text-to-image generation for slide visuals
- Autonomous image captioning and analysis
- Web and academic paper search integration
- Sandbox environment with Docker isolation

## Functional Requirements

### FR-001: Document Processing
- Accept PDF, Markdown, and plain text inputs
- Extract structured content using MinerU API
- Support both online and offline document parsing

### FR-002: Presentation Generation
- Generate outline from source content
- Select appropriate layouts per slide
- Fill content into slide schemas
- Execute edit actions (replace/clone/delete)

### FR-003: Multi-Agent Orchestration
- Coordinate Research and Design agents
- Manage MCP tool invocations
- Handle streaming responses in Web UI

### FR-004: Quality Assurance
- Evaluate Content, Design, and Coherence (PPTEval)
- Per-slide quality checks during generation
- Support iterative refinement

## Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Response Time | < 5 minutes for 10-slide presentation |
| Concurrency | Support multiple simultaneous users via Gradio |
| Reliability | Graceful error handling with retry logic |
| Security | Docker sandbox for code execution |
| Extensibility | Plugin architecture via MCP servers |

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| GitHub Stars | 1,000+ | Achieved (v1) |
| EMNLP Acceptance | Published | Achieved (2025) |
| Template Coverage | 6+ templates | 6 templates |
| MCP Tools | 20+ tools | 20+ tools |

## Constraints

1. **API Dependencies**: Requires LLM API keys (OpenAI-compatible)
2. **External Services**: MinerU API for document parsing (14-day key validity)
3. **Hardware**: Docker required for sandbox environment
4. **Network**: Online mode requires Tavily API for search

## Dependencies

### Python Packages
- openai, oaib - LLM integration
- pptagent_pptx - PowerPoint manipulation
- jinja2 - Template rendering
- pydantic - Data validation
- PIL, pdf2image - Image processing
- tenacity - Retry logic

### Node.js Packages
- pptxgenjs - PPTX generation
- playwright - Browser automation
- sharp - Image processing

### External Services
- MinerU API - Document parsing
- Tavily API - Web search (optional)
- Semantic Scholar - Paper metadata

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| API key expiration | Service disruption | Offline mode support |
| LLM rate limits | Slow generation | Async batch processing |
| Docker unavailable | No sandbox | Fallback execution mode |

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| v1.0 | 2025-05 | Core functionality, 1K stars |
| v2.0 | 2025-09 | MCP support, major improvements |
| v2.1 | 2025-12 | Deep research, freeform design |
| v2.2 | 2026-01 | PPTX export, offline mode |

---

*Last updated: 2026-01-19*
