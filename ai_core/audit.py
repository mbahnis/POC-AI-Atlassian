"""Journal d'audit des appels à l'IA (une ligne JSON par appel).

On trace qui a appelé quoi, avec quel modèle et quel prompt, combien de
tokens, et ce qui a été masqué. On n'écrit jamais le contenu brut :
seulement une empreinte (hash) pour pouvoir rapprocher deux appels.
"""

import hashlib
import json
import time
from datetime import UTC, datetime


def fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def write_record(path: str, record: dict) -> None:
    record = {"timestamp": datetime.now(UTC).isoformat(), **record}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


class Timer:
    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.ms = int((time.perf_counter() - self._start) * 1000)
