---
title: "i18n + Electron Desktop App"
description: "Add EN/VI language support and build Windows .exe with GitHub Actions"
status: pending
priority: P2
effort: 16h
branch: main
tags: [i18n, electron, desktop, ci-cd]
created: 2026-01-19
---

# i18n + Electron Desktop App Implementation Plan

## Overview

Two-feature implementation for PPTAgent:
1. **i18n**: English/Vietnamese language support via Gradio native `gr.I18n`
2. **Desktop App**: Windows .exe using Electron + PyInstaller with GitHub Actions CI/CD

## Phases

| Phase | Description | Effort | Status |
|-------|-------------|--------|--------|
| [Phase 1](phase-01-i18n-setup.md) | Create translation infrastructure | 2h | pending |
| [Phase 2](phase-02-webui-i18n-integration.md) | Integrate i18n into webui.py | 2h | pending |
| [Phase 3](phase-03-electron-project-setup.md) | Initialize Electron project | 3h | pending |
| [Phase 4](phase-04-python-backend-bundling.md) | PyInstaller configuration | 3h | pending |
| [Phase 5](phase-05-electron-python-ipc.md) | IPC communication layer | 3h | pending |
| [Phase 6](phase-06-github-actions-cicd.md) | Build and release workflow | 3h | pending |

## Key Dependencies

- Gradio v5.x (v6.0-6.1 has i18n bugs)
- Python 3.11+
- Node.js 20+
- PyInstaller
- electron-builder with NSIS

## Architecture

```
PPTAgent/
├── locales/                 # Translation files
│   ├── en.json
│   └── vi.json
├── utils/i18n.py            # i18n helper module
├── webui.py                 # Modified with i18n
├── electron-app/            # New Electron project
│   ├── src/
│   │   ├── main.js
│   │   ├── preload.js
│   │   └── renderer/
│   ├── python/
│   │   └── backend.py       # IPC wrapper
│   └── package.json
└── .github/workflows/
    └── build-desktop.yml    # CI/CD workflow
```

## Reports

- [Electron + Python Research](research/researcher-01-electron-python-integration.md)
- [Gradio i18n Research](research/researcher-02-gradio-i18n-implementation.md)

## Validation Summary

**Validated:** 2026-01-19
**Questions asked:** 4

### Confirmed Decisions
| Decision | Choice | Notes |
|----------|--------|-------|
| Gradio version | **v5.x** | Confirmed from pyproject.toml: `gradio>=5.47.2,<6.0` ✅ |
| Playwright browsers | **Bundle vào installer** | App lớn hơn (~150MB+), hoạt động offline ngay |
| Code signing | **Skip** | User sẽ thấy SmartScreen warning, click 'Run anyway' |
| i18n scope | **Chỉ UI labels** | Agent responses giữ nguyên (tiếng Anh) |

### Action Items
- [x] ~~Gradio version confirmation~~ → Đã xác nhận v5.x
- [ ] Update Phase 4: Thêm Playwright browsers vào PyInstaller bundling
- [ ] Update Phase 6: Bỏ code signing steps trong CI/CD

### Resolved Questions
1. ✅ Gradio v5.47.2+ - i18n native hoạt động tốt
2. ✅ Skip code signing - chấp nhận SmartScreen warning
3. ✅ Bundle Playwright browsers vào installer
