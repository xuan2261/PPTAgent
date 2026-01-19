
<div align="right">
  <details>
    <summary >🌐 Language</summary>
    <div>
      <div align="center">
        <a href="https://openaitx.github.io/view.html?user=icip-cas&project=PPTAgent&lang=en">English</a>
        | <a href="https://openaitx.github.io/view.html?user=icip-cas&project=PPTAgent&lang=zh-CN">简体中文</a>
        | <a href="https://openaitx.github.io/view.html?user=icip-cas&project=PPTAgent&lang=ja">日本語</a>
        | <a href="https://openaitx.github.io/view.html?user=icip-cas&project=PPTAgent&lang=ko">한국어</a>
        | <a href="https://openaitx.github.io/view.html?user=icip-cas&project=PPTAgent&lang=vi">Tiếng Việt</a>
      </div>
    </div>
  </details>
</div>

<div align="center">
  <img src="resource/pptagent-logo.png" width="240px">
</div>

https://github.com/user-attachments/assets/938889e8-d7d8-4f4f-b2a1-07ee3ef3991a

## About

**PPTAgent** is an AI-powered presentation generation system that creates professional PowerPoint presentations from documents. Published at **EMNLP 2025**, it features a two-stage pipeline and multi-agent architecture.

### Key Features

- **Template-Based Generation** - Two-stage pipeline with SlideInducter and PPTGen
- **Freeform Generation** - Multi-agent system with Research and Design agents
- **20+ MCP Tools** - Web search, paper search, image generation, and more
- **Offline Mode** - Support for local deployment without external APIs
- **PPTX Export** - Professional PowerPoint output

## Documentation

| Document | Description |
|----------|-------------|
| [Project Overview](docs/project-overview-pdr.md) | Vision, goals, requirements |
| [Codebase Summary](docs/codebase-summary.md) | Directory structure, key files |
| [Code Standards](docs/code-standards.md) | Python style, conventions |
| [System Architecture](docs/system-architecture.md) | Technical architecture, data flow |
| [Project Roadmap](docs/project-roadmap.md) | Version history, future plans |

## News

- **[2026/01]**: PPTX export and offline mode support
- **[2025/12]**: 🔥 V2 with Deep Research, Free-Form Design, Agent Environment
- **[2025/09]**: MCP server support - see [MCP Server](PPTAgent/DOC.md#mcp-server-)
- **[2025/08]**: 🎉 Paper accepted to **EMNLP 2025**!
- **[2025/05]**: ✨ v1 released, reached 1,000 GitHub stars!

## Quick Start

### Prerequisites

> **Required**: API keys, Docker for sandbox, Python 3.11+

### 1. Set up agent environment

```bash
bash deeppresenter/docker/build.sh
```

### 2. Configure external services

**Online Setup:**
- **MinerU**: Get API key at [mineru.net](https://mineru.net/apiManage/docs)
- **Tavily** (optional): Get API key at [tavily.com](https://www.tavily.com/)
- **LLM**: Copy `deeppresenter/deeppresenter/config.yaml.example` to `config.yaml`
- **MCP**: Copy `deeppresenter/deeppresenter/mcp.json.example` to `mcp.json`

**Offline Setup:**
- Deploy MinerU locally: [MinerU docker guide](https://opendatalab.github.io/MinerU/quick_start/docker_deployment/)
- Set `offline_mode: true` in `config.yaml`

### 3. Install dependencies

```bash
pip install -e deeppresenter
pip install playwright && playwright install chromium
npm install && npx playwright install chromium
```

### 4. Launch

```bash
python webui.py
```

> 💡 Configuration: [constants.py](deeppresenter/deeppresenter/utils/constants.py)

## Case Studies

### Document Presentation
> Prompt: "Please present the given document to me."

<div style="display: flex; flex-wrap: wrap; gap: 10px;">
  <img src="resource/v2/manuscript/0001.jpg" alt="Slide 1" width="200"/>
  <img src="resource/v2/manuscript/0002.jpg" alt="Slide 2" width="200"/>
  <img src="resource/v2/manuscript/0003.jpg" alt="Slide 3" width="200"/>
  <img src="resource/v2/manuscript/0004.jpg" alt="Slide 4" width="200"/>
</div>

### Product Introduction
> Prompt: "请介绍小米 SU7 的外观和价格"

<div style="display: flex; flex-wrap: wrap; gap: 10px;">
  <img src="resource/v2/presentation1/0001.jpg" alt="Slide 1" width="200"/>
  <img src="resource/v2/presentation1/0002.jpg" alt="Slide 2" width="200"/>
  <img src="resource/v2/presentation1/0003.jpg" alt="Slide 3" width="200"/>
</div>

### Educational Content
> Prompt: "请制作一份高中课堂展示课件，主题为'解码立法过程'"

<div style="display: flex; flex-wrap: wrap; gap: 10px;">
  <img src="resource/v2/presentation2/0001.jpg" alt="Slide 1" width="200"/>
  <img src="resource/v2/presentation2/0002.jpg" alt="Slide 2" width="200"/>
  <img src="resource/v2/presentation2/0003.jpg" alt="Slide 3" width="200"/>
</div>

## Architecture

```
PPTAgent/
├── pptagent/          # Core library (Template mode)
│   ├── induct.py      # SlideInducter (Stage I)
│   ├── pptgen.py      # PPTGen (Stage II)
│   └── templates/     # Built-in templates
├── deeppresenter/     # Multi-agent system (Freeform mode)
│   ├── main.py        # AgentLoop
│   ├── env.py         # AgentEnv + MCP
│   └── agents/        # Research & Design agents
└── webui.py           # Gradio interface
```

See [System Architecture](docs/system-architecture.md) for details.

## Contact

> The main contributor is a Master's student graduating in 2026, currently on the job market.

<div align="center">
  <img src="resource/wechat.jpg" width="140px">
</div>

---

[![Star History Chart](https://api.star-history.com/svg?repos=icip-cas/PPTAgent&type=Date)](https://star-history.com/#icip-cas/PPTAgent&Date)

## Citation

```bibtex
@inproceedings{zheng-etal-2025-pptagent,
    title = "{PPTA}gent: Generating and Evaluating Presentations Beyond Text-to-Slides",
    author = "Zheng, Hao and Guan, Xinyan and Kong, Hao and Zhang, Wenkai and
              Zheng, Jia and Zhou, Weixiang and Lin, Hongyu and Lu, Yaojie and
              Han, Xianpei and Sun, Le",
    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing",
    month = nov,
    year = "2025",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.emnlp-main.728/",
    doi = "10.18653/v1/2025.emnlp-main.728",
    pages = "14413--14429",
}
```

## License

MIT License - ICIP-CAS 2025
