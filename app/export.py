"""Application fictive "Maison Lumen" : export des commandes pour la logistique (ticket PI-4)."""

import csv
import io
from datetime import date

COLONNES = ["numero", "date", "client", "adresse_livraison", "montant_ttc"]


def exporter_commandes_csv(commandes: list[dict], annee: int, mois: int) -> str:
    """Exporte en CSV les commandes payées d'un mois donné (séparateur ";" pour Excel FR)."""
    sortie = io.StringIO()
    writer = csv.DictWriter(sortie, fieldnames=COLONNES, delimiter=";", extrasaction="ignore")
    writer.writeheader()
    for commande in commandes:
        jour: date = commande["date"]
        if commande.get("statut") == "payee" and (jour.year, jour.month) == (annee, mois):
            writer.writerow({**commande, "date": jour.isoformat()})
    return sortie.getvalue()
