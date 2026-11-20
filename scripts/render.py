"""Renderiza os carrosséis de uma semana e gera a página de prévia.

Uso:
    .venv/bin/python scripts/render.py conteudo/2026-11-23
    .venv/bin/python scripts/render.py conteudo/2026-11-23 --so 03-panqueca   # um post só
"""
import argparse
import html
import json
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RAIZ / "config.json").read_text())
env = Environment(loader=FileSystemLoader(RAIZ / "templates"), autoescape=True)


def carregar_posts(pasta: Path, so: str | None):
    for arq in sorted(pasta.glob("*.json")):
        if so and not arq.stem.startswith(so):
            continue
        yield arq, json.loads(arq.read_text())


def renderizar(pasta: Path, so: str | None = None):
    saida_semana = RAIZ / "saida" / pasta.name
    tpl = env.get_template("carrossel.html")
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=CONFIG["chrome"])
        pg = nav.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for arq, post in carregar_posts(pasta, so):
            destino = saida_semana / arq.stem
            destino.mkdir(parents=True, exist_ok=True)
            for velho in list(destino.glob("*.png")) + list(destino.glob("*.jpg")):
                velho.unlink()
            # Dias alternados = capas alternadas (terracota/verde): a grade 3x fica em xadrez.
            dia = date.fromisoformat(post["data"]).toordinal()
            capa_cor = post.get("capa_cor") or ("verde" if dia % 2 else "terracota")
            html_doc = tpl.render(post=post, perfil=CONFIG["perfil"], nome_guia=CONFIG["nome_guia"], capa_cor=capa_cor,
                                  cta_modo=CONFIG["cta_modo"], palavra_comentario=CONFIG["palavra_comentario"],
                                  cores=CONFIG["cores"])
            tmp = destino / "_slides.html"
            tmp.write_text(html_doc)
            pg.goto(tmp.as_uri())
            pg.wait_for_selector("body[data-pronto='1']", timeout=20000)
            slides = pg.query_selector_all(".slide")
            for i, el in enumerate(slides, 1):
                # Instagram só aceita JPEG pela API
                el.screenshot(path=str(destino / f"{i:02d}.jpg"), type="jpeg", quality=92)
            tmp.unlink()
            print(f"✓ {arq.stem}: {len(slides)} slides")
        nav.close()
    gerar_previa(pasta)


def legenda_completa(post):
    return post["legenda"].strip() + "\n\n" + " ".join(post.get("hashtags", []))


def gerar_previa(pasta: Path):
    saida_semana = RAIZ / "saida" / pasta.name
    blocos = []
    for arq, post in carregar_posts(pasta, None):
        imgs = sorted((saida_semana / arq.stem).glob("*.jpg"))
        tira = "".join(f'<img src="{arq.stem}/{i.name}" loading="lazy">' for i in imgs)
        status = post.get("status", "rascunho")
        blocos.append(f"""
        <article>
          <header><span class="data">{post['data']} · {post['hora']}</span>
            <span class="status {status}">{status}</span><code>{arq.stem}</code></header>
          <div class="tira">{tira}</div>
          <pre>{html.escape(legenda_completa(post))}</pre>
        </article>""")
    doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prévia {pasta.name}</title><style>
body{{font-family:system-ui,sans-serif;background:#f4efe8;margin:0;padding:24px;color:#3b2f2a}}
h1{{margin:0 0 20px}} article{{background:#fff;border-radius:16px;padding:20px;margin-bottom:28px}}
header{{display:flex;gap:12px;align-items:center;margin-bottom:12px;flex-wrap:wrap}}
.data{{font-weight:800}} code{{color:#999}}
.status{{padding:3px 10px;border-radius:99px;font-size:13px;font-weight:700;background:#eee}}
.status.aprovado{{background:#d8ecd9;color:#2d6a3a}} .status.publicado{{background:#d6e4f5;color:#244c7a}}
.tira{{display:flex;gap:10px;overflow-x:auto;padding-bottom:8px}}
.tira img{{height:420px;border-radius:10px;flex:none}}
pre{{white-space:pre-wrap;font-family:inherit;background:#faf7f2;padding:14px;border-radius:10px;font-size:14px;line-height:1.5}}
</style></head><body><h1>Semana {pasta.name} — {CONFIG['perfil']}</h1>{''.join(blocos)}</body></html>"""
    (saida_semana / "previa.html").write_text(doc)
    print(f"Prévia: {saida_semana / 'previa.html'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta", help="pasta da semana, ex: conteudo/2026-11-23")
    ap.add_argument("--so", help="prefixo do arquivo para renderizar um post só")
    a = ap.parse_args()
    pasta = (RAIZ / a.pasta).resolve() if not Path(a.pasta).is_absolute() else Path(a.pasta)
    if not pasta.is_dir():
        sys.exit(f"Pasta não encontrada: {pasta}")
    renderizar(pasta, a.so)
