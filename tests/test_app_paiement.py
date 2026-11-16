import pytest

from app.paiement import PaiementRefuse, Panier, valider_panier


def panier_simple():
    return Panier(articles={"lampe": 2}, prix_unitaires={"lampe": 49.9})


def test_paiement_carte_ok():
    commande = valider_panier(panier_simple(), "carte")
    assert commande == {"statut": "payee", "montant": 99.8, "moyen": "carte"}


def test_panier_vide_refuse():
    with pytest.raises(PaiementRefuse, match="vide"):
        valider_panier(Panier(), "carte")


def test_moyen_inconnu_refuse():
    with pytest.raises(PaiementRefuse):
        valider_panier(panier_simple(), "cheque")


def test_article_sans_prix_ne_provoque_plus_d_erreur_500():
    panier = Panier(articles={"lampe": 1, "vase-retire": 1}, prix_unitaires={"lampe": 49.9})
    with pytest.raises(PaiementRefuse, match="plus disponible"):
        valider_panier(panier, "carte")
