"""Chargement des prompts versionnés.

Chaque prompt est un fichier Markdown dans ai_core/prompts/ avec un
en-tête YAML (nom, version, niveau de modèle) puis deux sections :
"# System" et "# User". Les variables s'écrivent $variable.

Versionner les prompts dans Git permet de savoir quel prompt a produit
quelle réponse (la version est écrite dans le journal d'audit).
"""

from dataclasses import dataclass
from pathlib import Path
from string import Template

import yaml

PROMPTS_DIR = Path(__file__).parent / "prompts"


@dataclass
class Prompt:
    name: str
    version: str
    tier: str
    system: str
    user_template: str

    def render(self, variables: dict) -> str:
        # substitute (et non safe_substitute) : une variable oubliée doit faire échouer
        return Template(self.user_template).substitute(variables)


def load_prompt(name: str, prompts_dir: Path = PROMPTS_DIR) -> Prompt:
    raw = (prompts_dir / f"{name}.md").read_text(encoding="utf-8")
    _, front, body = raw.split("---", 2)
    meta = yaml.safe_load(front)
    system_part, user_part = body.split("# User", 1)
    system = system_part.replace("# System", "", 1).strip()
    return Prompt(
        name=meta["name"],
        version=str(meta["version"]),
        tier=meta.get("tier", "fast"),
        system=system,
        user_template=user_part.strip(),
    )
