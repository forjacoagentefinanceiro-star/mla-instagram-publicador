"""Teste manual (GitHub Actions): envia 1 arquivo da pasta media para o site de hospedagem e imprime a URL.
Não publica nada no Instagram."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publish_instagram as pi

ROOT = Path(__file__).resolve().parent.parent
arq = next((ROOT / "media").rglob("sem_qua3.jpg"), None) or next((ROOT / "media").rglob("*.jpg"))
print("Enviando", arq)
url = pi.host_image(str(arq))
import requests

r = requests.get(url, timeout=60)
print("URL:", url, "-> HTTP", r.status_code, len(r.content), "bytes")
sys.exit(0 if r.status_code == 200 and len(r.content) > 1000 else 1)
