from datetime import date

from app.export import exporter_commandes_csv

COMMANDES = [
    {"numero": "C1", "date": date(2026, 11, 3), "client": "A. Martin", "adresse_livraison": "Paris",
     "montant_ttc": 99.8, "statut": "payee"},
    {"numero": "C2", "date": date(2026, 11, 5), "client": "B. Durand", "adresse_livraison": "Lyon",
     "montant_ttc": 20.0, "statut": "annulee"},
    {"numero": "C3", "date": date(2026, 10, 30), "client": "C. Petit", "adresse_livraison": "Lille",
     "montant_ttc": 15.0, "statut": "payee"},
]


def test_export_mois_et_statut_paye_uniquement():
    lignes = exporter_commandes_csv(COMMANDES, 2026, 11).strip().splitlines()
    assert lignes[0] == "numero;date;client;adresse_livraison;montant_ttc"
    assert lignes[1:] == ["C1;2026-11-03;A. Martin;Paris;99.8"]
