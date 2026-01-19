# Code Standards

## Python Style Guide

### Version Requirements
- **Python 3.11+** required
- Use modern Python features (match statements, type hints, etc.)

### Linting & Formatting

Pre-commit hooks configured with:
- **ruff** - Fast Python linter and formatter
- **pyupgrade** - Automatic Python syntax upgrades

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/asottile/pyupgrade
    hooks:
      - id: pyupgrade
        args: [--py311-plus]
```

### Type Hints

Use type hints for all function signatures:

```python
# Good
def generate_slide(
    self,
    outline: dict[str, Any],
    template: str,
    page_count: int = 10,
) -> Presentation:
    ...

# Avoid
def generate_slide(self, outline, template, page_count=10):
    ...
```

### Import Organization

```python
# Standard library
from pathlib import Path
from typing import Any

# Third-party
import openai
from pydantic import BaseModel

# Local
from pptagent.llms import AsyncLLM
from pptagent.agent import Agent
```

## File Organization Patterns

### Module Structure

```
module/
├── __init__.py          # Public API exports
├── core.py              # Main implementation
├── models.py            # Pydantic models
├── utils.py             # Helper functions
└── exceptions.py        # Custom exceptions
```

### File Size Guidelines

| File Type | Max Lines | Action if Exceeded |
|-----------|-----------|-------------------|
| Core modules | 500 | Split by responsibility |
| Utilities | 200 | Group by functionality |
| Tests | 300 | Split by test category |
| Config | 100 | Use separate config files |

## Naming Conventions

### Files & Directories
- Use **snake_case** for Python files: `slide_inducter.py`
- Use **kebab-case** for config files: `config.yaml`, `mcp.json`
- Use **PascalCase** for class-only files: `AgentLoop.py` (optional)

### Python Identifiers

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `SlideInducter`, `PPTAgent` |
| Functions | snake_case | `generate_outline()`, `edit_slide()` |
| Constants | UPPER_SNAKE | `DEFAULT_MODEL`, `MAX_RETRIES` |
| Variables | snake_case | `slide_count`, `template_path` |
| Private | _prefix | `_parse_response()`, `_cache` |

### YAML Role Definitions

```yaml
# roles/planner.yaml
name: planner
description: Plans presentation structure
system_prompt: |
  You are a presentation planner...
```

## Error Handling Patterns

### Use Specific Exceptions

```python
# Define custom exceptions
class PPTAgentError(Exception):
    """Base exception for PPTAgent."""
    pass

class TemplateNotFoundError(PPTAgentError):
    """Raised when template is not found."""
    pass

class GenerationError(PPTAgentError):
    """Raised when slide generation fails."""
    pass
```

### Retry Logic with Tenacity

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def call_llm(prompt: str) -> str:
    """Call LLM with automatic retry on failure."""
    ...
```

### Graceful Degradation

```python
async def generate_with_fallback(self, content: str) -> Presentation:
    try:
        return await self._generate_with_images(content)
    except ImageGenerationError:
        logger.warning("Image generation failed, using placeholders")
        return await self._generate_text_only(content)
```

## Async Patterns

### Prefer Async for I/O Operations

```python
# Good - async for API calls
async def generate_slides(self, outline: list[dict]) -> list[Slide]:
    tasks = [self._generate_slide(item) for item in outline]
    return await asyncio.gather(*tasks)

# Avoid - synchronous blocking
def generate_slides(self, outline: list[dict]) -> list[Slide]:
    return [self._generate_slide(item) for item in outline]
```

### Use AsyncLLM for Concurrent Requests

```python
from pptagent.llms import AsyncLLM

llm = AsyncLLM(model="gpt-4", api_key=key)
responses = await llm.batch_complete(prompts)
```

## Configuration Management

### Environment Variables

```python
# Use pydantic-settings for config
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    mineru_api_key: str
    tavily_api_key: str | None = None
    offline_mode: bool = False

    class Config:
        env_file = ".env"
```

### YAML Configuration

```yaml
# config.yaml
research_agent:
  model: claude-sonnet
  temperature: 0.7

design_agent:
  model: gemini-pro
  temperature: 0.5

offline_mode: false
```

## Documentation Standards

### Docstrings (Google Style)

```python
def generate_outline(
    self,
    document: str,
    page_count: int = 10,
) -> dict[str, Any]:
    """Generate presentation outline from document.

    Args:
        document: Source document content.
        page_count: Target number of slides.

    Returns:
        Outline dictionary with slide specifications.

    Raises:
        GenerationError: If outline generation fails.
    """
```

### Inline Comments

```python
# Use for non-obvious logic only
def calculate_layout_score(self, layout: Layout) -> float:
    # Weight factors based on PPTEval paper (Section 4.2)
    content_weight = 0.4
    design_weight = 0.35
    coherence_weight = 0.25
    ...
```

## Testing Standards

### Test File Structure

```python
# tests/test_pptgen.py
import pytest
from pptagent.pptgen import PPTAgent

class TestPPTAgent:
    @pytest.fixture
    def agent(self):
        return PPTAgent(model="gpt-4")

    async def test_generate_outline(self, agent):
        outline = await agent.generate_outline("Test doc")
        assert "slides" in outline
        assert len(outline["slides"]) > 0
```

### Coverage Requirements

| Component | Minimum Coverage |
|-----------|-----------------|
| Core modules | 80% |
| API endpoints | 90% |
| Utilities | 70% |

## Git Commit Standards

### Conventional Commits

```
feat: Add ImageContent adaptation for Qwen model
fix: Resolve path issues in template loader
chore: Enhance html2pptx conversion
docs: Update API documentation
```

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

## Security Considerations

### API Key Management

```python
# Never hardcode API keys
# Bad
api_key = "sk-xxxx"

# Good - use environment variables
api_key = os.environ.get("OPENAI_API_KEY")
```

### Docker Sandbox

All code execution runs in isolated Docker container:
- `desktop-commander-deeppresenter` image
- No network access for untrusted code
- Resource limits enforced

### Input Validation

```python
from pydantic import BaseModel, validator

class SlideRequest(BaseModel):
    content: str
    template: str
    page_count: int

    @validator("page_count")
    def validate_page_count(cls, v):
        if not 1 <= v <= 50:
            raise ValueError("page_count must be between 1 and 50")
        return v
```

---

*Last updated: 2026-01-19*
