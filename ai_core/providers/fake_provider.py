"""Faux fournisseur : réponses prévisibles, sans réseau ni coût.

Sert aux tests automatiques et à répéter une démo hors connexion.
"""

from .base import AIResponse


class FakeProvider:
    name = "fake"

    def __init__(self, canned_response: str = "OK"):
        self.canned_response = canned_response
        self.last_system: str | None = None
        self.last_user: str | None = None

    def complete(self, system: str, user: str, model: str, max_tokens: int) -> AIResponse:
        self.last_system = system
        self.last_user = user
        return AIResponse(
            text=self.canned_response,
            model=f"fake-{model}",
            input_tokens=len(user.split()),
            output_tokens=len(self.canned_response.split()),
        )
