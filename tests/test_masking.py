from ai_core.masking import mask


def test_masque_email_ip_telephone():
    text, counts = mask("Contact jean.dupont@client.fr ou 06 12 34 56 78, serveur 10.0.12.4")
    assert "jean.dupont" not in text and "10.0.12.4" not in text and "06 12" not in text
    assert counts == {"EMAIL": 1, "TELEPHONE": 1, "IP": 1}


def test_masque_secrets():
    text, counts = mask("token ghp_abcdefghijklmnopqrstuvwxyz123456 et AKIAABCDEFGHIJKLMNOP")
    assert "ghp_" not in text and "AKIA" not in text
    assert counts["SECRET"] == 2


def test_masque_iban_et_carte():
    _, counts = mask("IBAN FR76 3000 6000 0112 3456 7890 189, carte 4970 1012 3456 7890")
    assert counts.get("IBAN") == 1 and counts.get("CARTE") == 1


def test_texte_neutre_inchange():
    original = "Echec du paiement par carte à la validation du panier (version 1.4.2)"
    text, counts = mask(original)
    assert text == original and counts == {}
