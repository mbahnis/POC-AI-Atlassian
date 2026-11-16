import json

from ai_core.prompts import load_prompt
from ai_core.validation import find_problems
from scripts import review_pr as rp

REVIEW = {
    "resume": "Le message d'erreur est affiché en français, la version anglaise manque.",
    "criteres": [
        {"ticket": "PI-3", "critere": "Message en français et en anglais", "statut": "partiel",
         "preuve": "app/messages.py : seul le français est présent"},
        {"ticket": "PI-99", "critere": "Code bancaire jamais affiché", "statut": "couvert",
         "preuve": "app/messages.py : le code n'est pas repris"},
    ],
    "hors_perimetre": [],
    "tests": "Les tests couvrent le français uniquement.",
}
TICKETS = {"PI-3": {"summary": "Message d'erreur FR/EN", "type": "Story", "description": "Critères..."}}


def test_schema_et_normalisation():
    assert find_problems(REVIEW, load_prompt("pr_review").output_schema) == []
    review = rp.normalize(json.loads(json.dumps(REVIEW)), TICKETS)
    assert review["criteres"][1]["ticket"] == "PI-3"
    assert review["verdict"] == "partiel"


def test_verdict_calcule_par_le_code():
    def crit(*statuts):
        return [{"statut": s} for s in statuts]

    assert rp.compute_verdict(crit("couvert", "non_verifiable", "couvert")) == "conforme"
    assert rp.compute_verdict(crit("couvert", "partiel", "non_verifiable")) == "partiel"
    assert rp.compute_verdict(crit("absent", "couvert", "non_verifiable")) == "non_conforme"
    assert rp.compute_verdict(crit("non_verifiable")) == "conforme"


def test_temperature_zero_pour_la_revue():
    assert load_prompt("pr_review").temperature == 0


def test_diff_filtre_et_tronque():
    files = [{"filename": "app/messages.py", "status": "added", "patch": "+x" * 10},
             {"filename": "package-lock.json", "status": "modified", "patch": "+y"},
             {"filename": "docs/guide.md", "status": "modified", "patch": "+z"},
             {"filename": "app/gros.py", "status": "added", "patch": "+" * 500}]
    diff, truncated = rp.build_diff(files, limit=200)
    assert "app/messages.py" in diff and "package-lock" not in diff and "docs/guide" not in diff
    assert truncated is True


def test_commentaire_pr_et_verdict_precedent():
    body = rp.render_pr_comment(dict(REVIEW, verdict="partiel"), TICKETS, "https://jira.example", "claude-sonnet", truncated=False)
    assert body.startswith("<!-- poc-ia-revue-pr verdict=partiel -->")
    assert "🟠 Partiel" in body and "[PI-3](https://jira.example/browse/PI-3)" in body
    assert rp.previous_verdict({"body": body}) == "partiel"
    assert rp.previous_verdict(None) is None


def test_commentaire_sans_ticket():
    body = rp.render_no_ticket_comment()
    assert "verdict=sans_ticket" in body and "PI-12" in body


def test_commentaire_jira_liste_les_manques():
    comment = json.dumps(rp.jira_comment(dict(REVIEW, verdict="partiel"), {"number": 14, "url": "https://github.com/x/y/pull/14"}),
                         ensure_ascii=False)
    assert "Points à compléter" in comment and "Message en français et en anglais" in comment
    assert '"panelType": "warning"' in comment
