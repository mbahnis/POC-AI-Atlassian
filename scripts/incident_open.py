"""Brique 4 (1/2) : une alerte de supervision devient un incident Jira.

Entrée : une alerte au format webhook d'Alertmanager (Prometheus). Les autres outils
(CloudWatch, Datadog, Grafana) envoient un format proche : seul `parse_alert` est à adapter.

- Alerte "firing" : crée l'incident (ou commente l'incident déjà ouvert pour la même alerte)
- Alerte "resolved" : commente l'incident. On ne le ferme pas : c'est l'équipe qui décide.
- Le dernier déploiement (GitHub Release) est ajouté au contexte : c'est souvent la première piste.

Usage :
  python -m scripts.incident_open demo/alerts/memoire-saturee.json
  python -m scripts.incident_open demo/alerts/memoire-saturee.json --timeline demo/alerts/memoire-saturee.chronologie.yaml

Variables : JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, GITHUB_TOKEN, GITHUB_REPOSITORY (facultatives pour le contexte),
            INCIDENT_PROJECT_KEY (défaut PIOPS), INCIDENT_ISSUE_TYPE (défaut Bug)
"""

import argparse
import json
import os
import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from integrations import adf
from integrations.jira_client import JiraClient

TZ = ZoneInfo(os.environ.get("TZ_NAME", "Europe/Paris"))
DEMO_ALERT_AGE = timedelta(minutes=45)

# Correspondance gravité de l'alerte -> priorité Jira (noms de l'instance, ici en français)
PRIORITIES = {"critical": "Critique", "high": "Haute", "warning": "Moyenne", "info": "Basse"}


def write_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(markdown)


def parse_alert(payload: dict) -> dict:
    """Normalise une alerte Alertmanager : c'est le seul endroit à adapter pour un autre outil de supervision."""
    first = (payload.get("alerts") or [{}])[0]
    labels = {**payload.get("commonLabels", {}), **first.get("labels", {})}
    annotations = {**payload.get("commonAnnotations", {}), **first.get("annotations", {})}
    return {
        "status": payload.get("status", first.get("status", "firing")),
        "name": labels.get("alertname", "Alerte"),
        "service": labels.get("service", "inconnu"),
        "severity": labels.get("severity", "warning"),
        "env": labels.get("env", ""),
        "instance": labels.get("instance", ""),
        "summary": annotations.get("summary", labels.get("alertname", "Alerte")),
        "description": annotations.get("description", ""),
        "runbook": annotations.get("runbook_url", ""),
        "starts_at": first.get("startsAt", ""),
        "fingerprint": (first.get("fingerprint") or labels.get("alertname", "alerte"))[:12].lower(),
        "source": payload.get("externalURL", ""),
    }


def demo_start(payload: dict, now: datetime | None = None) -> dict:
    """Démo : l'alerte démarre 45 minutes avant le lancement, pour des dates cohérentes quel que soit le jour."""
    start = ((now or datetime.now(UTC)) - DEMO_ALERT_AGE).strftime("%Y-%m-%dT%H:%M:%SZ")
    for alert in payload.get("alerts", []):
        alert["startsAt"] = start
    return payload


def render_timeline(entries: list[dict], starts_at: str) -> list[str]:
    """Démo : remplace {heure:N} par l'heure locale du début de l'alerte + N minutes."""
    start = datetime.fromisoformat(starts_at).astimezone(TZ)

    def heure(match: re.Match) -> str:
        return (start + timedelta(minutes=int(match.group(1)))).strftime("%H:%M")

    return [re.sub(r"\{heure:(-?\d+)\}", heure, e["texte"]) for e in sorted(entries, key=lambda e: e["apres"])]


def last_deployment() -> dict | None:
    """Dernière release GitHub (nom, date, lien) : contexte précieux pour l'équipe d'astreinte."""
    if not (os.environ.get("GITHUB_TOKEN") and os.environ.get("GITHUB_REPOSITORY")):
        return None
    from integrations.github_client import GitHubClient

    try:
        releases = GitHubClient()._get("releases", per_page=1)
    except RuntimeError:
        return None
    if not releases:
        return None
    r = releases[0]
    return {"name": r["tag_name"], "date": r.get("published_at", ""), "url": r["html_url"]}


def incident_description(alert: dict, deployment: dict | None) -> dict:
    rows = [
        [adf.text("Service : ", bold=True), adf.text(f"{alert['service']} ({alert['env'] or 'env. inconnu'})")],
        [adf.text("Gravité : ", bold=True), adf.text(alert["severity"])],
        [adf.text("Début de l'alerte : ", bold=True), adf.text(alert["starts_at"] or "inconnu")],
    ]
    if alert["instance"]:
        rows.append([adf.text("Instance : ", bold=True), adf.text(alert["instance"])])
    if alert["runbook"]:
        rows.append([adf.text("Procédure (runbook) : ", bold=True), adf.text(alert["runbook"])])
    blocks = [
        adf.panel("error", adf.paragraph(adf.text(f"🚨 {alert['summary']}", bold=True))),
        adf.paragraph(adf.text(alert["description"] or "Pas de description fournie par l'alerte.")),
        adf.heading("Contexte"),
        adf.bullet_list(rows),
    ]
    if deployment:
        blocks.append(adf.panel("note", adf.paragraph(
            adf.text("Dernier déploiement : ", bold=True),
            adf.text(f"{deployment['name']} le {deployment['date'][:16].replace('T', ' ')} UTC ({deployment['url']})"),
        )))
    blocks.append(adf.paragraph(adf.text(
        f"Incident créé automatiquement depuis l'alerte {alert['name']} (empreinte {alert['fingerprint']}). "
        "Commentez ici chaque action : la chronologie servira au post-mortem."
    )))
    return adf.doc(*blocks)


def open_or_update(alert: dict, jira: JiraClient, project: str, issue_type: str) -> tuple[str, bool]:
    """Retourne (clé de l'incident, créé ?). Une alerte qui se répète commente l'incident déjà ouvert."""
    alert_label = f"alerte-{alert['fingerprint']}"
    existing = jira.search(
        f'project = {project} AND labels = "{alert_label}" AND statusCategory != Done ORDER BY created DESC',
        max_results=1,
    )
    if existing:
        key = existing[0]["key"]
        state = "résolue côté supervision" if alert["status"] == "resolved" else "toujours active"
        jira.add_comment(key, adf.doc(adf.panel(
            "success" if alert["status"] == "resolved" else "warning",
            adf.paragraph(adf.text(f"Alerte {alert['name']} {state}. ", bold=True),
                          adf.text("La clôture de l'incident reste une décision de l'équipe.")),
        )))
        return key, False
    if alert["status"] == "resolved":
        raise SystemExit("Alerte résolue sans incident ouvert correspondant : rien à faire.")
    key = jira.create_issue(
        project,
        f"[Incident] {alert['summary']}",
        incident_description(alert, last_deployment()),
        issue_type=issue_type,
        labels=["incident", alert_label, f"service-{alert['service']}"],
        priority=PRIORITIES.get(alert["severity"]),
    )
    return key, True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("alert_file", help="fichier JSON de l'alerte (format webhook Alertmanager)")
    parser.add_argument("--timeline", help="démo : fichier YAML de commentaires simulant la réponse de l'équipe")
    parser.add_argument("--demo", action="store_true", help="démo : l'alerte démarre 45 minutes avant maintenant")
    args = parser.parse_args()

    payload = json.loads(Path(args.alert_file).read_text(encoding="utf-8"))
    if args.demo:
        payload = demo_start(payload)
    alert = parse_alert(payload)
    jira = JiraClient()
    project = os.environ.get("INCIDENT_PROJECT_KEY") or "PIOPS"
    issue_type = os.environ.get("INCIDENT_ISSUE_TYPE") or "Bug"
    key, created = open_or_update(alert, jira, project, issue_type)

    if args.timeline:
        entries = yaml.safe_load(Path(args.timeline).read_text(encoding="utf-8"))
        for line in render_timeline(entries, alert["starts_at"]):
            jira.add_comment(key, line)

    url = f"{os.environ['JIRA_BASE_URL'].rstrip('/')}/browse/{key}"
    action = "créé" if created else "mis à jour"
    print(f"Incident {key} {action} : {url}")
    write_summary(f"## 🚨 Incident {key} {action}\n\n{alert['summary']}\n\n{url}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
