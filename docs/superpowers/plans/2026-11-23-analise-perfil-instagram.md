# Análise de Perfil e Comentários do Instagram Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar o script `scripts/analisar.py` para coletar métricas de posts e comentários do perfil `@comidinhasdobebe.dicas`, categorizar o engajamento e gerar relatórios acionáveis em `relatorios/AAAA-MM-DD.md`.

---

## Proposed Changes

### 1. `tests/test_analisar.py`
- Testes unitários para:
  - Categorização de comentários (dúvidas, pedidos de receitas, palavras de CTA "PRATINHO", elogios).
  - Cálculo de métricas e ranking de posts por engajamento.
  - Geração e formatação do relatório em Markdown.

### 2. `scripts/analisar.py`
- Script executável:
  - Funções de categorização de comentários com heurísticas simples e robustas.
  - Funções de chamada à API oficial do Instagram via `scripts.instagram` para mídias, comentários e insights (com fallback silencioso).
  - Gerador do relatório em Markdown com recomendações de marketing.
  - Ponto de entrada CLI: `python scripts/analisar.py [--dias N] [--limite N] [--saida caminho]`.

### 3. `.agents/skills/comidinhas-analisar-perfil/SKILL.md`
- Skill no padrão do workspace para execução sob demanda do relatório de análise pelo agente.

---

## Tasks

### Task 1: Testes e Lógica de Categorização e Formatação de Relatório
**Files:**
- `tests/test_analisar.py`
- `scripts/analisar.py`

- [ ] **Step 1:** Escrever teste unitário `tests/test_analisar.py` validando categorização de comentários e cálculo de ranking de posts.
- [ ] **Step 2:** Rodar `.venv/bin/python -m unittest tests/test_analisar.py` e verificar falha (RED).
- [ ] **Step 3:** Implementar a lógica pura em `scripts/analisar.py` para categorização, cálculo de engajamento e montagem do Markdown.
- [ ] **Step 4:** Rodar `.venv/bin/python -m unittest tests/test_analisar.py` e verificar aprovação (GREEN).
- [ ] **Step 5:** Commit: `feat(analise): adiciona categorizacao de comentarios e gerador de relatorio`.

---

### Task 2: Integração com API da Meta e Execução CLI
**Files:**
- `scripts/analisar.py`
- `tests/test_analisar.py`

- [ ] **Step 1:** Adicionar testes com mocks para chamadas de API (`get_posts`, `get_comments`, `get_insights`) em `tests/test_analisar.py`.
- [ ] **Step 2:** Rodar testes e verificar falha (RED).
- [ ] **Step 3:** Implementar integração com `scripts/instagram.py` e interface CLI em `scripts/analisar.py`.
- [ ] **Step 4:** Rodar testes unitários com `.venv/bin/python -m unittest tests/test_analisar.py` e verificar aprovação (GREEN).
- [ ] **Step 5:** Commit: `feat(analise): integra script de analise com API do Instagram`.

---

### Task 3: Skill do Agente e Validação com Conta Real
**Files:**
- `.agents/skills/comidinhas-analisar-perfil/SKILL.md`
- `relatorios/`

- [ ] **Step 1:** Criar a skill em `.agents/skills/comidinhas-analisar-perfil/SKILL.md`.
- [ ] **Step 2:** Executar `.venv/bin/python scripts/analisar.py` contra a API real do Instagram e gerar o primeiro relatório real em `relatorios/`.
- [ ] **Step 3:** Verificar a integridade do relatório gerado.
- [ ] **Step 4:** Commit: `feat(analise): adiciona skill de analise e primeiro relatorio`.

---

## Verification Plan

### Automated Tests:
```bash
.venv/bin/python -m unittest discover tests -v
```

### Manual Verification:
- Executar `.venv/bin/python scripts/analisar.py` e inspecionar o arquivo gerado em `relatorios/*.md`.
