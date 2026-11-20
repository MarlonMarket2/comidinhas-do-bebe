"""Publica no Instagram os posts APROVADOS cujo horário já chegou.

Regras:
- Só publica status "aprovado" (rascunho nunca sai).
- Um post por execução, do mais antigo para o mais novo.
- Posts com mais de 24 h de atraso não saem sozinhos (evita rajada depois de pane):
  ficam como "atrasado" para você decidir.

Uso:
    python scripts/publicar.py              # publica o próximo post vencido
    python scripts/publicar.py --simular    # mostra o que faria, sem chamar a API
    python scripts/publicar.py --agora 03-palitinhos   # força um post aprovado agora
"""
import argparse
import json
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
import instagram as ig  # noqa: E402

RAIZ = ig.RAIZ
CONFIG = json.loads((RAIZ / "config.json").read_text())
FUSO = ZoneInfo(CONFIG["fuso"])
ATRASO_MAX = timedelta(hours=24)


def posts_aprovados():
    for arq in sorted((RAIZ / "conteudo").glob("*/*.json")):
        post = json.loads(arq.read_text())
        if post.get("status") == "aprovado":
            quando = datetime.fromisoformat(f"{post['data']}T{post['hora']}").replace(tzinfo=FUSO)
            yield quando, arq, post


def imagens(arq: Path) -> list[Path]:
    pasta = RAIZ / "saida" / arq.parent.name / arq.stem
    return sorted(pasta.glob("*.jpg"))


def url_publica(img: Path) -> str:
    base = CONFIG.get("midia_base_url", "").rstrip("/")
    if not base:
        raise SystemExit("Defina 'midia_base_url' no config.json (endereço público das imagens).")
    rel = img.relative_to(RAIZ).as_posix()
    return f"{base}/{urllib.request.quote(rel)}"


def checar_url(u: str) -> bool:
    try:
        req = urllib.request.Request(u, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200 and "image" in r.headers.get("Content-Type", "")
    except Exception:
        return False


def legenda(post: dict) -> str:
    txt = post["legenda"].strip()
    tags = post.get("hashtags", [])
    if tags:
        txt += "\n\n" + " ".join(tags)
    if len(txt) > 2200:
        raise SystemExit(f"Legenda com {len(txt)} caracteres (máx. 2200).")
    if len(tags) > 30:
        raise SystemExit("Mais de 30 hashtags.")
    return txt


def salvar(arq: Path, post: dict):
    arq.write_text(json.dumps(post, ensure_ascii=False, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--agora", help="prefixo do arquivo de um post aprovado para publicar já")
    a = ap.parse_args()

    agora = datetime.now(FUSO)
    candidatos = []
    for quando, arq, post in posts_aprovados():
        if a.agora:
            if arq.stem.startswith(a.agora):
                candidatos.append((quando, arq, post))
        elif quando <= agora:
            if agora - quando > ATRASO_MAX:
                print(f"! {arq.stem}: {agora - quando} de atraso — marcado como 'atrasado', não publicado.")
                post["status"] = "atrasado"
                if not a.simular:
                    salvar(arq, post)
                continue
            candidatos.append((quando, arq, post))

    if not candidatos:
        prox = min((q for q, _, _ in posts_aprovados()), default=None)
        print("Nada para publicar agora." + (f" Próximo aprovado: {prox:%d/%m %H:%M}." if prox else ""))
        return

    quando, arq, post = candidatos[0]
    imgs = imagens(arq)
    if not imgs:
        raise SystemExit(f"{arq.stem}: nenhuma imagem em saida/ — rode o render.py.")
    urls = [url_publica(i) for i in imgs]
    texto = legenda(post)

    print(f"→ {arq.stem} ({quando:%d/%m %H:%M}) — {len(urls)} imagem(ns)")
    fora = [u for u in urls if not checar_url(u)]
    if fora:
        msg = f"{len(fora)} imagem(ns) sem acesso público ainda (ex.: {fora[0]})."
        if a.simular:
            print("  aviso: " + msg)
        else:
            raise SystemExit(msg + " Faça o push das imagens antes.")

    if a.simular:
        print("  [simulação] legenda:\n" + "\n".join("    " + l for l in texto.splitlines()))
        return

    conta = ig.eu()
    if conta["username"].lower() != CONFIG["perfil"].lstrip("@").lower():
        raise SystemExit(f"Token é da conta @{conta['username']}, esperado {CONFIG['perfil']}. Abortado.")
    if len(urls) == 1:
        mid = ig.publicar_imagem(conta["user_id"], urls[0], texto)
    else:
        mid = ig.publicar_carrossel(conta["user_id"], urls, texto)

    post["status"] = "publicado"
    post["publicado_em"] = datetime.now(FUSO).isoformat(timespec="seconds")
    post["ig_media_id"] = mid
    try:
        post["permalink"] = ig.permalink(mid)
    except ig.ErroInstagram:
        pass
    salvar(arq, post)
    print(f"✓ publicado: {post.get('permalink', mid)}")


if __name__ == "__main__":
    try:
        main()
    except ig.ErroInstagram as e:
        sys.exit(f"Erro da API do Instagram: {e}")
