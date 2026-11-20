"""Gerencia o token do Instagram.

    python scripts/ig_token.py verificar   # mostra qual conta o token acessa
    python scripts/ig_token.py renovar     # renova (mais 60 dias), grava no .env e no secret do GitHub

O token NUNCA é impresso. Para colocar o primeiro token, crie o arquivo .env com:
    IG_TOKEN=cole_aqui
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import instagram as ig  # noqa: E402

CONFIG = json.loads((ig.RAIZ / "config.json").read_text())


def gravar_env(novo: str):
    env = ig.RAIZ / ".env"
    linhas = [l for l in (env.read_text().splitlines() if env.exists() else []) if not l.startswith("IG_TOKEN=")]
    linhas.insert(0, f"IG_TOKEN={novo}")
    env.write_text("\n".join(linhas) + "\n")
    env.chmod(0o600)


def gravar_secret(novo: str):
    repo = CONFIG.get("github_repo")
    if not repo:
        print("  (sem github_repo no config.json — secret do GitHub não atualizado)")
        return
    r = subprocess.run(["gh", "secret", "set", "IG_TOKEN", "--repo", repo], input=novo, text=True,
                       capture_output=True)
    print("  secret IG_TOKEN atualizado no GitHub" if r.returncode == 0 else f"  falha no gh: {r.stderr.strip()}")


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else "verificar"
    try:
        if acao == "verificar":
            c = ig.eu()
            print(f"✓ token válido para @{c['username']} (id {c['user_id']}, tipo {c.get('account_type')})")
        elif acao == "renovar":
            novo = ig.renovar_token()
            gravar_env(novo)
            print("✓ token renovado (+60 dias) e gravado no .env")
            gravar_secret(novo)
        else:
            sys.exit(__doc__)
    except ig.ErroInstagram as e:
        sys.exit(f"Erro: {e}")
