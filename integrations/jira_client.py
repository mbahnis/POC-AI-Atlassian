"""Client Jira Cloud minimal (API REST v3).

Authentification : e-mail + token API Atlassian, lus dans l'environnement :
  JIRA_BASE_URL   ex. https://mon-site.atlassian.net
  JIRA_EMAIL      compte technique ou personnel
  JIRA_API_TOKEN  créé sur id.atlassian.com > Security > API tokens
"""

import os

import requests


def adf_text(text: str) -> dict:
    """Convertit du texte simple au format ADF attendu par Jira Cloud (un paragraphe par ligne)."""
    paragraphs = []
    for line in text.split("\n"):
        content = [{"type": "text", "text": line}] if line else []
        paragraphs.append({"type": "paragraph", "content": content})
    return {"type": "doc", "version": 1, "content": paragraphs}


class JiraClient:
    def __init__(self, base_url: str | None = None, email: str | None = None, token: str | None = None):
        self.base_url = (base_url or os.environ["JIRA_BASE_URL"]).rstrip("/")
        self.session = requests.Session()
        self.session.auth = (email or os.environ["JIRA_EMAIL"], token or os.environ["JIRA_API_TOKEN"])
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def _url(self, path: str) -> str:
        return f"{self.base_url}/rest/api/3/{path.lstrip('/')}"

    def _check(self, resp: requests.Response) -> requests.Response:
        if resp.status_code >= 400:
            raise RuntimeError(f"Jira {resp.request.method} {resp.url} -> {resp.status_code} : {resp.text[:500]}")
        return resp

    def search(self, jql: str, fields: list[str] | None = None, max_results: int = 100) -> list[dict]:
        issues, token = [], None
        while True:
            body = {"jql": jql, "fields": fields or ["summary", "status"], "maxResults": max_results}
            if token:
                body["nextPageToken"] = token
            data = self._check(self.session.post(self._url("search/jql"), json=body)).json()
            issues.extend(data.get("issues", []))
            token = data.get("nextPageToken")
            if not token or data.get("isLast", True):
                return issues

    def get_issue(self, key: str, fields: list[str] | None = None) -> dict:
        params = {"fields": ",".join(fields)} if fields else None
        return self._check(self.session.get(self._url(f"issue/{key}"), params=params)).json()

    def create_issue(self, project_key: str, summary: str, description: str,
                     issue_type: str = "Task", labels: list[str] | None = None) -> str:
        body = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": adf_text(description),
                "issuetype": {"name": issue_type},
                "labels": labels or [],
            }
        }
        return self._check(self.session.post(self._url("issue"), json=body)).json()["key"]

    def add_comment(self, key: str, text: str) -> None:
        self._check(self.session.post(self._url(f"issue/{key}/comment"), json={"body": adf_text(text)}))

    def delete_issue(self, key: str) -> None:
        self._check(self.session.delete(self._url(f"issue/{key}"), params={"deleteSubtasks": "true"}))
