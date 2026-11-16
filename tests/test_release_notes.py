import json

from ai_core.config import Settings
from ai_core.prompts import load_prompt
from ai_core.providers.fake_provider import FakeProvider
from ai_core.validation import find_problems
from integrations.github_client import extract_jira_keys, pr_numbers_from_commits
from scripts import release_notes as rn

PRS = [
    {"number": 12, "title": "PI-1 corrige l'erreur 500 au paiement", "branch": "PI-1-fix-paiement",
     "body": "Contact : dev@maison-lumen.example", "url": "https://github.com/x/y/pull/12", "author": "mbahnis"},
    {"number": 13, "title": "Export CSV des commandes", "branch": "feature/PI-4-export-csv",
     "body": "", "url": "https://github.com/x/y/pull/13", "author": "mbahnis"},
]

NOTES = {
    "resume": "Les paiements par carte fonctionnent de nouveau et le back-office permet d'exporter les commandes.",
    "points_forts": ["Paiement par carte rétabli"],
    "nouveautes": [{"titre": "Export CSV", "description": "Export mensuel.", "tickets": ["PI-4"], "prs": [13]}],
    "corrections": [{"titre": "Paiement", "description": "Plus d'erreur 500.", "tickets": ["PI-1", "PI-99"],
                     "prs": [12, 404]}],
    "technique": [],
    "points_attention": [],
}


class FakeJira:
    def get_issue(self, key, fields=None):
        data = {"PI-1": ("Erreur 500 au paiement", "Bug"), "PI-4": ("Exporter les commandes", "Story")}
        if key not in data:
            raise RuntimeError("404")
        return {"fields": {"summary": data[key][0], "issuetype": {"name": data[key][1]}, "status": {"name": "Terminé"}}}


def test_extraction_cles_et_numeros_de_pr():
    assert extract_jira_keys("PI-1-fix", "PI-1 corrige", "voir aussi PI-8") == ["PI-1", "PI-8"]
    messages = ["Merge pull request #12 from mbahnis/PI-1-fix\n\nfix", "Export CSV (#13)", "commit direct"]
    assert pr_numbers_from_commits(messages) == [12, 13]


def test_changements_associes_aux_tickets():
    prs, tickets = rn.collect_changes([dict(p) for p in PRS], FakeJira())
    assert prs[0]["tickets"] == ["PI-1"] and prs[1]["tickets"] == ["PI-4"]
    texte = rn.format_changes(prs, tickets)
    assert "Ticket PI-1 [Bug] : Erreur 500 au paiement" in texte and "PR #13" in texte


def test_normalisation_retire_les_references_inventees():
    prs, tickets = rn.collect_changes([dict(p) for p in PRS], FakeJira())
    notes = rn.normalize(json.loads(json.dumps(NOTES)), prs, tickets)
    assert notes["corrections"][0]["tickets"] == ["PI-1"]
    assert notes["corrections"][0]["prs"] == [12]


def test_rendus_markdown_et_confluence():
    prs, tickets = rn.collect_changes([dict(p) for p in PRS], FakeJira())
    notes = rn.normalize(json.loads(json.dumps(NOTES)), prs, tickets)
    md = rn.render_markdown(notes, "v1.1.0", "https://jira.example", "https://github.com/x/y")
    assert "### ✨ Nouveautés" in md and "[PI-4](https://jira.example/browse/PI-4)" in md
    page = rn.render_confluence(notes, "v1.1.0", prs, tickets, "https://jira.example", "https://github.com/x/y", "m")
    assert 'ac:name="info"' in page and "<h2>Tickets livrés</h2>" in page
    assert "Exporter les commandes" in page


def test_schema_release_notes_et_masquage(tmp_path):
    from ai_core import ask

    assert find_problems(NOTES, load_prompt("release_notes").output_schema) == []
    provider = FakeProvider(json.dumps(NOTES))
    prs, tickets = rn.collect_changes([dict(p) for p in PRS], FakeJira())
    ask("release_notes", {"version": "v1.1.0", "previous_version": "v1.0.0", "date": "16/11/2026",
                          "changes": rn.format_changes(prs, tickets)},
        settings=Settings(provider="fake", audit_log_path=str(tmp_path / "a.jsonl")), provider=provider)
    assert "dev@maison-lumen.example" not in provider.last_user and "[EMAIL]" in provider.last_user
