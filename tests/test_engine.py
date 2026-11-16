import json

import pytest

from ai_core import ask, extract_json
from ai_core.config import Settings
from ai_core.prompts import load_prompt
from ai_core.providers.fake_provider import FakeProvider


@pytest.fixture
def settings(tmp_path):
    return Settings(provider="fake", audit_log_path=str(tmp_path / "audit.jsonl"))


def test_prompt_versionne_charge():
    prompt = load_prompt("smoke_test")
    assert prompt.version == "1" and prompt.tier == "fast"
    assert "$context" in prompt.user_template


def test_variable_manquante_echoue():
    with pytest.raises(KeyError):
        load_prompt("smoke_test").render({})


def test_ask_masque_avant_envoi_et_journalise(settings):
    provider = FakeProvider('{"status": "ok"}')
    response = ask("smoke_test", {"context": "écrit par a.b@client.fr"}, settings=settings, provider=provider)

    # Le fournisseur n'a jamais reçu l'adresse e-mail
    assert "a.b@client.fr" not in provider.last_user
    assert "[EMAIL]" in provider.last_user
    assert extract_json(response.text)["status"] == "ok"

    with open(settings.audit_log_path, encoding="utf-8") as f:
        record = json.loads(f.read().strip())
    assert record["prompt"] == "smoke_test" and record["prompt_version"] == "1"
    assert record["masked"] == {"EMAIL": 1}
    assert "a.b@client.fr" not in json.dumps(record)


def test_masquage_desactivable(settings):
    settings.masking_enabled = False
    provider = FakeProvider("{}")
    ask("smoke_test", {"context": "a.b@client.fr"}, settings=settings, provider=provider)
    assert "a.b@client.fr" in provider.last_user


def test_extract_json_tolere_le_markdown():
    assert extract_json('Voici :\n```json\n{"a": 1}\n```') == {"a": 1}


class FlakyProvider(FakeProvider):
    """Renvoie une réponse corrompue, puis une réponse saine."""

    def __init__(self, bad, good):
        super().__init__(good)
        self.responses = [bad, good]
        self.calls = 0

    def complete(self, system, user, model, max_tokens, output_schema=None):
        self.canned_response = self.responses[min(self.calls, 1)]
        self.calls += 1
        return super().complete(system, user, model, max_tokens, output_schema)


def test_reponse_corrompue_relancee_une_fois(settings):
    from tests.test_triage import RESULT

    bad = json.dumps(dict(RESULT, resume="ok</resume>\n<parameter name=\"x\">"))
    provider = FlakyProvider(bad, json.dumps(RESULT))
    response = ask("triage", {k: "x" for k in
                              ["key", "issue_type", "summary", "description", "components", "labels", "candidates"]},
                   settings=settings, provider=provider)
    assert provider.calls == 2 and response.data["priorite"] == "Haute"
    with open(settings.audit_log_path, encoding="utf-8") as f:
        record = json.loads(f.read().strip())
    assert record["attempts"] == 2 and record["rejected"] == []


def test_echec_apres_deux_tentatives(settings):
    from tests.test_triage import RESULT

    bad = json.dumps(dict(RESULT, resume="ok</resume>"))
    with pytest.raises(ValueError, match="2 tentatives"):
        ask("triage", {k: "x" for k in
                       ["key", "issue_type", "summary", "description", "components", "labels", "candidates"]},
            settings=settings, provider=FlakyProvider(bad, bad))


def test_max_tokens_propre_au_prompt(settings):
    from tests.test_triage import RESULT

    class Spy(FakeProvider):
        def complete(self, system, user, model, max_tokens, output_schema=None):
            self.max_tokens = max_tokens
            return super().complete(system, user, model, max_tokens, output_schema)

    spy = Spy(json.dumps(RESULT))
    ask("triage", {k: "x" for k in ["key", "issue_type", "summary", "description", "components", "labels",
                                    "candidates"]}, settings=settings, provider=spy)
    assert spy.max_tokens == 4000
