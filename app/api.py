"""Application fictive "Maison Lumen" : réponse de l'API au front quand un paiement est refusé (ticket PI-3).

Le front affiche le message sous le formulaire de paiement, sans recharger la page (appel asynchrone),
et le bouton d'action remet le formulaire à zéro quand "reinitialiser_formulaire" vaut True.
"""

from app.messages import langue_navigateur, message_refus


def reponse_paiement_refuse(code_banque: str, en_tetes: dict[str, str]) -> dict:
    """Corps JSON renvoyé au front : message dans la langue du navigateur, sans le code bancaire."""
    langue = langue_navigateur(en_tetes.get("Accept-Language"))
    message = message_refus(code_banque, langue)
    return {
        "statut": "refuse",
        "affichage": "sous_formulaire",
        "recharger_page": False,
        "langue": langue,
        **message,
    }
