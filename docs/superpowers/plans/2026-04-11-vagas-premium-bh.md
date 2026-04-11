# Vagas Premium BH & Múltiplos Perfis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expandir o sistema para suportar múltiplos perfis de busca (focando em Engenharia Elétrica em BH), integrar Gupy via Playwright MCP, e melhorar a legibilidade da UI.

**Architecture:** 
- O `MultiSourceCollector` será atualizado para iterar sobre uma lista de `JobProfile` ativos.
- Novos conectores serão adicionados em `src/app/sources/`.
- Configurações persistidas em `.kilo/ui-settings.json` suportarão múltiplos perfis.

**Tech Stack:** Python (FastAPI), Playwright MCP, SQLite, Jinja2.

---

### Task 1: Configuração de Ambiente e Memória

**Files:**
- Create: `.env`
- Modify: `.kilo/project-context.md`

- [ ] **Step 1: Criar arquivo .env**
  Configure as credenciais de e-mail e Playwright MCP.
- [ ] **Step 2: Atualizar .kilo/project-context.md**
  Registrar o novo estado do projeto e as metas de Engenharia Elétrica.
- [ ] **Step 3: Instalar Playwright MCP**
  Executar: `npm install -g @playwright/mcp`
- [ ] **Step 4: Verificar instalação**
  Executar: `npx @playwright/mcp --help`

### Task 2: Sistema de Múltiplos Perfis (Backend)

**Files:**
- Modify: `src/app/core/profile.py`
- Modify: `src/app/schemas/ui.py`
- Modify: `.kilo/ui-settings.json`

- [ ] **Step 1: Refatorar JobProfile para suportar múltiplos perfis**
  Adicionar campo `id`, `name` e `active` ao `JobProfile`.
- [ ] **Step 2: Atualizar ui-settings.json**
  Mudar `target_locations`, `required_keywords`, etc., para dentro de uma lista de perfis.
- [ ] **Step 3: Criar Perfil de Engenharia Elétrica**
  Adicionar o perfil solicitado (BH, Estágio/Trainee, CLP/IHM).

### Task 3: Conector Gupy e Playwright Integration

**Files:**
- Create: `src/app/sources/gupy.py`
- Modify: `src/app/services/collector.py`

- [ ] **Step 1: Implementar GupySource**
  Usar Playwright para navegar e extrair dados da Gupy.
- [ ] **Step 2: Registrar Gupy no MultiSourceCollector**
  Garantir que o coletor use o GupySource se ativado.

### Task 4: Ajustes de UI (Fontes e Seleção)

**Files:**
- Modify: `src/app/static/dashboard.css`
- Modify: `src/app/templates/dashboard.html`

- [ ] **Step 1: Aumentar fontes no CSS**
  Ajustar `body`, `.card-title`, `.card-text` para tamanhos maiores (ex: 1.1rem, 1.2rem).
- [ ] **Step 2: Adicionar Seletor de Perfis no Dashboard**
  Exibir checkboxes para ativar/desativar perfis na UI.
