"""Gera as capas dos destaques e os stories que vão dentro deles.

Uso: .venv/bin/python scripts/render_destaques.py
Saída: saida/destaques/capa-*.jpg e story-*.jpg (1080x1920)
"""
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RAIZ / "config.json").read_text())

DESTAQUES = [
    {"id": "guia", "nome": "Guia grátis", "emoji": "🎁", "cor": "terracota"},
    {"id": "receitas", "nome": "Receitas", "emoji": "🥣", "cor": "verde"},
    {"id": "cortes", "nome": "Cortes seguros", "emoji": "🍇", "cor": "terracota"},
    {"id": "sobre", "nome": "Sobre", "emoji": "💛", "cor": "verde"},
]


def receitas_da_semana():
    semanas = sorted((RAIZ / "conteudo").iterdir())
    itens = []
    for arq in sorted(semanas[-1].glob("*.json")):
        p = json.loads(arq.read_text())
        if p.get("pilar") == "receita":
            capa = p["slides"][0]
            itens.append((capa.get("emoji", "🥄"), capa["titulo"]))
    return itens


def main():
    env = Environment(loader=FileSystemLoader(RAIZ / "templates"), autoescape=True)
    html = env.get_template("destaques.html").render(
        destaques=DESTAQUES, receitas=receitas_da_semana(), perfil=CONFIG["perfil"],
        nome_guia=CONFIG["nome_guia"], cores=CONFIG["cores"])
    out = RAIZ / "saida" / "destaques"
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_destaques.html"
    tmp.write_text(html)
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=CONFIG["chrome"])
        pg = nav.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(tmp.as_uri())
        pg.wait_for_selector("body[data-pronto='1']", timeout=20000)
        for el in pg.query_selector_all("section"):
            nome = el.get_attribute("id")
            el.screenshot(path=str(out / f"{nome}.jpg"), type="jpeg", quality=92)
            print("✓", nome)
        nav.close()
    tmp.unlink()


if __name__ == "__main__":
    main()
