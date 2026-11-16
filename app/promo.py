"""Application fictive "Maison Lumen" : codes promo appliqués au panier (ticket PI-12)."""

from datetime import date

# Catalogue des codes : réduction en pourcentage et date de fin de validité
CODES = {
    "BIENVENUE10": {"reduction": 10, "fin": date(2027, 12, 31)},
    "NOEL25": {"reduction": 25, "fin": date(2026, 12, 31)},
    "ETE2026": {"reduction": 15, "fin": date(2026, 9, 1)},
    "MEGA70": {"reduction": 70, "fin": date(2027, 6, 30)},
}
REDUCTION_MAX = 50  # en pourcentage du total du panier


class CodePromoRefuse(Exception):
    """Le code promo ne peut pas être appliqué (message lisible par le client)."""


def appliquer_code(total: float, code: str, aujourd_hui: date | None = None) -> dict:
    """Applique un code promo au total du panier et retourne le détail du calcul."""
    offre = CODES.get(code.strip().upper())
    if offre is None:
        raise CodePromoRefuse("Code promo inconnu")
    pourcentage = min(offre["reduction"], REDUCTION_MAX)
    reduction = round(total * pourcentage / 100, 2)
    return {"total_initial": total, "reduction": reduction, "total": round(total - reduction, 2),
            "pourcentage": pourcentage}
