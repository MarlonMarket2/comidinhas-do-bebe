"""Marca posts como aprovados (ou volta para rascunho) e atualiza a prévia.

Uso:
    .venv/bin/python scripts/aprovar.py conteudo/2026-11-23 01 02 05     # aprova esses
    .venv/bin/python scripts/aprovar.py conteudo/2026-11-23 todos         # aprova a semana
    .venv/bin/python scripts/aprovar.py conteudo/2026-11-23 03 --voltar   # volta para rascunho
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render import RAIZ, gerar_previa  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("pasta")
ap.add_argument("ids", nargs="+", help="prefixos dos arquivos (01, 02...) ou 'todos'")
ap.add_argument("--voltar", action="store_true")
a = ap.parse_args()

pasta = (RAIZ / a.pasta).resolve()
novo = "rascunho" if a.voltar else "aprovado"
for arq in sorted(pasta.glob("*.json")):
    if "todos" in a.ids or any(arq.stem.startswith(i) for i in a.ids):
        post = json.loads(arq.read_text())
        if post.get("status") == "publicado":
            print(f"- {arq.stem}: já publicado, ignorado")
            continue
        post["status"] = novo
        arq.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n")
        print(f"✓ {arq.stem}: {novo}")
gerar_previa(pasta)
