"""Brique 1 : triage IA d'un ticket Jira.

Lit le ticket, récupère les tickets ouverts du projet pour repérer les doublons,
demande une proposition à l'IA, puis publie un commentaire structuré dans le ticket.
L'IA ne modifie aucun champ : elle propose, l'équipe valide.

Usage :
  python -m scripts.triage_ticket PI-2              # triage + commentaire
  python -m scripts.triage_ticket PI-2 --dry-run    # affiche le résultat sans écrire dans Jira
  python -m scripts.triage_ticket PI-2 --force      # retrie un ticket déjà trié

Variables : ANTHROPIC_API_KEY, JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN
"""

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

from ai_core import ask, extract_json
from integrations import adf
from integrations.jira_client import JiraClient, adf_to_text

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config" / "triage.yaml"

PRIORITY_ICONS = {"Critique": "🔴", "Haute": "🟠", "Moyenne": "🟡", "Basse": "🟢"}
CONFIDENCE_ORDER = {"forte": 0, "moyenne": 1, "faible": 2}


def write_summary(markdown: str) -> None:
    """Écrit dans le résumé de l'exécution GitHub Actions (visible sur la page du run). Sans effet en local."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(markdown)


def load_config() -> dict:
    return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))


def format_candidates(issues: list[dict], exclude_key: str, limit: int) -> str:
    lines = [
        f"- {i['key']} : {i['fields']['summary']}"
        for i in issues
        if i["key"] != exclude_key
    ][:limit]
    return "\n".join(lines) or "(aucun)"


def build_comment(result: dict, model: str) -> dict:
    """Transforme la réponse JSON de l'IA en commentaire Jira mis en forme."""
    blocks = [
        adf.panel(
            "info",
            adf.paragraph(
                adf.text("🤖 Proposition de triage IA, à valider par l'équipe. ", bold=True),
                adf.text(f"Qualité estimée du ticket : {result.get('qualite_ticket', '?')}/5"),
            ),
        ),
        adf.heading("Reformulation"),
        adf.paragraph(adf.text(result.get("titre_reformule", ""), bold=True)),
        adf.paragraph(adf.text(result.get("resume", ""))),
    ]

    priority = result.get("priorite", "?")
    classification = [
        [adf.text("Priorité : ", bold=True),
         adf.text(f"{PRIORITY_ICONS.get(priority, '')} {priority} ({result.get('justification_priorite', '')})")],
        [adf.text("Composant : ", bold=True), adf.text(result.get("composant") or "à déterminer")],
        [adf.text("Labels : ", bold=True), adf.text(", ".join(result.get("labels") or []) or "aucun")],
    ]
    blocks += [adf.heading("Classement proposé"), adf.bullet_list(classification)]

    duplicates = sorted(result.get("doublons") or [], key=lambda d: CONFIDENCE_ORDER.get(d.get("confiance"), 3))
    if duplicates:
        items = [
            [adf.text(f"{d['cle']} ", bold=True), adf.text(f"(confiance {d.get('confiance', '?')}) : {d.get('raison', '')}")]
            for d in duplicates
        ]
        blocks += [adf.heading("Doublons possibles"), adf.bullet_list(items)]

    if result.get("criteres_acceptation"):
        blocks += [
            adf.heading("Critères d'acceptation proposés"),
            adf.bullet_list([[adf.text(c)] for c in result["criteres_acceptation"]]),
        ]

    if result.get("questions_a_poser"):
        blocks += [
            adf.heading("Questions à poser à l'auteur"),
            adf.bullet_list([[adf.text(q)] for q in result["questions_a_poser"]]),
        ]

    blocks.append(adf.paragraph(adf.text(f"Généré par {model}. Données personnelles masquées avant envoi.")))
    return adf.doc(*blocks)


def triage(key: str, dry_run: bool = False, force: bool = False, jira: JiraClient | None = None) -> dict | None:
    config = load_config()
    jira = jira or JiraClient()
    issue = jira.get_issue(key, ["summary", "description", "issuetype", "labels", "project"])
    fields = issue["fields"]

    if config["triaged_label"] in fields.get("labels", []) and not force:
        message = (
            f"{key} a déjà été trié (label {config['triaged_label']}) : aucun appel à l'IA, aucun commentaire. "
            "Relancer avec l'option 'Retrier' cochée pour forcer."
        )
        print(f"::warning title=Ticket déjà trié::{message}")
        write_summary(f"## ⏭️ Triage ignoré\n\n{message}\n")
        return None

    project = fields["project"]["key"]
    candidates = jira.search(
        f"project = {project} AND statusCategory != Done ORDER BY created DESC",
        max_results=config["max_candidates"] + 1,
    )

    response = ask(
        "triage",
        {
            "key": key,
            "issue_type": fields["issuetype"]["name"],
            "summary": fields["summary"],
            "description": adf_to_text(fields.get("description")) or "(vide)",
            "components": ", ".join(config["components"]),
            "labels": ", ".join(config["labels"]),
            "candidates": format_candidates(candidates, key, config["max_candidates"]),
        },
        caller=f"triage:{key}",
    )
    # Réponse structurée garantie par l'API ; extract_json reste en secours pour un fournisseur sans ce mécanisme
    result = response.data if response.data is not None else extract_json(response.text)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if dry_run:
        print("Mode --dry-run : aucun commentaire publié.")
        return result

    jira.add_comment(key, build_comment(result, response.model))
    jira.add_labels(key, [config["triaged_label"]])
    print(f"Commentaire de triage publié sur {key}.")
    doublons = ", ".join(f"{d['cle']} ({d['confiance']})" for d in result.get("doublons") or []) or "aucun"
    write_summary(
        f"## ✅ Triage publié sur {key}\n\n"
        f"| Qualité | Priorité | Composant | Doublons |\n|---|---|---|---|\n"
        f"| {result.get('qualite_ticket')}/5 | {result.get('priorite')} | {result.get('composant') or '-'} | {doublons} |\n"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("issue_key")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    triage(args.issue_key.strip().upper(), dry_run=args.dry_run, force=args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
