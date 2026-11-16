"""Client Confluence Cloud minimal (API REST v2).

Mêmes identifiants que Jira (même site Atlassian) :
  JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN
Espace cible : CONFLUENCE_SPACE_KEY (ex. POCIA), page parente optionnelle : CONFLUENCE_PARENT_TITLE
"""

import os

import requests


class ConfluenceClient:
    def __init__(self, base_url: str | None = None, email: str | None = None, token: str | None = None):
        self.base_url = (base_url or os.environ["JIRA_BASE_URL"]).rstrip("/") + "/wiki"
        self.session = requests.Session()
        self.session.auth = (email or os.environ["JIRA_EMAIL"], token or os.environ["JIRA_API_TOKEN"])
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    def _check(self, resp: requests.Response) -> dict:
        if resp.status_code >= 400:
            raise RuntimeError(f"Confluence {resp.request.method} {resp.url} -> {resp.status_code} : {resp.text[:400]}")
        return resp.json()

    def space_id(self, space_key: str) -> str:
        data = self._check(self.session.get(f"{self.base_url}/api/v2/spaces", params={"keys": space_key}))
        if not data.get("results"):
            raise RuntimeError(f"Espace Confluence '{space_key}' introuvable")
        return data["results"][0]["id"]

    def find_page(self, space_id: str, title: str) -> dict | None:
        data = self._check(self.session.get(
            f"{self.base_url}/api/v2/spaces/{space_id}/pages", params={"title": title, "limit": 1}
        ))
        return data["results"][0] if data.get("results") else None

    def create_or_update_page(self, space_key: str, title: str, storage_html: str,
                              parent_title: str | None = None) -> str:
        """Crée la page (ou la met à jour si le titre existe déjà) et renvoie son URL."""
        space = self.space_id(space_key)
        parent = self.find_page(space, parent_title) if parent_title else None
        existing = self.find_page(space, title)
        body = {"representation": "storage", "value": storage_html}

        if existing:
            version = self._check(self.session.get(f"{self.base_url}/api/v2/pages/{existing['id']}"))["version"]
            page = self._check(self.session.put(f"{self.base_url}/api/v2/pages/{existing['id']}", json={
                "id": existing["id"], "status": "current", "title": title, "body": body,
                "version": {"number": version["number"] + 1, "message": "Mise à jour automatique"},
            }))
        else:
            payload = {"spaceId": space, "status": "current", "title": title, "body": body}
            if parent:
                payload["parentId"] = parent["id"]
            page = self._check(self.session.post(f"{self.base_url}/api/v2/pages", json=payload))
        return self.base_url + page["_links"]["webui"]
