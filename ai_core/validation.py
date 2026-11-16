"""Contrôle qualité des réponses structurées.

Même avec une sortie structurée, un modèle peut produire une réponse
"valide en apparence" mais corrompue (par exemple du balisage d'appel
d'outil glissé dans un champ texte). On vérifie donc chaque réponse
avant de l'utiliser : structure conforme au schéma et absence de
balisage parasite. En cas d'échec, le moteur relance une fois.
"""

import copy
import re

import jsonschema

# Mots-clés que le mode "strict" de l'API ne prend pas en charge : ils restent
# dans le schéma de référence (documentation, tests) et sont appliqués par le code métier.
STRICT_UNSUPPORTED = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
                      "minLength", "maxLength", "maxItems", "pattern"}

# Traces de balisage d'appel d'outil qui ne doivent jamais apparaître dans un texte métier
CORRUPTION_PATTERN = re.compile(r"</?(parameter|invoke|function_calls)\b|</[a-z_]{3,}>")


def to_strict_schema(schema: dict) -> dict:
    """Adapte un schéma au mode strict : objets fermés, contraintes non prises en charge retirées."""
    schema = copy.deepcopy(schema)

    def walk(node):
        if isinstance(node, dict):
            for key in list(node):
                if key in STRICT_UNSUPPORTED or (key == "minItems" and node[key] > 1):
                    del node[key]
            # ["string", "null"] -> anyOf, forme la plus largement acceptée par les modes stricts
            if isinstance(node.get("type"), list):
                node["anyOf"] = [{"type": t} for t in node.pop("type")]
            if node.get("type") == "object":
                node["additionalProperties"] = False
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema)
    return schema


def find_problems(data: dict, schema: dict) -> list[str]:
    """Retourne la liste des problèmes détectés (vide si la réponse est saine)."""
    problems = [
        f"{'/'.join(str(p) for p in err.absolute_path) or 'racine'} : {err.message}"
        for err in jsonschema.Draft202012Validator(to_strict_schema(schema)).iter_errors(data)
    ]

    def scan(value, path):
        if isinstance(value, str) and CORRUPTION_PATTERN.search(value):
            problems.append(f"{path} : balisage parasite dans le texte")
        elif isinstance(value, dict):
            for k, v in value.items():
                scan(v, f"{path}/{k}")
        elif isinstance(value, list):
            for i, v in enumerate(value):
                scan(v, f"{path}/{i}")

    scan(data, "")
    return problems
