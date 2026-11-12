"""Configuration, entièrement pilotée par variables d'environnement.

Aucune valeur sensible ici : les clés restent dans les Secrets de la CI.
"""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    provider: str = field(default_factory=lambda: os.environ.get("AI_PROVIDER", "anthropic"))
    # "fast" : tâches simples et fréquentes (triage, résumé). "smart" : raisonnement (revue de PR, post-mortem).
    model_fast: str = field(default_factory=lambda: os.environ.get("AI_MODEL_FAST", "claude-haiku-5-5"))
    model_smart: str = field(default_factory=lambda: os.environ.get("AI_MODEL_SMART", "claude-sonnet-5-5"))
    max_tokens: int = field(default_factory=lambda: int(os.environ.get("AI_MAX_TOKENS", "1500")))
    masking_enabled: bool = field(
        default_factory=lambda: os.environ.get("AI_MASKING", "on").lower() not in ("off", "false", "0")
    )
    audit_log_path: str = field(default_factory=lambda: os.environ.get("AI_AUDIT_LOG", "ai-audit.jsonl"))

    def model_for(self, tier: str) -> str:
        if tier == "fast":
            return self.model_fast
        if tier == "smart":
            return self.model_smart
        raise ValueError(f"Niveau de modèle inconnu : {tier} (attendu : fast ou smart)")
