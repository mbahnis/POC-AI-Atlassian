"""Faux fournisseur : réponses prévisibles, sans réseau ni coût.

Sert aux tests automatiques et à répéter une démo hors connexion.
"""

import json

from .base import AIResponse


class FakeProvider:
    name = "fake"

    def __init__(self, canned_response: str = "OK"):
        self.canned_response = canned_response
        self.last_system: str | None = None
        self.last_user: str | None = None
        self.last_schema: dict | None = None

    def complete(
        self, system: str, user: str, model: str, max_tokens: int, output_schema: dict | None = None
    ) -> AIResponse:
        self.last_system = system
        self.last_user = user
        self.last_schema = output_schema
        return AIResponse(
            text=self.canned_response,
            model=f"fake-{model}",
            input_tokens=len(user.split()),
            output_tokens=len(self.canned_response.split()),
            data=json.loads(self.canned_response) if output_schema else None,
        )
