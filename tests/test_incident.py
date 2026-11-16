import json
from datetime import datetime
from pathlib import Path

import yaml

from ai_core.prompts import load_prompt
from ai_core.validation import find_problems
from scripts import incident_open as io
from scripts import postmortem as pm

ROOT = Path(__file__).resolve().parent.parent
ALERT = json.loads((ROOT / "demo/alerts/memoire-saturee.json").read_text(encoding="utf-8"))

POSTMORTEM = {
    "titre": "Saturation mémoire de api-commandes",
    "resume": "Les pods ont redémarré en boucle pendant 20 minutes. Léa a augmenté la mémoire.",
    "impact": "Une partie des paiements a échoué.",
    "chronologie": [{"heure": "02:03", "evenement": "Alerte prise en compte par l'astreinte"}],
    "cause_probable": {"hypothese": "Export CSV sans pagination", "confiance": "forte",
                       "elements": ["Hausse de la mémoire depuis v1.1.0"]},
    "facteurs_contributifs": ["Limite mémoire basse"],
    "ce_qui_a_bien_fonctionne": ["Alerte rapide"],
    "a_ameliorer": ["Pas de test de charge sur l'export"],
    "actions": [{"action": "Paginer l'export", "type": "prevention", "priorite": "haute",
                 "responsable": "Équipe de développement"}],
    "questions_ouvertes": ["Combien de commandes ont échoué ?"],
}


class FakeJira:
    def __init__(self, existing=None):
        self.existing = existing or []
        self.created, self.comments = [], []

    def search(self, jql, fields=None, max_results=100):
        self.last_jql = jql
        return self.existing

    def create_issue(self, project, summary, description, issue_type="Task", labels=None, priority=None):
        self.created.append({"project": project, "summary": summary, "labels": labels, "priority": priority,
                             "type": issue_type, "description": description})
        return "PIOPS-1"

    def add_comment(self, key, body):
        self.comments.append((key, body))


def test_lecture_alerte_alertmanager():
    alert = io.parse_alert(ALERT)
    assert alert["name"] == "MemoireSaturee" and alert["service"] == "api-commandes"
    assert alert["severity"] == "critical" and alert["fingerprint"] == "a3f9c2e1b7d0"


def test_creation_incident(monkeypatch):
    monkeypatch.setattr(io, "last_deployment", lambda: {"name": "v1.1.0", "date": "2026-11-16T10:47:00Z",
                                                         "url": "https://github.com/x/y/releases/v1.1.0"})
    jira = FakeJira()
    key, created = io.open_or_update(io.parse_alert(ALERT), jira, "PIOPS", "Bug")
    assert (key, created) == ("PIOPS-1", True)
    issue = jira.created[0]
    assert issue["priority"] == "Critique" and "incident" in issue["labels"]
    assert "alerte-a3f9c2e1b7d0" in issue["labels"]
    assert "v1.1.0" in json.dumps(issue["description"], ensure_ascii=False)


def test_alerte_repetee_commente_l_incident_ouvert():
    jira = FakeJira(existing=[{"key": "PIOPS-1"}])
    key, created = io.open_or_update(io.parse_alert(ALERT), jira, "PIOPS", "Bug")
    assert (key, created) == ("PIOPS-1", False) and jira.created == [] and len(jira.comments) == 1
    assert "statusCategory != Done" in jira.last_jql


def test_chronologie_de_demo_lisible():
    lines = yaml.safe_load((ROOT / "demo/alerts/memoire-saturee.chronologie.yaml").read_text(encoding="utf-8"))
    assert len(lines) >= 4 and all(line[:2].isdigit() for line in lines)


def test_duree_calculee_par_le_code():
    created = pm.parse_jira_date("2026-11-16T02:00:00.000+0100")
    resolved = pm.parse_jira_date("2026-11-16T04:05:00.000+0100")
    assert pm.duration_text(created, resolved) == "2 h 05 min"
    assert pm.duration_text(created, None) == "inconnue"
    assert isinstance(created, datetime)


def test_date_de_resolution_depuis_l_historique():
    history = [{"created": "2026-11-16T03:00:00.000+0100", "to": "En cours"},
               {"created": "2026-11-16T04:00:00.000+0100", "to": "Terminé"}]
    assert pm.resolution_date({"resolutiondate": None}, history) == "2026-11-16T04:00:00.000+0100"


def test_schema_et_principe_blameless():
    assert find_problems(POSTMORTEM, load_prompt("postmortem").output_schema) == []
    nettoye = pm.scrub_names(POSTMORTEM, {"Léa"})
    assert "Léa" not in json.dumps(nettoye, ensure_ascii=False)


def test_page_confluence():
    page = pm.render_confluence(POSTMORTEM, "PIOPS-1", "https://jira.example", "2 h 05 min", "claude-sonnet")
    assert "BROUILLON À RELIRE" in page and "2 h 05 min" in page
    assert "<th>Responsable proposé</th>" in page and "aucun ticket n'a été créé" in page
    assert 'href="https://jira.example/browse/PIOPS-1"' in page
