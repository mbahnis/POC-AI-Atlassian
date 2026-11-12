from types import SimpleNamespace

import anthropic

from ai_core.providers.anthropic_provider import STRUCTURED_TOOL, AnthropicProvider


class FakeMessages:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            model="claude-test",
            stop_reason="tool_use",
            usage=SimpleNamespace(input_tokens=10, output_tokens=5),
            content=[SimpleNamespace(type="tool_use", name=STRUCTURED_TOOL,
                                     input={"priorite": 'Haute (bouton "Payer")'})],
        )


def test_sortie_structuree_force_l_outil(monkeypatch):
    fake = FakeMessages()
    monkeypatch.setattr(anthropic, "Anthropic", lambda api_key: SimpleNamespace(messages=fake))
    provider = AnthropicProvider(api_key="test")
    schema = {"type": "object", "properties": {"priorite": {"type": "string"}}}

    response = provider.complete("sys", "user", "m", 100, output_schema=schema)

    assert fake.kwargs["tool_choice"] == {"type": "tool", "name": STRUCTURED_TOOL}
    assert fake.kwargs["tools"][0]["input_schema"] == schema
    # Les guillemets dans le texte ne posent plus de problème
    assert response.data == {"priorite": 'Haute (bouton "Payer")'}
