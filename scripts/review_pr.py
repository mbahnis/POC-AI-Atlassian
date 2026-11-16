"""Brique 3 : revue IA d'une pull request contre les critères d'acceptation du ticket Jira.

Question unique : le code fait-il ce que le ticket demande ? (en complément de la revue humaine)

1. Lit la PR et retrouve le ticket qu'elle traite (nom de branche ou titre)
2. Lit les critères d'acceptation dans Jira et le diff de la PR dans GitHub
3. Demande à l'IA d'évaluer chaque critère : couvert, partiel, absent, non vérifiable
4. Publie (ou met à jour) un commentaire unique dans la PR, et commente le ticket Jira
   quand le verdict change

Usage :
  python -m scripts.review_pr --pr 14              # revue + commentaires
  python -m scripts.review_pr --pr 14 --dry-run    # affiche sans rien publier

Variables : ANTHROPIC_API_KEY, GITHUB_TOKEN, GITHUB_REPOSITORY, JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN
"""

import argparse
import os
import re
import sys

from ai_core import ask, extract_json
from integrations import adf
from integrations.github_client import GitHubClient, extract_jira_keys
from integrations.jira_client import JiraClient, adf_to_text

MARKER = "<!-- poc-ia-revue-pr"
VERDICTS = {"conforme": "✅ Conforme", "partiel": "🟠 Partiellement conforme", "non_conforme": "🔴 Non conforme"}
STATUTS = {"couvert": "✅ Couvert", "partiel": "🟠 Partiel", "absent": "❌ Absent", "non_verifiable": "❔ Non vérifiable"}
PANELS = {"conforme": "success", "partiel": "warning", "non_conforme": "error"}
IGNORED_FILES = re.compile(r"(\.lock$|package-lock\.json$|\.min\.(js|css)$|^docs/)")
MAX_DIFF_CHARS = int(os.environ.get("PR_REVIEW_MAX_DIFF_CHARS", "40000"))


def write_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(markdown)


def build_diff(files: list[dict], limit: int = MAX_DIFF_CHARS) -> tuple[str, bool]:
    """Assemble le diff des fichiers utiles. Retourne le texte et un indicateur de troncature."""
    parts, size, truncated = [], 0, False
    for f in files:
        if IGNORED_FILES.search(f["filename"]):
            continue
        block = f"### {f['filename']} ({f['status']})\n{f['patch'] or '(diff non disponible : fichier binaire ou trop gros)'}\n"
        if size + len(block) > limit:
            truncated = True
            break
        parts.append(block)
        size += len(block)
    return "\n".join(parts) or "(aucun changement de code)", truncated


def format_tickets(tickets: dict[str, dict]) -> str:
    return "\n\n".join(
        f"### {key} [{t['type']}] : {t['summary']}\n{t['description'] or '(pas de description)'}"
        for key, t in tickets.items()
    )


def previous_verdict(comment: dict | None) -> str | None:
    if not comment:
        return None
    match = re.search(r"poc-ia-revue-pr verdict=(\w+)", comment.get("body") or "")
    return match.group(1) if match else None


def render_pr_comment(review: dict, tickets: dict[str, dict], jira_url: str, model: str, truncated: bool) -> str:
    links = ", ".join(f"[{k}]({jira_url}/browse/{k})" for k in tickets)
    lines = [
        f"{MARKER} verdict={review['verdict']} -->",
        "## 🤖 Revue IA : le code fait-il ce que demande le ticket ?",
        "",
        f"**Verdict : {VERDICTS[review['verdict']]}** (ticket {links})",
        "",
        review["resume"],
        "",
        "| Ticket | Critère d'acceptation | Statut | Preuve |",
        "|---|---|---|---|",
    ]
    for c in review["criteres"]:
        lines.append(f"| {c['ticket']} | {c['critere']} | {STATUTS[c['statut']]} | {c['preuve']} |")
    if review["hors_perimetre"]:
        lines += ["", "**Hors du périmètre du ticket** (à confirmer, pas forcément un problème) :"]
        lines += [f"- {h}" for h in review["hors_perimetre"]]
    lines += ["", f"**Tests :** {review['tests']}"]
    if truncated:
        lines += ["", "> ⚠️ Le diff était trop long : seule une partie a été analysée."]
    lines += ["", (f"<sub>Complément de la revue humaine, ne bloque pas la fusion. Mis à jour à chaque push. "
                   f"Généré par {model}, données personnelles masquées avant envoi.</sub>")]
    return "\n".join(lines)


def render_no_ticket_comment() -> str:
    return "\n".join([
        f"{MARKER} verdict=sans_ticket -->",
        "## 🤖 Revue IA : aucun ticket Jira associé",
        "",
        ("Aucune clé de ticket (ex. `PI-12`) n'a été trouvée dans le nom de branche ou le titre de la PR. "
         "La revue contre les critères d'acceptation n'est pas possible."),
        "",
        "Ajoutez la clé dans le titre de la PR pour lancer la revue au prochain push, et pour relier la PR au ticket.",
    ])


def jira_comment(review: dict, pr: dict) -> dict:
    manquants = [c for c in review["criteres"] if c["statut"] in ("absent", "partiel")]
    blocks = [adf.panel(PANELS[review["verdict"]], adf.paragraph(
        adf.text(f"🤖 Revue IA de la PR #{pr['number']} : {VERDICTS[review['verdict']]}. ", bold=True),
        adf.text(review["resume"]),
    ))]
    if manquants:
        blocks.append(adf.paragraph(adf.text("Points à compléter :", bold=True)))
        blocks.append(adf.bullet_list([[adf.text(f"{STATUTS[c['statut']]} : {c['critere']}")] for c in manquants]))
    blocks.append(adf.paragraph(adf.text(f"Détail dans la PR : {pr['url']}")))
    return adf.doc(*blocks)


def compute_verdict(criteres: list[dict]) -> str:
    """Verdict calculé par le code à partir des statuts (et non choisi par l'IA) : stable et explicable.

    - conforme : tous les critères vérifiables sont couverts (les "non vérifiables" ne comptent pas contre la PR)
    - non_conforme : au moins la moitié des critères vérifiables sont absents
    - partiel : les autres cas
    """
    verifiables = [c for c in criteres if c["statut"] != "non_verifiable"]
    if all(c["statut"] == "couvert" for c in verifiables):
        return "conforme"
    absents = sum(1 for c in verifiables if c["statut"] == "absent")
    return "non_conforme" if absents * 2 >= len(verifiables) else "partiel"


def normalize(review: dict, tickets: dict[str, dict]) -> dict:
    """Le code a le dernier mot : tickets inconnus rattachés au premier ticket, verdict recalculé."""
    first = next(iter(tickets))
    for c in review["criteres"]:
        if c["ticket"] not in tickets:
            c["ticket"] = first
    review["verdict"] = compute_verdict(review["criteres"])
    return review


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pr", type=int, default=int(os.environ.get("PR_NUMBER", "0")) or None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.pr:
        parser.error("--pr est obligatoire hors GitHub Actions")

    github = GitHubClient()
    pr = github.pull_request(args.pr)
    # Le ticket est celui de la branche ou du titre ; la description peut citer d'autres tickets pour contexte
    keys = extract_jira_keys(pr["branch"], pr["title"])
    existing = github.find_comment(args.pr, MARKER)

    if not keys:
        print("Aucun ticket Jira cité : pas de revue contre le ticket.")
        if not args.dry_run:
            github.upsert_comment(args.pr, MARKER, render_no_ticket_comment())
        write_summary(f"## ℹ️ PR #{args.pr} : aucun ticket Jira associé\n")
        return 0

    jira = JiraClient()
    tickets = {}
    for key in keys:
        try:
            f = jira.get_issue(key, ["summary", "description", "issuetype"])["fields"]
            tickets[key] = {"summary": f["summary"], "type": f["issuetype"]["name"],
                            "description": adf_to_text(f.get("description"))}
        except RuntimeError:
            print(f"::warning::Ticket {key} cité dans la PR introuvable dans Jira")
    if not tickets:
        print("::warning::Aucun des tickets cités n'existe dans Jira.")
        return 0

    diff, truncated = build_diff(github.pull_request_files(args.pr))
    response = ask(
        "pr_review",
        {"pr_title": pr["title"], "pr_branch": pr["branch"], "pr_body": pr["body"] or "(vide)",
         "tickets": format_tickets(tickets), "diff": diff},
        caller=f"review_pr:{args.pr}",
    )
    review = normalize(response.data if response.data is not None else extract_json(response.text), tickets)
    jira_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    body = render_pr_comment(review, tickets, jira_url, response.model, truncated)
    print(body)

    if args.dry_run:
        print("Mode --dry-run : rien n'a été publié.")
        return 0

    url = github.upsert_comment(args.pr, MARKER, body)
    # Jira n'est commenté que si le verdict change : pas de bruit à chaque push
    if previous_verdict(existing) != review["verdict"]:
        for key in tickets:
            jira.add_comment(key, jira_comment(review, pr))

    counts = {s: sum(1 for c in review["criteres"] if c["statut"] == s) for s in STATUTS}
    write_summary(
        f"## {VERDICTS[review['verdict']]} : PR #{args.pr}\n\n"
        + " · ".join(f"{STATUTS[s]} : {n}" for s, n in counts.items() if n)
        + f"\n\n[Voir le commentaire]({url})\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
