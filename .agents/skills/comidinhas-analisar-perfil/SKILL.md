---
name: comidinhas-analisar-perfil
description: Analisa o desempenho recente do perfil @comidinhasdobebe.dicas, lê comentários, identifica dúvidas frequentes e gera relatório de inteligência
---

Use esta skill quando o usuário pedir para analisar o perfil ("analise o perfil", "veja os comentários", "quais posts tiveram melhor engajamento?", "gere o relatório de desempenho").

## Procedimento de Análise

1. **Executar o script de análise**:
   ```bash
   .venv/bin/python scripts/analisar.py
   ```
   Isso buscará os posts mais recentes, curtidas, contagem de comentários e o conteúdo de cada comentário através da API oficial do Instagram, salvando o resultado em `relatorios/AAAA-MM-DD.md`.

2. **Ler o Relatório Gerado**:
   - Leia o arquivo gerado em `relatorios/AAAA-MM-DD.md`.
   - Analise os top posts e as categorias de comentários (dúvidas, pedidos de receitas, respostas ao CTA "PRATINHO").

3. **Apresentar Diagnóstico ao Usuário**:
   - Apresente um resumo claro e direto:
     - Post com melhor engajamento da semana.
     - Dúvidas mais frequentes das mães (para virarem posts de dicas).
     - Receitas mais pedidas (para virarem posts de receitas).
     - Pessoas que comentaram o CTA (para atendimento e envio do guia).
   - Indique as sugestões práticas para o próximo lote de posts.
