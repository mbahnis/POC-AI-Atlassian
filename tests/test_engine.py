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
