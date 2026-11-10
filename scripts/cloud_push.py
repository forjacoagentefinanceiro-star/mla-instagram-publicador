"""Sincroniza a fila com a nuvem (GitHub Actions publica a cada 15 min, sem o PC ligado).

  python scripts/cloud_push.py pull   baixa o status mais novo (RODAR ANTES de editar agenda.json)
  python scripts/cloud_push.py push   sobe agenda.json + mídias dos itens pendentes e envia
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, text=True, encoding="utf-8", capture_output=True)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)}\n{r.stdout}\n{r.stderr}")
    return r


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "pull":
        print(git("pull", "--rebase", "--autostash").stdout.strip() or "ok")
    elif cmd == "push":
        git("pull", "--rebase", "--autostash")
        itens = json.loads((ROOT / "agenda.json").read_text(encoding="utf-8"))
        for it in itens:
            if it.get("status", "pendente") == "pendente":
                for f in it["files"]:
                    git("add", "-f", f)
        git("add", "agenda.json")
        if git("diff", "--cached", "--quiet", check=False).returncode:
            git("commit", "-m", "agenda: novos itens")
            git("push")
            print("enviado para a nuvem")
        else:
            print("nada novo para enviar")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
