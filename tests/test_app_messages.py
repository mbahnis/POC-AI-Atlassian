from app.messages import message_refus


def test_message_lisible_sans_code_bancaire():
    message = message_refus("51")
    assert "plafond" in message["texte"]
    assert "51" not in message["texte"]


def test_code_inconnu_message_generique():
    assert "refusé par votre banque" in message_refus("99")["texte"]


def test_action_reessayer_reinitialise_le_formulaire():
    assert message_refus("05")["action"] == {"libelle": "Réessayer", "reinitialiser_formulaire": True}
