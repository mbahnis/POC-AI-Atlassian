from ai_core.prompts import load_prompt
from ai_core.validation import find_problems, to_strict_schema
from scripts.triage_ticket import load_config, normalize
from tests.test_triage import RESULT

SCHEMA = load_prompt("triage").output_schema


def test_reponse_saine_acceptee():
    assert find_problems(RESULT, SCHEMA) == []


def test_balisage_parasite_detecte():
    # Cas réel observé le 13/11 sur PI-2 : un champ "avalé" dans le texte du précédent
    corrompue = dict(RESULT, justification_priorite=(
        'Ampleur non confirmée.</justification_priorite>\n<parameter name="composant">Paiement'
    ), composant=None)
    problems = find_problems(corrompue, SCHEMA)
    assert any("justification_priorite" in p for p in problems)


def test_champ_manquant_detecte():
    incomplete = {k: v for k, v in RESULT.items() if k != "priorite"}
    assert find_problems(incomplete, SCHEMA)


def test_schema_strict_ferme_et_compatible():
    strict = to_strict_schema(SCHEMA)
    assert strict["additionalProperties"] is False
    assert "maximum" not in strict["properties"]["qualite_ticket"]
    assert "anyOf" in strict["properties"]["composant"]
    # le schéma d'origine n'est pas modifié
    assert SCHEMA["properties"]["questions_a_poser"]["maxItems"] == 5


def test_normalisation_regles_metier():
    config = load_config()
    brut = dict(RESULT, qualite_ticket=9, composant="Inconnu", labels=["regression", "invente"],
                questions_a_poser=[f"q{i}" for i in range(8)])
    propre = normalize(brut, config)
    assert propre["qualite_ticket"] == 5 and propre["composant"] is None
    assert propre["labels"] == ["regression"] and len(propre["questions_a_poser"]) == 5
