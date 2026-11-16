"""Application fictive "Maison Lumen" : messages affichés au client quand un paiement est refusé (ticket PI-3)."""

# Le code de refus renvoyé par la banque n'est jamais montré au client : on le traduit en catégorie lisible
CATEGORIES = {
    "05": "refus_generique",
    "51": "fonds_insuffisants",
    "54": "carte_expiree",
}

MESSAGES_FR = {
    "refus_generique": "Votre paiement a été refusé par votre banque. Vous pouvez réessayer ou utiliser un autre moyen de paiement.",
    "fonds_insuffisants": "Le paiement n'a pas abouti. Vérifiez le plafond de votre carte ou utilisez un autre moyen de paiement.",
    "carte_expiree": "Votre carte semble expirée. Vérifiez sa date de validité ou utilisez une autre carte.",
}


MESSAGES_EN = {
    "refus_generique": "Your payment was declined by your bank. You can try again or use another payment method.",
    "fonds_insuffisants": "The payment did not go through. Check your card limit or use another payment method.",
    "carte_expiree": "Your card seems to have expired. Check its expiry date or use another card.",
}

MESSAGES = {"fr": MESSAGES_FR, "en": MESSAGES_EN}
RESSAYER = {"fr": "Réessayer", "en": "Try again"}


def langue_navigateur(accept_language: str | None) -> str:
    """Déduit la langue d'affichage de l'en-tête Accept-Language du navigateur (français par défaut)."""
    for partie in (accept_language or "").split(","):
        code = partie.split(";")[0].strip().lower()[:2]
        if code in MESSAGES:
            return code
    return "fr"


def message_refus(code_banque: str, langue: str = "fr") -> dict:
    """Message à afficher sous le formulaire de paiement, avec l'action proposée au client."""
    langue = langue if langue in MESSAGES else "fr"
    categorie = CATEGORIES.get(code_banque, "refus_generique")
    return {
        "texte": MESSAGES[langue][categorie],
        "action": {"libelle": RESSAYER[langue], "reinitialiser_formulaire": True},
    }
