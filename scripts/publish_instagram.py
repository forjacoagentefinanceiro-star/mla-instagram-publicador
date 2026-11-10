"""
publish_instagram.py — Publica foto única ou carrossel no Instagram (conta MLA Containers)
via Instagram API with Instagram Login (graph.instagram.com).

Uso:
  python publish_instagram.py --images a.png b.png --caption "texto"   # carrossel (2-10)
  python publish_instagram.py --images a.png --caption "texto"         # foto única
  python publish_instagram.py --images a.png b.png --caption "x" --dry-run
"""
import argparse, os, sys, time, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

IG_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
BASE = f"https://graph.instagram.com/{os.getenv('META_API_VERSION', 'v21.0')}"


def host_image(path: str) -> str:  # tambem hospeda video
    """Hospeda a imagem em URL publica (a API exige URL, nao aceita arquivo local)."""
    ext = path.lower().rsplit(".", 1)[-1]
    mime = {"png": "image/png", "mp4": "video/mp4", "mov": "video/quicktime"}.get(ext, "image/jpeg")
    name = Path(path).name
    errors = []
    # 1) litterbox (temporario 72h)  2) uguu.se (reserva)
    try:
        with open(path, "rb") as f:
            r = requests.post(
                "https://litterbox.catbox.moe/resources/internals/api.php",
                data={"reqtype": "fileupload", "time": "72h"},
                files={"fileToUpload": (name, f, mime)},
                timeout=120,
            )
        url = r.text.strip()
        if url.startswith("https://"):
            print(f"  Hospedada: {url}")
            return url
        errors.append(f"litterbox: {url}")
    except requests.RequestException as e:
        errors.append(f"litterbox: {e}")
    try:
        with open(path, "rb") as f:
            r = requests.post("https://uguu.se/upload", files={"files[]": (name, f, mime)}, timeout=120)
        url = r.json()["files"][0]["url"]
        print(f"  Hospedada: {url}")
        return url
    except Exception as e:
        errors.append(f"uguu: {e}")
    raise RuntimeError(f"Falha no upload: {errors}")


def post(endpoint: str, data: dict) -> dict:
    data["access_token"] = TOKEN
    r = requests.post(f"{BASE}/{endpoint}", data=data, timeout=60)
    res = r.json()
    if "id" not in res:
        raise RuntimeError(f"{endpoint}: {res}")
    return res


def wait_ready(container_id: str, tries: int = 24) -> None:
    for i in range(tries):
        r = requests.get(f"{BASE}/{container_id}",
                         params={"fields": "status_code", "access_token": TOKEN}, timeout=30)
        status = r.json().get("status_code", "")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container {status}: {r.json()}")
        print(f"  Processando... {i * 5}s")
        time.sleep(5)
    raise RuntimeError("Timeout no processamento")


def run(images: list, caption: str, dry_run: bool, story: bool = False, reel: bool = False):
    if not IG_ID or not TOKEN:
        sys.exit("ERRO: credenciais nao encontradas no .env")
    if not 1 <= len(images) <= 10:
        sys.exit("ERRO: use de 1 a 10 imagens.")
    for p in images:
        if not Path(p).exists():
            sys.exit(f"ERRO: arquivo nao encontrado: {p}")

    print(f"\nPublicando {len(images)} imagem(ns) em @{os.getenv('INSTAGRAM_USERNAME')}...")
    if dry_run:
        print("[DRY RUN] Tudo OK. Remova --dry-run para publicar.")
        return

    if reel:
        if len(images) != 1:
            sys.exit("ERRO: --reel aceita exatamente 1 video.")
        print("\n1/2 Enviando video e criando Reel (pode levar 1-3 min)...")
        container = post(f"{IG_ID}/media", {"media_type": "REELS", "video_url": host_image(images[0]),
                                            "caption": caption, "share_to_feed": "true"})["id"]
        wait_ready(container, tries=60)
        print("\n2/2 Publicando...")
        reel_id = post(f"{IG_ID}/media_publish", {"creation_id": container})["id"]
        print(f"\nReel publicado! ID: {reel_id}")
        return

    if story:
        # Cada imagem vira um story separado (1080x1920). Legenda nao se aplica.
        for p in images:
            print(f"\nStory: {Path(p).name}")
            container = post(f"{IG_ID}/media", {"media_type": "STORIES", "image_url": host_image(p)})["id"]
            wait_ready(container)
            print(f"  Story publicado. ID: {post(f'{IG_ID}/media_publish', {'creation_id': container})['id']}")
            time.sleep(3)
        return

    if len(images) == 1:
        print("\n1/2 Criando container...")
        container = post(f"{IG_ID}/media", {"image_url": host_image(images[0]), "caption": caption})["id"]
    else:
        print("\n1/3 Criando itens do carrossel...")
        children = [post(f"{IG_ID}/media", {"image_url": host_image(p), "is_carousel_item": "true"})["id"]
                    for p in images]
        print("\n2/3 Montando carrossel...")
        container = post(f"{IG_ID}/media", {"media_type": "CAROUSEL",
                                            "children": ",".join(children),
                                            "caption": caption})["id"]

    wait_ready(container)
    print("\nPublicando...")
    post_id = post(f"{IG_ID}/media_publish", {"creation_id": container})["id"]
    print(f"\nPublicado com sucesso! Post ID: {post_id}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", nargs="+", required=True)
    ap.add_argument("--caption", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--story", action="store_true", help="publica cada imagem como story")
    ap.add_argument("--reel", action="store_true", help="publica 1 video como Reel")
    a = ap.parse_args()
    if not a.story and not a.caption:
        ap.error("--caption e obrigatorio (exceto com --story)")
    run(a.images, a.caption, a.dry_run, a.story, a.reel)
