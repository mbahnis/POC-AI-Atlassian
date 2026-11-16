"""Brique 4 (2/2) : brouillon de post-mortem rédigé par l'IA à la clôture d'un incident.

1. Lit l'incident : description, commentaires de l'équipe, historique des statuts
2. Calcule la durée (le code, pas l'IA) et récupère les déploiements récents
3. Demande à l'IA un brouillon "blameless" : résumé, impact, chronologie, cause probable
   (avec niveau de confiance), ce qui a bien ou mal fonctionné, actions correctives, questions ouvertes
4. Publie une page Confluence marquée BROUILLON et commente l'incident avec le lien

L'IA ne crée aucun ticket d'action : elle les propose, l'équipe décide lesquels ouvrir.

Usage :
  python -m scripts.postmortem PIOPS-1             # générer et publier
  python -m scripts.postmortem PIOPS-1 --dry-run   # générer sans publier

Variables : ANTHROPIC_API_KEY, JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN,
            CONFLUENCE_SPACE_KEY, CONFLUENCE_BASE_URL, CONFLUENCE_POSTMORTEM_PARENT,
            GITHUB_TOKEN + GITHUB_REPOSITORY (facultatives, pour les déploiements récents)
"""

import argparse
import html
import os
import sys
from datetime import datetime

from ai_core import ask, extract_json
from integrations import adf
from integrations.jira_client import JiraClient, adf_to_text

TYPES = {"prevention": "🛡️ Prévention", "detection": "🔎 Détection", "reponse": "🚒 Réponse"}
PRIORITES = {"haute": "Haute", "moyenne": "Moyenne", "basse": "Basse"}
CONFIANCE = {"forte": "Green", "moyenne": "Yellow", "faible": "Red"}


def write_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(markdown)


def parse_jira_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)  # format Jira : 2026-11-16T05:47:43.520-0500 (avec fuseau)
    except ValueError:
        return None


def duration_text(created: datetime | None, resolved: datetime | None) -> str:
    """Durée d'ouverture du ticket, calculée par le code (l'IA ne fait pas d'arithmétique sur des dates)."""
    if not (created and resolved):
        return "inconnue"
    minutes = int((resolved - created).total_seconds() // 60)
    hours, mins = divmod(minutes, 60)
    return f"{hours} h {mins:02d} min" if hours else f"{mins} min"


def resolution_date(fields: dict, history: list[dict]) -> str | None:
    """Date de résolution Jira, ou à défaut le dernier passage dans un statut de fin."""
    if fields.get("resolutiondate"):
        return fields["resolutiondate"]
    done = [h for h in history if (h["to"] or "").lower() in ("terminé", "done", "résolu", "resolved", "fermé")]
    return done[-1]["created"] if done else None


def recent_deployments(limit: int = 3) -> str:
    if not (os.environ.get("GITHUB_TOKEN") and os.environ.get("GITHUB_REPOSITORY")):
        return "(non disponible)"
    from integrations.github_client import GitHubClient

    try:
        releases = GitHubClient()._get("releases", per_page=limit)
    except RuntimeError:
        return "(non disponible)"
    return "\n".join(f"- {r['tag_name']} publiée le {r.get('published_at', '?')}" for r in releases) or "(aucun)"


def scrub_names(value, names: set[str]):
    """Principe blameless appliqué par le code : retire les noms des auteurs Jira qui auraient échappé à l'IA."""
    if isinstance(value, str):
        for name in names:
            value = value.replace(name, "un membre de l'équipe")
        return value
    if isinstance(value, list):
        return [scrub_names(v, names) for v in value]
    if isinstance(value, dict):
        return {k: scrub_names(v, names) for k, v in value.items()}
    return value


def render_confluence(pm: dict, key: str, jira_url: str, duration: str, model: str) -> str:
    e = html.escape

    def macro(name: str, inner: str) -> str:
        return (f'<ac:structured-macro ac:name="{name}"><ac:rich-text-body>{inner}'
                "</ac:rich-text-body></ac:structured-macro>")

    def status(title: str, colour: str) -> str:
        return (f'<ac:structured-macro ac:name="status"><ac:parameter ac:name="colour">{colour}</ac:parameter>'
                f'<ac:parameter ac:name="title">{e(title)}</ac:parameter></ac:structured-macro>')

    def ul(items: list[str]) -> str:
        return "<ul>" + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>" if items else "<p><em>(rien)</em></p>"

    cause = pm["cause_probable"]
    out = [
        (f"<p>{status('BROUILLON À RELIRE', 'Yellow')} Incident "
         f'<a href="{jira_url}/browse/{key}">{key}</a> · Durée : <strong>{e(duration)}</strong></p>'),
        macro("info", f"<p><strong>{e(pm['resume'])}</strong></p>"),
        "<h2>Impact</h2>", f"<p>{e(pm['impact'])}</p>",
        "<h2>Chronologie</h2><table><tbody><tr><th>Heure</th><th>Événement</th></tr>"
        + "".join(f"<tr><td>{e(c['heure'])}</td><td>{e(c['evenement'])}</td></tr>" for c in pm["chronologie"])
        + "</tbody></table>",
        f"<h2>Cause probable {status('confiance ' + cause['confiance'], CONFIANCE[cause['confiance']])}</h2>",
        f"<p>{e(cause['hypothese'])}</p>", "<p><strong>Éléments qui l'appuient :</strong></p>", ul(cause["elements"]),
        "<h2>Facteurs contributifs</h2>", ul(pm["facteurs_contributifs"]),
        "<h2>Ce qui a bien fonctionné</h2>", ul(pm["ce_qui_a_bien_fonctionne"]),
        "<h2>Ce qui est à améliorer</h2>", ul(pm["a_ameliorer"]),
        "<h2>Actions correctives proposées</h2>",
        "<table><tbody><tr><th>Action</th><th>Type</th><th>Priorité</th><th>Responsable proposé</th></tr>"
        + "".join(f"<tr><td>{e(a['action'])}</td><td>{TYPES[a['type']]}</td><td>{PRIORITES[a['priorite']]}</td>"
                  f"<td>{e(a['responsable'])}</td></tr>" for a in pm["actions"])
        + "</tbody></table>",
        macro("note", "<p>Ces actions sont des <strong>propositions</strong> : aucun ticket n'a été créé. "
                      "L'équipe choisit lesquelles ouvrir lors de la revue du post-mortem.</p>"),
        "<h2>Questions ouvertes (à compléter en revue)</h2>", ul(pm["questions_ouvertes"]),
        macro("warning", f"<p>Brouillon généré par IA ({e(model)}) à partir du ticket {key}, de ses commentaires et "
                         "de son historique. Principe blameless : aucune personne n'est mise en cause. "
                         "Données personnelles masquées avant envoi. À relire et corriger par l'équipe.</p>"),
    ]
    return "".join(out)


def jira_comment(pm: dict, page_url: str) -> dict:
    return adf.doc(adf.panel("info", adf.paragraph(
        adf.text("📚 Brouillon de post-mortem généré. ", bold=True),
        adf.text(f"{pm['resume']} À relire par l'équipe : {page_url}"),
    )), adf.paragraph(adf.text(
        f"{len(pm['actions'])} actions correctives proposées, {len(pm['questions_ouvertes'])} questions ouvertes."
    )))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("issue_key")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    key = args.issue_key.strip().upper()

    jira = JiraClient()
    f = jira.get_issue(key, ["summary", "description", "priority", "status", "created", "resolutiondate", "labels"])[
        "fields"]
    comments = jira.get_comments(key)
    history = jira.get_status_history(key)
    created, resolved_raw = f["created"], resolution_date(f, history)
    duration = duration_text(parse_jira_date(created), parse_jira_date(resolved_raw))

    response = ask(
        "postmortem",
        {
            "key": key, "summary": f["summary"], "priority": (f.get("priority") or {}).get("name", "?"),
            "status": f["status"]["name"], "created": created, "resolved": resolved_raw or "non résolu",
            "duration": duration, "description": adf_to_text(f.get("description")) or "(vide)",
            "comments": "\n".join(f"- [{c['created']}] {c['text']}" for c in comments) or "(aucun)",
            "status_history": "\n".join(f"- [{h['created']}] {h['from']} -> {h['to']}" for h in history) or "(aucun)",
            "deployments": recent_deployments(),
        },
        caller=f"postmortem:{key}",
    )
    pm = response.data if response.data is not None else extract_json(response.text)
    pm = scrub_names(pm, {c["author"] for c in comments} | {h["author"] for h in history})

    jira_url = os.environ["JIRA_BASE_URL"].rstrip("/")
    page = render_confluence(pm, key, jira_url, duration, response.model)
    with open("postmortem.html", "w", encoding="utf-8") as out:
        out.write(page)
    print(f"Post-mortem {key} : {pm['titre']}\n{pm['resume']}\nDurée : {duration}")

    if args.dry_run:
        print("Mode --dry-run : rien n'a été publié (page dans postmortem.html).")
        return 0

    space = os.environ.get("CONFLUENCE_SPACE_KEY")
    if not space:
        raise SystemExit("CONFLUENCE_SPACE_KEY absente : le brouillon est dans l'artefact postmortem.html")
    from integrations.confluence_client import ConfluenceClient

    page_url = ConfluenceClient().create_or_update_page(
        space, f"Post-mortem {key} : {pm['titre']}", page,
        parent_title=os.environ.get("CONFLUENCE_POSTMORTEM_PARENT") or None,
    )
    jira.add_comment(key, jira_comment(pm, page_url))
    jira.add_labels(key, ["postmortem-brouillon"])
    write_summary(f"## 📚 Post-mortem de {key} publié (brouillon)\n\n{pm['resume']}\n\n- Durée : {duration}\n"
                  f"- Actions proposées : {len(pm['actions'])}\n- Page : {page_url}\n")
    print(f"Brouillon publié : {page_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
