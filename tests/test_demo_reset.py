from pathlib import Path

import yaml

from scripts.demo_reset import resolve_type

SEED = Path(__file__).resolve().parent.parent / "demo" / "seed_tickets.yaml"


def test_types_en_francais():
    available = ["Epic", "Tâche", "Bug", "Story"]
    assert resolve_type("Task", available) == "Tâche"
    assert resolve_type("Story", available) == "Story"


def test_type_absent_retombe_sur_tache():
    assert resolve_type("Story", ["Task", "Bug"]) == "Task"


def test_jeu_de_donnees_valide():
    seed = yaml.safe_load(SEED.read_text(encoding="utf-8"))
    assert seed["label"] == "poc-demo"
    ids = [t["id"] for t in seed["tickets"]]
    assert len(ids) == len(set(ids))
    for t in seed["tickets"]:
        assert t["summary"] and t["description"].strip() and t["role"]
