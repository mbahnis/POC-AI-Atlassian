from app.messages import langue_navigateur, message_refus


def test_message_lisible_sans_code_bancaire():
    message = message_refus("51")
    assert "plafond" in message["texte"]
    assert "51" not in message["texte"]


def test_code_inconnu_message_generique():
    assert "refusé par votre banque" in message_refus("99")["texte"]


def test_action_reessayer_reinitialise_le_formulaire():
    assert message_refus("05")["action"] == {"libelle": "Réessayer", "reinitialiser_formulaire": True}


def test_message_en_anglais():
    message = message_refus("54", langue="en")
    assert "expired" in message["texte"] and message["action"]["libelle"] == "Try again"


def test_langue_du_navigateur():
    assert langue_navigateur("en-GB,en;q=0.9,fr;q=0.8") == "en"
    assert langue_navigateur("de-DE,fr;q=0.7") == "fr"
    assert langue_navigateur(None) == "fr"
