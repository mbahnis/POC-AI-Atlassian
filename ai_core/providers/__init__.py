from .base import AIProvider, AIResponse


def get_provider(name: str) -> AIProvider:
    """Retourne le fournisseur demandé (variable AI_PROVIDER)."""
    if name == "anthropic":
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    if name == "fake":
        from .fake_provider import FakeProvider

        return FakeProvider()
    raise ValueError(f"Fournisseur IA inconnu : {name}")


__all__ = ["AIProvider", "AIResponse", "get_provider"]
