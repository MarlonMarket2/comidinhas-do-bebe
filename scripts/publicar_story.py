"""Publica imagens como stories (a imagem precisa já estar no GitHub).

Uso:
    python scripts/publicar_story.py saida/destaques/story-guia.jpg [outras.jpg ...]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import instagram as ig  # noqa: E402
from publicar import CONFIG, checar_url, url_publica  # noqa: E402

if len(sys.argv) < 2:
    sys.exit(__doc__)

conta = ig.eu()
if conta["username"].lower() != CONFIG["perfil"].lstrip("@").lower():
    sys.exit(f"Token é da conta @{conta['username']}, esperado {CONFIG['perfil']}.")

for caminho in sys.argv[1:]:
    img = (ig.RAIZ / caminho).resolve()
    url = url_publica(img)
    if not checar_url(url):
        sys.exit(f"Imagem sem acesso público: {url} — faça o push antes.")
    try:
        mid = ig.publicar_story(conta["user_id"], url)
        print(f"✓ story publicado: {img.name} (id {mid})")
    except ig.ErroInstagram as e:
        sys.exit(f"Erro em {img.name}: {e}")
