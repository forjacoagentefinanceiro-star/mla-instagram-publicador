"""
agenda.py — publica os itens vencidos de agenda.json (horario local do PC).
Rodado a cada 15 min pelo Agendador de Tarefas do Windows.

  python agenda.py            publica o que venceu
  python agenda.py --list     mostra a fila
  python agenda.py --dry-run  mostra o que seria publicado agora, sem publicar
"""
import json, subprocess, sys, os
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENDA = ROOT / "agenda.json"
LOG = ROOT / "agenda.log"
PUBLISH = ROOT / "scripts" / "publish_instagram.py"
MAX_ATRASO = timedelta(hours=12)  # se o PC ficou desligado mais que isso, nao publica fora de hora


def log(msg):
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load():
    return json.loads(AGENDA.read_text(encoding="utf-8"))


def save(items):
    AGENDA.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def run_item(it):
    cmd = [sys.executable, str(PUBLISH), "--images", *[str(ROOT / p) for p in it["files"]]]
    if it["type"] == "reel":
        cmd += ["--reel", "--caption", it["caption"]]
    elif it["type"] == "story":
        cmd += ["--story"]
    else:
        cmd += ["--caption", it["caption"]]
    env = {**os.environ, "PYTHONUTF8": "1"}
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env, timeout=1200)


def main():
    items = load()
    now = datetime.now()
    if "--list" in sys.argv:
        for it in items:
            print(f"{it['when']}  {it['type']:<6} {it.get('status','pendente'):<10} {it['id']}")
        return
    dry = "--dry-run" in sys.argv
    if not dry and (ROOT / "NUVEM_ATIVA").exists():
        # a publicação roda no GitHub Actions; este PC não publica, para não duplicar posts
        log("NUVEM_ATIVA presente: o GitHub Actions publica. Nada a fazer neste PC.")
        return
    changed = False
    for it in items:
        if it.get("status", "pendente") != "pendente":
            continue
        when = datetime.fromisoformat(it["when"])
        if when > now:
            continue
        if now - when > MAX_ATRASO:
            if dry:
                log(f"[dry-run] marcaria como perdido: {it['id']}")
                continue
            it["status"] = "perdido"
            log(f"PERDIDO (PC desligado?): {it['id']} previsto {it['when']}")
            changed = True
            continue
        if dry:
            log(f"[dry-run] publicaria agora: {it['id']} ({it['type']})")
            continue
        it["status"] = "em_andamento"
        save(items)
        log(f"Publicando {it['id']} ({it['type']})...")
        try:
            r = run_item(it)
            ok = r.returncode == 0
            out = (r.stdout + r.stderr).strip()
        except Exception as e:  # timeout etc.
            ok, out = False, str(e)
        it["status"] = "publicado" if ok else "erro"
        it["resultado"] = out[-600:]
        log(("OK " if ok else "ERRO ") + it["id"] + "\n" + out[-600:])
        changed = True
    if changed:
        save(items)


if __name__ == "__main__":
    main()
