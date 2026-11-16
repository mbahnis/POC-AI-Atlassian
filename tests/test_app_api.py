from app.api import reponse_paiement_refuse


def test_reponse_dans_la_langue_du_navigateur():
    corps = reponse_paiement_refuse("51", {"Accept-Language": "en-US,en;q=0.9"})
    assert corps["langue"] == "en" and "card limit" in corps["texte"]
    assert corps["action"] == {"libelle": "Try again", "reinitialiser_formulaire": True}


def test_affichage_sans_rechargement_et_sans_code_bancaire():
    corps = reponse_paiement_refuse("51", {"Accept-Language": "fr-FR"})
    assert corps["affichage"] == "sous_formulaire" and corps["recharger_page"] is False
    assert "51" not in corps["texte"]
