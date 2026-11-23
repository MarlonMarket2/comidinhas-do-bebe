---
name: comidinhas-aprovar-posts
description: Aprova posts semanais do @comidinhasdobebe.dicas, atualiza prévias e faz push para publicação automática pelo GitHub Actions
---

Use esta skill quando o usuário pedir para aprovar posts ("aprova a semana 2026-11-23", "aprova todos", "aprova o 1 e o 3", "libera a semana", "reverte o post X").

## Procedimento de Aprovação

1. **Localizar a semana**:
   - Identifique a pasta em `conteudo/<semana>/` indicada pelo usuário ou selecione a semana mais recente caso não especificada.

2. **Executar o script de aprovação**:
   - Para aprovar todos os posts da semana:
     ```bash
     .venv/bin/python scripts/aprovar.py conteudo/<semana> todos
     ```
   - Para aprovar posts específicos (ex: 02 e 03):
     ```bash
     .venv/bin/python scripts/aprovar.py conteudo/<semana> 02 03
     ```
   - Para reverter um post de volta para rascunho:
     ```bash
     .venv/bin/python scripts/aprovar.py conteudo/<semana> <id> --voltar
     ```

3. **Verificar a Prévia**:
   - O script `aprovar.py` atualiza automaticamente `saida/<semana>/previa.html`.
   - Confirme que o status dos posts foi atualizado corretamente nos arquivos JSON.

4. **Sincronização com o GitHub (Commit e Push)**:
   - Para que o fluxo do GitHub Actions (`.github/workflows/publicar.yml`) publique automaticamente no Instagram pelo horário agendado, os arquivos JSON aprovados e as imagens em `saida/` precisam estar no repositório remoto.
   - Execute:
     ```bash
     git add conteudo/<semana> saida/<semana>
     git commit -m "Semana <semana> aprovada"
     git push origin main
     ```

5. **Confirmação ao Usuário**:
   - Apresente um resumo dos posts aprovados com as respectivas datas e horários de agendamento em que serão disparados pela API.
