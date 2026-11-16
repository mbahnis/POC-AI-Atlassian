"""Brique 2 : notes de version générées par l'IA à chaque release.

1. Retrouve les PR fusionnées depuis le tag précédent et les tickets Jira cités
   (dans le nom de branche, le titre ou la description de la PR)
2. Demande à l'IA des notes de version lisibles par les métiers
3. Publie la page dans Confluence (ou, à défaut, dans la GitHub Release)
4. Côté Jira : crée la version, la marque livrée, l'ajoute aux tickets et commente chaque ticket

Usage :
  python -m scripts.release_notes --tag v1.1.0              # tout publier
  python -m scripts.release_notes --tag v1.1.0 --dry-run    # générer sans rien publier

Variables : ANTHROPIC_API_KEY, GITHUB_TOKEN, GITHUB_REPOSITORY,
            JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY,
            CONFLUENCE_SPACE_KEY (optionnelle : sans elle, publication dans la GitHub Release)
"""

import argparse
import html
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from ai_core import ask, extract_json
from integrations import adf
from integrations.github_client import GitHubClient, extract_jira_keys
from integrations.jira_client import JiraClient

TZ = ZoneInfo(os.environ.get("TZ_NAME", "Europe/Paris"))
CATEGORIES = [("nouveautes", "✨ Nouveautés"), ("corrections", "🐛 Corrections"), ("technique", "🔧 Technique")]


def write_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(markdown)


def collect_changes(prs: list[dict], jira: JiraClient | None) -> tuple[list[dict], dict[str, dict]]:
    """Associe chaque PR à ses tickets Jira. Retourne les changements et les tickets connus."""
    tickets: dict[str, dict] = {}
    for pr in prs:
        pr["tickets"] = extract_jira_keys(pr["branch"], pr["title"], pr["body"])
        for key in pr["tickets"]:
            if key in tickets or jira is None:
                continue
            try:
                f = jira.get_issue(key, ["summary", "issuetype", "status"])["fields"]
                tickets[key] = {"summary": f["summary"], "type": f["issuetype"]["name"], "status": f["status"]["name"]}
            except RuntimeError:
                print(f"::warning::Ticket {key} cité dans la PR #{pr['number']} introuvable dans Jira")
    return prs, tickets


def format_changes(prs: list[dict], tickets: dict[str, dict], body_chars: int = 400) -> str:
    lines = []
    for pr in prs:
        lines.append(f"- PR #{pr['number']} : {pr['title']} (branche {pr['branch']})")
        for key in pr["tickets"]:
            t = tickets.get(key)
            lines.append(f"  Ticket {key}" + (f" [{t['type']}] : {t['summary']}" if t else " (non trouvé)"))
        body = " ".join(pr["body"].split())[:body_chars]
        if body:
            lines.append(f"  Description de la PR : {body}")
    return "\n".join(lines)


def normalize(notes: dict, prs: list[dict], tickets: dict[str, dict]) -> dict:
    """Le code a le dernier mot : on retire les tickets et PR que l'IA aurait cités sans qu'ils existent."""
    known_prs = {pr["number"] for pr in prs}
    known_keys = {key for pr in prs for key in pr["tickets"]}
    for category, _ in CATEGORIES:
        for item in notes.get(category, []):
            item["tickets"] = [k for k in item.get("tickets", []) if k in known_keys]
            item["prs"] = [n for n in item.get("prs", []) if n in known_prs]
    notes["points_forts"] = notes.get("points_forts", [])[:3]
    return notes


def render_markdown(notes: dict, tag: str, jira_url: str, repo_url: str) -> str:
    def refs(item):
        parts = [f"[{k}]({jira_url}/browse/{k})" for k in item["tickets"]]
        parts += [f"[#{n}]({repo_url}/pull/{n})" for n in item["prs"]]
        return f" ({', '.join(parts)})" if parts else ""

    out = [f"## Version {tag}", "", notes["resume"], ""]
    if notes["points_forts"]:
        out += ["**Points forts**", ""] + [f"- {p}" for p in notes["points_forts"]] + [""]
    for category, label in CATEGORIES:
        if notes.get(category):
            out += [f"### {label}", ""]
            out += [f"- **{i['titre']}** : {i['description']}{refs(i)}" for i in notes[category]] + [""]
    if notes["points_attention"]:
        out += ["### ⚠️ Points d'attention", ""] + [f"- {p}" for p in notes["points_attention"]] + [""]
    out.append("_Notes générées par IA à partir des PR et tickets Jira, à relire par l'équipe._")
    return "\n".join(out)


def render_confluence(notes: dict, tag: str, prs: list[dict], tickets: dict[str, dict],
                      jira_url: str, repo_url: str, model: str) -> str:
    """Page au format "storage" de Confluence (XHTML), avec encadrés natifs."""
    e = html.escape

    def macro(name: str, inner: str) -> str:
        return (f'<ac:structured-macro ac:name="{name}"><ac:rich-text-body>{inner}'
                f"</ac:rich-text-body></ac:structured-macro>")

    def refs(item):
        parts = [f'<a href="{jira_url}/browse/{k}">{k}</a>' for k in item["tickets"]]
        parts += [f'<a href="{repo_url}/pull/{n}">#{n}</a>' for n in item["prs"]]
        return f" ({', '.join(parts)})" if parts else ""

    out = [macro("info", f"<p><strong>{e(notes['resume'])}</strong></p>")]
    if notes["points_forts"]:
        out.append("<h2>Points forts</h2><ul>" + "".join(f"<li>{e(p)}</li>" for p in notes["points_forts"]) + "</ul>")
    for category, label in CATEGORIES:
        if notes.get(category):
            items = "".join(f"<li><strong>{e(i['titre'])}</strong> : {e(i['description'])}{refs(i)}</li>"
                            for i in notes[category])
            out.append(f"<h2>{e(label)}</h2><ul>{items}</ul>")
    if notes["points_attention"]:
        out.append(macro("warning", "<ul>" + "".join(f"<li>{e(p)}</li>" for p in notes["points_attention"]) + "</ul>"))

    rows = "".join(
        f'<tr><td><a href="{jira_url}/browse/{k}">{k}</a></td><td>{e(t["summary"])}</td>'
        f"<td>{e(t['type'])}</td></tr>"
        for k, t in tickets.items()
    )
    if rows:
        out.append(f"<h2>Tickets livrés</h2><table><tbody><tr><th>Ticket</th><th>Résumé</th><th>Type</th></tr>"
                   f"{rows}</tbody></table>")
    pr_list = "".join(f'<li><a href="{pr["url"]}">#{pr["number"]}</a> {e(pr["title"])}</li>' for pr in prs)
    out.append(f"<h2>Pull requests</h2><ul>{pr_list}</ul>")
    out.append(macro("note", f"<p>Page générée automatiquement par IA ({e(model)}) à la release {e(tag)}, "
                              "à partir des PR et des tickets Jira. Données personnelles masquées avant envoi. "
                              "À relire par l'équipe.</p>"))
    return "".join(out)


def jira_ticket_comment(tag: str, page_url: str) -> dict:
    return adf.doc(adf.panel("success", adf.paragraph(
        adf.text(f"🚀 Livré en production dans la version {tag}. ", bold=True),
        adf.text(f"Notes de version : {page_url}"),
    )))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tag", default=os.environ.get("GITHUB_REF_NAME"), required=False)
    parser.add_argument("--base", help="tag de départ (par défaut : le tag précédent)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.tag:
        parser.error("--tag est obligatoire hors GitHub Actions")

    github = GitHubClient()
    jira = JiraClient() if os.environ.get("JIRA_API_TOKEN") else None
    base = args.base or github.previous_tag(args.tag)
    if base is None:
        # Premier tag du dépôt : il sert de point de départ, il n'y a rien à comparer
        print(f"{args.tag} est la première version : elle sert de référence, pas de notes de version.")
        write_summary(f"## 📍 {args.tag} : version de référence\n\nLes notes seront générées à partir du tag suivant.\n")
        return 0
    prs = github.merged_pull_requests(base, args.tag)
    if not prs:
        print(f"::warning::Aucune PR fusionnée entre {base or 'le début'} et {args.tag} : pas de notes de version.")
        write_summary(f"## ⏭️ Pas de notes de version pour {args.tag}\n\nAucune PR fusionnée depuis {base}.\n")
        return 0

    prs, tickets = collect_changes(prs, jira)
    response = ask(
        "release_notes",
        {"version": args.tag, "previous_version": base or "aucune", "date": datetime.now(TZ).strftime("%d/%m/%Y"),
         "changes": format_changes(prs, tickets)},
        caller=f"release_notes:{args.tag}",
    )
    notes = normalize(response.data if response.data is not None else extract_json(response.text), prs, tickets)

    jira_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    repo_url = f"https://github.com/{github.repo}"
    markdown = render_markdown(notes, args.tag, jira_url, repo_url)
    with open("release-notes.md", "w", encoding="utf-8") as f:
        f.write(markdown)
    print(markdown)

    if args.dry_run:
        print("Mode --dry-run : rien n'a été publié.")
        return 0

    # 1. Publication : Confluence si configuré, sinon GitHub Release
    space = os.environ.get("CONFLUENCE_SPACE_KEY")
    if space:
        from integrations.confluence_client import ConfluenceClient

        page_url = ConfluenceClient().create_or_update_page(
            space, f"Release notes {args.tag}",
            render_confluence(notes, args.tag, prs, tickets, jira_url, repo_url, response.model),
            parent_title=os.environ.get("CONFLUENCE_PARENT_TITLE") or None,
        )
    else:
        page_url = github.upsert_release(args.tag, f"Version {args.tag}", markdown)

    # 2. Jira : version livrée, rattachée aux tickets, commentaire sur chaque ticket
    if jira and tickets:
        project = os.environ.get("JIRA_PROJECT_KEY", "PI")
        jira.ensure_version(project, args.tag, released=True, release_date=datetime.now(TZ).date().isoformat())
        for key in tickets:
            jira.add_fix_version(key, args.tag)
            jira.add_comment(key, jira_ticket_comment(args.tag, page_url))

    write_summary(
        f"## ✅ Notes de version {args.tag} publiées\n\n"
        f"- Publication : {page_url}\n- PR : {len(prs)}\n- Tickets Jira mis à jour : {', '.join(tickets) or 'aucun'}\n"
    )
    print(f"Notes de version publiées : {page_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
