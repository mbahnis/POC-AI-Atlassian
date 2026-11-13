import json

from ai_core.config import Settings
from ai_core.providers.fake_provider import FakeProvider
from integrations.jira_client import adf_to_text
from scripts import triage_ticket

RESULT = {
    "qualite_ticket": 1,
    "titre_reformule": "Echec du paiement par carte à la validation du panier",
    "resume": "Des clients ne parviennent pas à payer.",
    "priorite": "Haute",
    "justification_priorite": "Impact direct sur le chiffre d'affaires",
    "composant": "Paiement",
    "labels": ["regression"],
    "doublons": [
        {"cle": "PI-8", "confiance": "faible", "raison": "Sujet voisin"},
        {"cle": "PI-1", "confiance": "forte", "raison": "Même erreur au paiement"},
    ],
    "criteres_acceptation": ["Le paiement par carte aboutit"],
    "questions_a_poser": ["Quel moyen de paiement ?"],
}


class FakeJira:
    def __init__(self, labels=None):
        self.comments, self.added_labels = [], []
        self.labels = labels or []

    def get_issue(self, key, fields=None):
        return {"fields": {
            "summary": "ça marche pas le paiement",
            "description": {"type": "doc", "version": 1, "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "voir avec sophie@client.fr"}]}]},
            "issuetype": {"name": "Bug"},
            "labels": self.labels,
            "project": {"key": "PI"},
        }}

    def search(self, jql, fields=None, max_results=100):
        return [{"key": "PI-1", "fields": {"summary": "Erreur 500 au paiement"}},
                {"key": "PI-2", "fields": {"summary": "ça marche pas le paiement"}}]

    def add_comment(self, key, body):
        self.comments.append((key, body))

    def add_labels(self, key, labels):
        self.added_labels += labels


def run_triage(monkeypatch, tmp_path, jira, **kwargs):
    provider = FakeProvider(json.dumps(RESULT))
    settings = Settings(provider="fake", audit_log_path=str(tmp_path / "audit.jsonl"))

    def fake_ask(name, variables, caller):
        from ai_core.engine import ask
        return ask(name, variables, settings=settings, provider=provider, caller=caller)

    monkeypatch.setattr(triage_ticket, "ask", fake_ask)
    return triage_ticket.triage("PI-2", jira=jira, **kwargs), provider


def test_triage_publie_commentaire_et_label(monkeypatch, tmp_path):
    jira = FakeJira()
    result, provider = run_triage(monkeypatch, tmp_path, jira)
    assert result["priorite"] == "Haute"
    assert jira.added_labels == ["ia-triage"]
    # Le ticket lui-même n'est pas proposé comme doublon de lui-même
    assert "PI-1 : Erreur 500" in provider.last_user and "- PI-2" not in provider.last_user
    # Masquage appliqué à la description
    assert "sophie@client.fr" not in provider.last_user


def test_dry_run_ne_publie_rien(monkeypatch, tmp_path):
    jira = FakeJira()
    run_triage(monkeypatch, tmp_path, jira, dry_run=True)
    assert jira.comments == [] and jira.added_labels == []


def test_ticket_deja_trie_ignore(monkeypatch, tmp_path):
    jira = FakeJira(labels=["ia-triage"])
    result, _ = run_triage(monkeypatch, tmp_path, jira)
    assert result is None and jira.comments == []


def test_commentaire_doublons_tries_par_confiance():
    comment = triage_ticket.build_comment(RESULT, "claude-haiku-5-5")
    texte = json.dumps(comment, ensure_ascii=False)
    assert texte.index("PI-1") < texte.index("PI-8")
    assert "à valider" in texte


def test_adf_vers_texte():
    node = {"type": "doc", "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "ligne 1"}]},
        {"type": "bulletList", "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "a"}]}]}]},
    ]}
    assert adf_to_text(node) == "ligne 1\n- a"


def test_schema_de_sortie_transmis_au_fournisseur(monkeypatch, tmp_path):
    _, provider = run_triage(monkeypatch, tmp_path, FakeJira(), dry_run=True)
    assert provider.last_schema is not None
    assert "priorite" in provider.last_schema["required"]


def test_schema_valide_la_reponse_type():
    import jsonschema

    from ai_core.prompts import load_prompt

    jsonschema.validate(RESULT, load_prompt("triage").output_schema)


def test_ticket_deja_trie_visible_dans_le_resume(monkeypatch, tmp_path):
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    run_triage(monkeypatch, tmp_path, FakeJira(labels=["ia-triage"]))
    assert "Triage ignoré" in summary.read_text(encoding="utf-8")


def test_resume_apres_triage(monkeypatch, tmp_path):
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    run_triage(monkeypatch, tmp_path, FakeJira())
    texte = summary.read_text(encoding="utf-8")
    assert "Triage publié sur PI-2" in texte and "PI-1 (forte)" in texte
