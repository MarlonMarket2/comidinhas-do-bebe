"""Módulo de inteligência e análise de desempenho do Instagram.

Coleta dados de mídias, curtidas, comentários e insights do perfil,
classifica comentários (dúvidas, pedidos, CTAs, elogios) e gera relatórios
didáticos com recomendações práticas para pautar a criação de conteúdo.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
try:
    import instagram as ig
except ImportError:
    from scripts import instagram as ig


def categorizar_comentario(comentario: dict, palavra_cta: str = "PRATINHO") -> str:
    """Categoriza um comentário com base no conteúdo textual."""
    texto = comentario.get("text", "").lower().strip()
    cta = palavra_cta.lower().strip()

    if cta and cta in texto:
        return "cta_lead"

    duvida_padroes = [
        r"\bcomo\b",
        r"\bquando\b",
        r"\bpode\b",
        r"\bcongelar\b",
        r"\bconserva\b",
        r"\bdura\b",
        r"\bengasg",
        r"\bidade\b",
        r"\bmeses\b",
        r"\balerg",
        r"\?",
    ]
    if any(re.search(p, texto) for p in duvida_padroes):
        return "duvida"

    pedido_padroes = [
        r"\bfaz\b",
        r"\breceita de\b",
        r"\btem de\b",
        r"\bensina\b",
        r"\bmostra\b",
        r"\bqueria ver\b",
        r"\bcomidinhas\b",
    ]
    if any(re.search(p, texto) for p in pedido_padroes):
        return "pedido_receita"

    elogio_padroes = [
        r"\bbom\b",
        r"\blindo\b",
        r"\bamei\b",
        r"\badorou\b",
        r"\bperfeito\b",
        r"\bmaravilh",
        r"\bparabéns\b",
        r"\bparabens\b",
        r"\botimo\b",
        r"\bótimo\b",
        r"\bdelicia\b",
        r"\bdelícia\b",
        r"❤️",
        r"👏",
        r"😍",
    ]
    if any(re.search(p, texto) for p in elogio_padroes):
        return "elogio"

    return "outros"


def classificar_comentarios(comentarios: list[dict], palavra_cta: str = "PRATINHO") -> dict:
    """Agrupa lista de comentários por categoria."""
    resultado = {
        "cta_lead": [],
        "duvida": [],
        "pedido_receita": [],
        "elogio": [],
        "outros": [],
    }
    for c in comentarios:
        cat = categorizar_comentario(c, palavra_cta)
        resultado[cat].append(c)
    return resultado


def calcular_engajamento_posts(posts: list[dict]) -> list[dict]:
    """Calcula métricas agregadas e ordena posts por engajamento decrescente."""
    ranking = []
    for p in posts:
        likes = p.get("like_count") or 0
        comments = p.get("comments_count") or 0
        engajamento = likes + comments
        p_copia = dict(p)
        p_copia["engajamento_total"] = engajamento
        ranking.append(p_copia)

    ranking.sort(key=lambda x: x["engajamento_total"], reverse=True)
    return ranking


def gerar_relatorio_markdown(ranking_posts: list[dict], categorias: dict, total_posts: int) -> str:
    """Gera relatório didático e amigável em Markdown."""
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    linhas = [
        f"# Relatório de Desempenho e Inteligência — {agora}",
        "",
        "> 💡 **Resumo Executivo:** Este relatório analisa os posts publicados no perfil, "
        "o engajamento do público e as dúvidas das mães para orientar os próximos posts.",
        "",
        "---",
        "",
        "## 1. 🏆 Desempenho dos Posts",
        "",
    ]

    if not ranking_posts:
        linhas.append("_Nenhum post encontrado no período analisado._\n")
    else:
        linhas.append("| Post | Tipo | Curtidas | Comentários | Engajamento Total | Link |")
        linhas.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for p in ranking_posts:
            titulo = (p.get("caption") or "Sem legenda").split("\n")[0][:45]
            tipo = p.get("media_type", "POST")
            likes = p.get("like_count", 0)
            comm = p.get("comments_count", 0)
            eng = p.get("engajamento_total", 0)
            link = f"[Ver post]({p['permalink']})" if p.get("permalink") else "-"
            linhas.append(f"| {titulo} | `{tipo}` | {likes} | {comm} | **{eng}** | {link} |")
        linhas.append("")

    linhas.extend([
        "---",
        "",
        "## 2. 💬 Voz do Público (Radar de Comentários)",
        "",
    ])

    total_cta = len(categorias.get("cta_lead", []))
    total_duvidas = len(categorias.get("duvida", []))
    total_pedidos = len(categorias.get("pedido_receita", []))
    total_elogios = len(categorias.get("elogio", []))

    linhas.append(f"- **Pedidos do Guia Gratuito / CTA:** {total_cta}")
    linhas.append(f"- **Dúvidas e Medos levantados:** {total_duvidas}")
    linhas.append(f"- **Pedidos de novas receitas:** {total_pedidos}")
    linhas.append(f"- **Elogios e incentivos:** {total_elogios}")
    linhas.append("")

    if total_cta > 0:
        linhas.append("### 🎯 Leads Interessadas no Guia / E-book:")
        for c in categorias["cta_lead"]:
            linhas.append(f"- `@{c.get('username', 'usuario')}`: \"{c.get('text', '')}\"")
        linhas.append("")

    if total_duvidas > 0:
        linhas.append("### ❓ Dúvidas mais comuns das Mães:")
        for c in categorias["duvida"]:
            linhas.append(f"- `@{c.get('username', 'usuario')}`: \"{c.get('text', '')}\"")
        linhas.append("")

    if total_pedidos > 0:
        linhas.append("### 🍲 Receitas pedidas pelos seguidores:")
        for c in categorias["pedido_receita"]:
            linhas.append(f"- `@{c.get('username', 'usuario')}`: \"{c.get('text', '')}\"")
        linhas.append("")

    linhas.extend([
        "---",
        "",
        "## 3. 🎯 Plano de Ação para os Próximos Posts",
        "",
    ])

    if total_duvidas > 0:
        linhas.append("- **Aproveitar as dúvidas:** Transformar as principais dúvidas das mães em posts do pilar `dica` (ex.: conservação, texturas, cortes seguros).")
    if total_pedidos > 0:
        linhas.append("- **Atender a audiência:** Incluir as receitas mais pedidas no próximo lote de carrosséis da semana.")
    if total_cta > 0:
        linhas.append("- **Atenção ao Direct:** Verificar se todas que comentaram a palavra-chave receberam o link do guia na bio ou direct.")

    linhas.append("- **Manter a proporção 90/10:** Garantir 5-6 receitas atrativas e 1-2 dicas fundamentadas, reforçando o CTA para o e-book ao final.")
    linhas.append("")

    return "\n".join(linhas)


def buscar_dados_perfil(limite: int = 25) -> dict:
    """Busca dados de posts, comentários e métricas do perfil conectado."""
    conta = ig.eu()
    uid = conta["user_id"]

    campos_media = "id,caption,media_type,timestamp,like_count,comments_count,permalink"
    resp_media = ig.get(f"{uid}/media", fields=campos_media, limit=limite)
    posts = resp_media.get("data", [])

    todos_comentarios = []
    for p in posts:
        mid = p["id"]
        try:
            resp_c = ig.get(f"{mid}/comments", fields="id,text,username,timestamp,like_count")
            comms = resp_c.get("data", [])
            for c in comms:
                c["post_id"] = mid
            todos_comentarios.extend(comms)
        except Exception:
            pass

        try:
            resp_ins = ig.get(f"{mid}/insights", metric="impressions,reach,saved")
            p["insights"] = {
                item["name"]: item["values"][0]["value"]
                for item in resp_ins.get("data", [])
                if item.get("values")
            }
        except Exception:
            p["insights"] = {}

    return {
        "user": conta,
        "posts": posts,
        "comentarios": todos_comentarios,
    }


def executar_analise(limite: int = 25, palavra_cta: str = "PRATINHO", destino_arquivo: Path | None = None) -> str:
    """Executa o ciclo completo de análise e geração de relatório."""
    dados = buscar_dados_perfil(limite=limite)
    ranking = calcular_engajamento_posts(dados["posts"])
    categorias = classificar_comentarios(dados["comentarios"], palavra_cta=palavra_cta)
    md = gerar_relatorio_markdown(ranking, categorias, total_posts=len(dados["posts"]))

    if destino_arquivo:
        destino_arquivo = Path(destino_arquivo)
        destino_arquivo.parent.mkdir(parents=True, exist_ok=True)
        destino_arquivo.write_text(md, encoding="utf-8")
        print(f"✓ Relatório salvo em: {destino_arquivo}")

    return md


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Analisa posts e comentários do perfil @comidinhasdobebe.dicas")
    ap.add_argument("--limite", type=int, default=25, help="Quantidade máxima de posts recentes para analisar")
    ap.add_argument("--saida", type=str, default="", help="Caminho do arquivo de saída Markdown")
    args = ap.parse_args()

    config_path = RAIZ / "config.json"
    palavra = "PRATINHO"
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text(encoding="utf-8"))
            palavra = cfg.get("palavra_comentario", "PRATINHO")
        except Exception:
            pass

    if args.saida:
        dest = Path(args.saida)
    else:
        hoje = datetime.now().strftime("%Y-%m-%d")
        dest = RAIZ / "relatorios" / f"{hoje}.md"

    relatorio = executar_analise(limite=args.limite, palavra_cta=palavra, destino_arquivo=dest)
    print("\n--- Resumo do Relatório Gerado ---")
    print("\n".join(relatorio.splitlines()[:15]))
    print("...\n(Relatório completo salvo)")

