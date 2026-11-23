# Design Doc: Análise de Desempenho e Leitura de Comentários (@comidinhasdobebe.dicas)

**Data:** 2026-11-23  
**Status:** Proposto (Aguardando aprovação)  
**Autor:** Antigravity & Marlon  

---

## 1. Intenção e Objetivo (O "Porquê")
O perfil `@comidinhasdobebe.dicas` tem como objetivo gerar tráfego qualificado e conversões como afiliado Hotmart no nicho de introdução alimentar infantil. Para crescer de forma consistente sem depender de intuição ou experiência prévia avançada em marketing, o proprietário precisa de um mecanismo automatizado que colete dados reais do perfil (engajamento, métricas dos posts e o texto dos comentários), traduzindo-os em diagnósticos práticos em linguagem simples para orientar o conteúdo das semanas seguintes.

---

## 2. Metas, Não-Metas e Anti-Metas

### Metas (Goals)
- Desenvolver um script independente (`scripts/analisar.py`) que consome a API oficial do Instagram (Graph API).
- Coletar as mídias publicadas, contagem de curtidas, contagem de comentários e o texto completo de cada comentário via endpoint oficial `/{media_id}/comments`.
- Tentar coletar métricas de alcance/impressões/salvamentos (`/{media_id}/insights`); caso a permissão de insights não esteja concedida pelo token, o script deve degradar suavemente (graceful fallback) e reportar com base nas métricas públicas disponíveis (curtidas, comentários e taxa de engajamento).
- Gerar um relatório analítico estruturado e didático em Markdown (`relatorios/AAAA-MM-DD.md`) contendo:
  1. **Top Posts e Desempenho:** ranking de engajamento dos posts publicados.
  2. **Radar de Comentários & Voz do Público:** classificação automática dos comentários em categorias (Dúvidas/Medos, Pedidos de Receitas, Elogios, e Leads que comentaram a palavra-chave de CTA, ex.: "PRATINHO").
  3. **Plano de Ação Semanal (Marketing Feedback):** recomendações diretas sobre quais ingredientes, temas e formatos funcionaram melhor e devem ser priorizados na próxima criação semanal.
- Criar a skill correspondente em `.agents/skills/comidinhas-analisar-perfil/SKILL.md` para permitir que o usuário execute a análise a qualquer momento com o comando *"analise o perfil"* ou *"gere o relatório de desempenho"*.

### Não-Metas (Non-Goals)
- Não responderá comentários automaticamente no Instagram (respostas diretas exigem moderação humana ou ferramentas de direct dedicadas como ManyChat).
- Não criará dashboards pesados com banco de dados externo ou servidor web em execução contínua.

### Anti-Metas (Anti-Goals)
- Evitar jargões técnicos herméticos de marketing digital que confundam o usuário (ex.: não focar em fórmulas complexas sem contexto).
- Não travar nem lançar exceção se a API da Meta negar permissões de insights avançados: o relatório deve sempre ser gerado com os dados disponíveis.

---

## 3. Restrições (Constraints)
- Usar apenas bibliotecas padrão do Python (sem dependências pesadas externas, alinhado com `scripts/instagram.py`).
- Compatível tanto no macOS local quanto em execuções no CI/GitHub Actions.
- O token da Meta pode ser de Usuário do Sistema ou Usuário com expiração; tratar erros de autenticação com orientações claras.

---

## 4. Abordagens Consideradas

1. **Abordagem 1: Script CLI + Relatório Didático em Markdown (`relatorios/AAAA-MM-DD.md`) [ESCOLHIDA]**
   - *Por que foi escolhida:* O usuário tem pouco conhecimento prévio de marketing e prefere uma leitura direta, clara e orientada a ações práticas. É leve, versionável no Git e serve de insumo imediato para a IA na criação dos posts da semana seguinte.
2. **Abordagem 2: Dashboard Visual em HTML (`saida/analytics.html`)**
   - *Trade-off:* Mais código visual para manter; o relatório em Markdown já atende perfeitamente ao consumo do usuário e do agente.
3. **Abordagem 3: Monitoramento Contínuo com Alertas Diários de Comentários**
   - *Trade-off:* Prematuro para o volume atual de tráfego e posts do perfil.

---

## 5. Arquitetura da Solução

### Componentes:
- **`scripts/analisar.py`**:
  - Parâmetros: `python scripts/analisar.py [--dias N] [--saida caminho]`
  - Funções:
    - `obter_posts_recentes(user_id, limite)`
    - `obter_comentarios_post(media_id)`
    - `obter_insights_post(media_id)` (com tratamento de erro silencioso se faltar escopo)
    - `categorizar_comentarios(comentarios, palavra_cta)`
    - `gerar_diagnostico_marketing(posts, categorias)`
    - `salvar_relatorio_markdown(dados, destino)`
- **`relatorios/`**:
  - Diretório para armazenar os relatórios semanais gerados (ex.: `relatorios/2026-11-23.md`).
- **`.agents/skills/comidinhas-analisar-perfil/SKILL.md`**:
  - Skill que ensina o agente a executar a análise, resumir os achados e aplicar o feedback na criação de novos posts.

---

## 6. O que fica a cargo do construtor (Decisões de Implementação)
- Regras de heurística simples para categorização dos comentários (palavras-chave como "como fazer", "pode congelar", "comprar", "receita de", "meu bebê não quer").
- Formatação das tabelas e seções dentro do Markdown para máxima legibilidade.
