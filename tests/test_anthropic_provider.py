from types import SimpleNamespace

import anthropic

from ai_core.providers.anthropic_provider import AnthropicProvider


class FakeMessages:
    def __init__(self, text, stop_reason="end_turn"):
        self.kwargs = None
        self.text = text
        self.stop_reason = stop_reason

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            model="claude-test",
            stop_reason=self.stop_reason,
            usage=SimpleNamespace(input_tokens=10, output_tokens=5),
            content=[SimpleNamespace(type="text", text=self.text)],
        )


def make_provider(monkeypatch, fake):
    monkeypatch.setattr(anthropic, "Anthropic", lambda api_key: SimpleNamespace(messages=fake))
    return AnthropicProvider(api_key="test")


def test_sortie_structuree_native(monkeypatch):
    fake = FakeMessages('{"priorite": "Haute (bouton \\"Payer\\")"}')
    provider = make_provider(monkeypatch, fake)
    schema = {"type": "object", "properties": {"priorite": {"type": "string"}}}

    response = provider.complete("sys", "user", "m", 100, output_schema=schema)

    fmt = fake.kwargs["output_config"]["format"]
    assert fmt["type"] == "json_schema"
    assert fmt["schema"]["additionalProperties"] is False
    assert "tools" not in fake.kwargs
    # Les guillemets dans le texte ne posent pas de problème
    assert response.data == {"priorite": 'Haute (bouton "Payer")'}


def test_reponse_tronquee_signalee(monkeypatch):
    import pytest

    provider = make_provider(monkeypatch, FakeMessages('{"priorite": "Hau', stop_reason="max_tokens"))
    with pytest.raises(RuntimeError, match="tronquée.*Hau"):
        provider.complete("s", "u", "m", 10, output_schema={"type": "object"})


def test_texte_simple_sans_schema(monkeypatch):
    provider = make_provider(monkeypatch, FakeMessages("bonjour"))
    response = provider.complete("s", "u", "m", 10)
    assert response.text == "bonjour" and response.data is None
