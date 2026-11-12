"""Point d'entrée unique pour appeler l'IA.

Toutes les briques (triage, release notes, revue de PR, post-mortem)
passent par ask(). C'est ici que s'appliquent, toujours dans le même ordre :
  1. chargement du prompt versionné
  2. masquage des données sensibles
  3. appel au fournisseur configuré
  4. écriture du journal d'audit
"""

import json
import re

from .audit import Timer, fingerprint, write_record
from .config import Settings
from .masking import mask
from .prompts import load_prompt
from .providers import AIProvider, AIResponse, get_provider


def ask(
    prompt_name: str,
    variables: dict,
    *,
    settings: Settings | None = None,
    provider: AIProvider | None = None,
    caller: str = "unknown",
) -> AIResponse:
    settings = settings or Settings()
    provider = provider or get_provider(settings.provider)
    prompt = load_prompt(prompt_name)
    model = settings.model_for(prompt.tier)

    user_text = prompt.render(variables)
    masked_counts: dict[str, int] = {}
    if settings.masking_enabled:
        user_text, masked_counts = mask(user_text)

    with Timer() as t:
        response = provider.complete(
            prompt.system, user_text, model, settings.max_tokens, output_schema=prompt.output_schema
        )

    write_record(
        settings.audit_log_path,
        {
            "caller": caller,
            "provider": provider.name,
            "model": response.model,
            "prompt": prompt.name,
            "prompt_version": prompt.version,
            "input_fingerprint": fingerprint(user_text),
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "latency_ms": t.ms,
            "masked": masked_counts,
            "structured": prompt.output_schema is not None,
        },
    )
    return response


def extract_json(text: str) -> dict:
    """Récupère l'objet JSON d'une réponse, même entouré de texte ou de ```json."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("Aucun objet JSON trouvé dans la réponse du modèle")
    return json.loads(match.group(0))
