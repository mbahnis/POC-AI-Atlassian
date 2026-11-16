"""Client GitHub minimal : retrouver les PR fusionnées entre deux tags.

Authentification : GITHUB_TOKEN (fourni automatiquement dans GitHub Actions).
Dépôt : GITHUB_REPOSITORY (ex. mbahnis/POC-AI-Atlassian), fourni aussi par Actions.
"""

import os
import re

import requests

# "Merge pull request #12 from user/PI-3-message" (merge classique) ou "Titre (#12)" (squash merge)
PR_NUMBER = re.compile(r"Merge pull request #(\d+)|\(#(\d+)\)\s*$", re.MULTILINE)
JIRA_KEY = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")


def extract_jira_keys(*texts: str) -> list[str]:
    """Clés de tickets trouvées dans des textes (branche, titre, description), sans doublon, dans l'ordre."""
    seen: list[str] = []
    for text in texts:
        for key in JIRA_KEY.findall(text or ""):
            if key not in seen:
                seen.append(key)
    return seen


def pr_numbers_from_commits(messages: list[str]) -> list[int]:
    numbers: list[int] = []
    for message in messages:
        for merge, squash in PR_NUMBER.findall(message):
            n = int(merge or squash)
            if n not in numbers:
                numbers.append(n)
    return numbers


class GitHubClient:
    def __init__(self, repo: str | None = None, token: str | None = None):
        self.repo = repo or os.environ["GITHUB_REPOSITORY"]
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token or os.environ['GITHUB_TOKEN']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    def _get(self, path: str, **params) -> dict | list:
        resp = self.session.get(f"https://api.github.com/repos/{self.repo}/{path}", params=params or None)
        if resp.status_code >= 400:
            raise RuntimeError(f"GitHub GET {path} -> {resp.status_code} : {resp.text[:300]}")
        return resp.json()

    def tags(self) -> list[str]:
        """Tags du dépôt, du plus récent au plus ancien (ordre de l'API)."""
        return [t["name"] for t in self._get("tags", per_page=100)]

    def previous_tag(self, tag: str) -> str | None:
        tags = self.tags()
        return tags[tags.index(tag) + 1] if tag in tags and tags.index(tag) + 1 < len(tags) else None

    def commit_messages(self, base: str | None, head: str) -> list[str]:
        if base is None:
            commits = self._get("commits", sha=head, per_page=100)
        else:
            commits = self._get(f"compare/{base}...{head}")["commits"]
        return [c["commit"]["message"] for c in commits]

    def pull_request(self, number: int) -> dict:
        pr = self._get(f"pulls/{number}")
        return {"number": number, "title": pr["title"], "branch": pr["head"]["ref"], "body": pr.get("body") or "",
                "url": pr["html_url"], "author": pr["user"]["login"]}

    def pull_request_files(self, number: int) -> list[dict]:
        """Fichiers modifiés par la PR, avec leur diff (patch) quand GitHub le fournit."""
        return [{"filename": f["filename"], "status": f["status"], "patch": f.get("patch", "")}
                for f in self._get(f"pulls/{number}/files", per_page=100)]

    def find_comment(self, number: int, marker: str) -> dict | None:
        """Retrouve un commentaire de PR contenant un marqueur invisible (pour le mettre à jour au lieu d'en ajouter)."""
        for comment in self._get(f"issues/{number}/comments", per_page=100):
            if marker in (comment.get("body") or ""):
                return comment
        return None

    def upsert_comment(self, number: int, marker: str, body: str) -> str:
        url = f"https://api.github.com/repos/{self.repo}/issues"
        existing = self.find_comment(number, marker)
        if existing:
            resp = self.session.patch(f"{url}/comments/{existing['id']}", json={"body": body})
        else:
            resp = self.session.post(f"{url}/{number}/comments", json={"body": body})
        if resp.status_code >= 400:
            raise RuntimeError(f"GitHub commentaire PR #{number} -> {resp.status_code} : {resp.text[:300]}")
        return resp.json()["html_url"]

    def upsert_release(self, tag: str, name: str, body: str) -> str:
        """Crée la GitHub Release du tag (ou met à jour sa description) et renvoie son URL."""
        url = f"https://api.github.com/repos/{self.repo}/releases"
        existing = self.session.get(f"{url}/tags/{tag}")
        if existing.status_code == 200:
            resp = self.session.patch(f"{url}/{existing.json()['id']}", json={"name": name, "body": body})
        else:
            resp = self.session.post(url, json={"tag_name": tag, "name": name, "body": body})
        if resp.status_code >= 400:
            raise RuntimeError(f"GitHub release {tag} -> {resp.status_code} : {resp.text[:300]}")
        return resp.json()["html_url"]

    def merged_pull_requests(self, base: str | None, head: str) -> list[dict]:
        """PR fusionnées entre deux références : numéro, titre, branche, description, auteur."""
        prs = []
        for number in pr_numbers_from_commits(self.commit_messages(base, head)):
            pr = self._get(f"pulls/{number}")
            if pr.get("merged_at"):
                prs.append({
                    "number": number,
                    "title": pr["title"],
                    "branch": pr["head"]["ref"],
                    "body": pr.get("body") or "",
                    "url": pr["html_url"],
                    "author": pr["user"]["login"],
                })
        return prs
