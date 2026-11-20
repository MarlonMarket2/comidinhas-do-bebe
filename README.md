# Comidinhas do Bebê — automação de conteúdo

Perfil: **@comidinhasdobebe.dicas** · Afiliado Hotmart (e-book de introdução alimentar).

## Fluxo semanal

1. **Criar** — o Claude escreve os 7 posts da semana em `conteudo/AAAA-MM-DD/*.json`.
2. **Renderizar** — gera as artes 1080×1350 e a prévia:
   ```bash
   .venv/bin/python scripts/render.py conteudo/2026-11-23
   ```
   Abra `saida/2026-11-23/previa.html` para revisar.
3. **Aprovar** — nada é publicado sem aprovação:
   ```bash
   .venv/bin/python scripts/aprovar.py conteudo/2026-11-23 todos
   ```
   (ou peça ao Claude: "aprova 1, 2 e 5", "refaz a 3 com outra receita")
4. **Publicar** — o GitHub Actions (`.github/workflows/publicar.yml`) roda a cada 20 min e chama
   `scripts/publicar.py`, que posta **só os aprovados**, um por vez, quando chega o dia/hora do post,
   pela API oficial do Instagram. Depois grava `status: publicado` + link do post no JSON.
   - Teste local sem publicar: `.venv/bin/python scripts/publicar.py --simular`
   - Post com mais de 24 h de atraso vira `atrasado` e não sai sozinho.
   - As imagens precisam estar em URL pública (`midia_base_url` no config) — o push para o GitHub resolve.

## Token do Instagram

- Fica no `.env` local (fora do git) e no secret `IG_TOKEN` do repositório no GitHub.
- Vale 60 dias. `.venv/bin/python scripts/ig_token.py renovar` renova e atualiza os dois lugares
  (rodar a cada aprovação semanal). `... ig_token.py verificar` confere a conta.

## Estrutura

| Pasta/arquivo | O que é |
|---|---|
| `config.json` | perfil, links de afiliado, link do guia gratuito, cores, modo do CTA (`bio` ou `comentario`) |
| `templates/carrossel.html` | modelo visual dos slides (identidade do guia gratuito) |
| `conteudo/<semana>/` | um JSON por post: data, hora, slides, legenda, hashtags, status |
| `saida/<semana>/` | PNGs gerados + `previa.html` |

Tipos de slide: `capa`, `lista`, `passos`, `tabela`, `dica`, `alerta`, `cta`.
Na capa, `"foto": "caminho/da/foto.jpg"` substitui o emoji por uma foto real.

## Regras do produtor (não quebrar)

- Nunca usar o nome do produto no nome/@ do perfil nem se apresentar como equipe oficial.
- Não divulgar produtos concorrentes neste perfil.
- 90% receitas para bebês 6m+, 10% dicas relacionadas.
- Repost do perfil oficial só após 7 dias; nunca copiar outros afiliados.

## Regras de segurança do conteúdo

Sem sal e sem açúcar; nada de mel antes de 1 ano; ovo sempre bem cozido; cortes seguros
(uva/tomate-cereja em 4 no comprimento, nada duro e cru); aviso "siga a orientação do pediatra" em toda legenda.
