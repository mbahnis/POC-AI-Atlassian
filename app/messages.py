"""Application fictive "Maison Lumen" : messages affichés au client quand un paiement est refusé (ticket PI-3)."""

# Le code de refus renvoyé par la banque n'est jamais montré au client : on le traduit en catégorie lisible
CATEGORIES = {
    "05": "refus_generique",
    "51": "fonds_insuffisants",
    "54": "carte_expiree",
}

MESSAGES = {
    "refus_generique": "Votre paiement a été refusé par votre banque. Vous pouvez réessayer ou utiliser un autre moyen de paiement.",
    "fonds_insuffisants": "Le paiement n'a pas abouti. Vérifiez le plafond de votre carte ou utilisez un autre moyen de paiement.",
    "carte_expiree": "Votre carte semble expirée. Vérifiez sa date de validité ou utilisez une autre carte.",
}


def message_refus(code_banque: str, langue: str = "fr") -> dict:
    """Message à afficher sous le formulaire de paiement, avec l'action proposée au client."""
    categorie = CATEGORIES.get(code_banque, "refus_generique")
    return {"texte": MESSAGES[categorie], "action": {"libelle": "Réessayer", "reinitialiser_formulaire": True}}
