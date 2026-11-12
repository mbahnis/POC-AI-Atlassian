"""Fournisseur Claude via l'API Anthropic."""

import os

from .base import AIResponse


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str | None = None):
        # Import ici pour que les tests n'aient pas besoin du SDK installé
        import anthropic

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY absente. En CI, la définir dans les Secrets du dépôt."
            )
        self._client = anthropic.Anthropic(api_key=key)

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> AIResponse:
        msg = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(block.text for block in msg.content if block.type == "text")
        return AIResponse(
            text=text,
            model=msg.model,
            input_tokens=msg.usage.input_tokens,
            output_tokens=msg.usage.output_tokens,
        )
