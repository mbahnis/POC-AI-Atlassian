"""Remet le projet Jira de démo dans un état propre et identique à chaque fois.

1. Supprime les tickets portant le label de démo (et seulement eux)
2. Recrée les tickets décrits dans demo/seed_tickets.yaml

Par défaut, le script affiche seulement ce qu'il ferait (aucune modification).
Ajouter --apply pour exécuter réellement.

Usage :
  python -m scripts.demo_reset            # simulation
  python -m scripts.demo_reset --apply    # exécution

Variables : JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY (défaut : PI)
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

from integrations.jira_client import JiraClient

SEED_FILE = Path(__file__).resolve().parent.parent / "demo" / "seed_tickets.yaml"


# Les noms de types dépendent de la langue de l'instance Jira (ex. "Task" ou "Tâche")
TYPE_ALIASES = {
    "Task": ["Task", "Tâche"],
    "Story": ["Story", "Récit"],
    "Bug": ["Bug", "Bogue"],
}


def available_issue_types(jira: JiraClient, project_key: str) -> list[str]:
    resp = jira.session.get(jira._url(f"issue/createmeta/{project_key}/issuetypes"))
    jira._check(resp)
    data = resp.json()
    types = data.get("issueTypes") or data.get("values") or []
    return [t["name"] for t in types if not t.get("subtask")]


def resolve_type(wanted: str, available: list[str]) -> str:
    """Trouve le nom local du type voulu, sinon une tâche, sinon le premier type disponible."""
    for candidate in TYPE_ALIASES.get(wanted, [wanted]) + TYPE_ALIASES["Task"]:
        if candidate in available:
            return candidate
    return available[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="exécuter réellement (sinon simulation)")
    args = parser.parse_args()

    project = os.environ.get("JIRA_PROJECT_KEY", "PI")
    seed = yaml.safe_load(SEED_FILE.read_text(encoding="utf-8"))
    label = seed["label"]
    jira = JiraClient()

    existing = jira.search(f'project = {project} AND labels = "{label}" ORDER BY key ASC')
    types = available_issue_types(jira, project)
    mode = "EXECUTION" if args.apply else "SIMULATION (ajouter --apply pour exécuter)"
    print(f"Mode : {mode}")
    print(f"Projet {project} : {len(existing)} ticket(s) de démo à supprimer, {len(seed['tickets'])} à créer")

    for issue in existing:
        print(f"  - suppression {issue['key']} : {issue['fields']['summary']}")
        if args.apply:
            jira.delete_issue(issue["key"])

    for t in seed["tickets"]:
        issue_type = resolve_type(t["type"], types)
        if args.apply:
            key = jira.create_issue(project, t["summary"], t["description"].strip(), issue_type, [label])
            print(f"  + {key} [{issue_type}] {t['summary']}")
        else:
            print(f"  + (à créer) [{issue_type}] {t['summary']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
