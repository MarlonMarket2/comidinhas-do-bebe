"""Cliente mínimo da API oficial do Instagram (Instagram API with Instagram Login).

Sem dependências externas: roda no Mac e no GitHub Actions só com Python.
O token vem da variável de ambiente IG_TOKEN ou do arquivo .env na raiz do projeto.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VERSAO = os.environ.get("IG_API_VERSAO", "v23.0")
CONFIG = json.loads((RAIZ / "config.json").read_text())


def _base() -> str:
    """Chave do login do Instagram (IG...) usa graph.instagram.com;
    chave de usuário do sistema da Meta (EAA...) usa graph.facebook.com."""
    host = "graph.instagram.com" if token().startswith("IG") else "graph.facebook.com"
    return f"https://{host}/{VERSAO}"


class ErroInstagram(RuntimeError):
    pass


def ler_env():
    env = RAIZ / ".env"
    if env.exists():
        for linha in env.read_text().splitlines():
            if "=" in linha and not linha.strip().startswith("#"):
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def token() -> str:
    ler_env()
    t = os.environ.get("IG_TOKEN", "").strip()
    if not t:
        raise ErroInstagram("IG_TOKEN não definido (.env local ou secret do GitHub).")
    return t


def _chamar(metodo: str, url: str, params: dict) -> dict:
    params = {**params, "access_token": token()}
    dados = urllib.parse.urlencode(params).encode()
    if metodo == "GET":
        req = urllib.request.Request(f"{url}?{dados.decode()}")
    else:
        req = urllib.request.Request(url, data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        try:
            msg = json.loads(corpo).get("error", {}).get("message", corpo)
        except json.JSONDecodeError:
            msg = corpo
        raise ErroInstagram(f"{metodo} {url.split(VERSAO, 1)[-1]}: HTTP {e.code} — {msg}") from None


def get(caminho: str, **params) -> dict:
    return _chamar("GET", f"{_base()}/{caminho}", params)


def post(caminho: str, **params) -> dict:
    return _chamar("POST", f"{_base()}/{caminho}", params)


def eu() -> dict:
    """Conta conectada ao token: {'user_id', 'username', 'account_type'}."""
    if token().startswith("IG"):
        return get("me", fields="user_id,username,account_type")
    d = get(CONFIG["ig_user_id"], fields="id,username")
    return {"user_id": d["id"], "username": d["username"], "account_type": "BUSINESS (usuário do sistema)"}


def esperar_container(cid: str, limite_s: int = 180):
    inicio = time.time()
    while True:
        st = get(cid, fields="status_code").get("status_code")
        if st in ("FINISHED", "PUBLISHED"):
            return
        if st in ("ERROR", "EXPIRED"):
            raise ErroInstagram(f"container {cid} terminou com status {st}")
        if time.time() - inicio > limite_s:
            raise ErroInstagram(f"container {cid} não ficou pronto em {limite_s}s (status {st})")
        time.sleep(5)


def publicar_carrossel(user_id: str, urls_imagens: list[str], legenda: str) -> str:
    """Publica um carrossel (2 a 10 JPEGs em URLs públicas). Retorna o id da mídia."""
    if not 2 <= len(urls_imagens) <= 10:
        raise ErroInstagram(f"carrossel precisa de 2 a 10 imagens (recebeu {len(urls_imagens)})")
    filhos = []
    for u in urls_imagens:
        filhos.append(post(f"{user_id}/media", image_url=u, is_carousel_item="true")["id"])
    for f in filhos:
        esperar_container(f)
    cid = post(f"{user_id}/media", media_type="CAROUSEL", children=",".join(filhos), caption=legenda)["id"]
    esperar_container(cid)
    return post(f"{user_id}/media_publish", creation_id=cid)["id"]


def publicar_imagem(user_id: str, url_imagem: str, legenda: str) -> str:
    cid = post(f"{user_id}/media", image_url=url_imagem, caption=legenda)["id"]
    esperar_container(cid)
    return post(f"{user_id}/media_publish", creation_id=cid)["id"]


def publicar_story(user_id: str, url_imagem: str) -> str:
    """Publica uma imagem 9:16 (JPEG em URL pública) como story. Retorna o id da mídia."""
    cid = post(f"{user_id}/media", image_url=url_imagem, media_type="STORIES")["id"]
    esperar_container(cid)
    return post(f"{user_id}/media_publish", creation_id=cid)["id"]


def permalink(media_id: str) -> str:
    return get(media_id, fields="permalink").get("permalink", "")


def renovar_token() -> str:
    """Troca o token de longa duração por um novo (vale mais 60 dias)."""
    if not token().startswith("IG"):
        raise ErroInstagram("esta chave é de usuário do sistema e nunca expira — não precisa renovar.")
    req = urllib.request.Request(
        "https://graph.instagram.com/refresh_access_token?"
        + urllib.parse.urlencode({"grant_type": "ig_refresh_token", "access_token": token()})
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["access_token"]
    except urllib.error.HTTPError as e:
        raise ErroInstagram(f"falha ao renovar token: HTTP {e.code} — {e.read().decode(errors='replace')}") from None
