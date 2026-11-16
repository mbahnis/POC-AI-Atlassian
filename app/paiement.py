"""Application fictive "Maison Lumen" : module de paiement.

Ce code n'existe que pour la démo. Il donne de la matière aux branches,
PR et releases qui font avancer les tickets Jira (briques 2 et 3).
"""

from dataclasses import dataclass, field

MOYENS_ACCEPTES = {"carte", "paypal"}


class PaiementRefuse(Exception):
    """Le paiement a été refusé (motif lisible par le client, jamais le code bancaire)."""


@dataclass
class Panier:
    articles: dict[str, int] = field(default_factory=dict)  # référence -> quantité
    prix_unitaires: dict[str, float] = field(default_factory=dict)

    def total(self) -> float:
        manquants = [ref for ref in self.articles if ref not in self.prix_unitaires]
        if manquants:
            # Avant : KeyError non gérée, donc page d'erreur 500 au moment de payer
            raise PaiementRefuse("Un article de votre panier n'est plus disponible. Merci de le retirer.")
        return round(sum(q * self.prix_unitaires[ref] for ref, q in self.articles.items()), 2)


def valider_panier(panier: Panier, moyen: str) -> dict:
    """Valide le panier et retourne la commande créée."""
    if not panier.articles:
        raise PaiementRefuse("Votre panier est vide.")
    if moyen not in MOYENS_ACCEPTES:
        raise PaiementRefuse("Ce moyen de paiement n'est pas accepté.")
    return {"statut": "payee", "montant": panier.total(), "moyen": moyen}
