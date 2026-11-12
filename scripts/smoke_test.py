"""Vérifie la chaîne complète : prompt versionné > masquage > Claude > journal d'audit.

Usage : python -m scripts.smoke_test
Variables : ANTHROPIC_API_KEY (obligatoire), AI_PROVIDER, AI_MODEL_FAST (optionnelles)
"""

import sys

from ai_core import ask, extract_json

# Contexte volontairement piégé : l'e-mail et l'IP doivent être masqués avant l'envoi
CONTEXT = "Ticket créé par jean.dupont@client.fr, serveur 10.0.12.4 en erreur 500 sur le paiement"


def main() -> int:
    response = ask("smoke_test", {"context": CONTEXT}, caller="scripts/smoke_test")
    print(f"Modèle : {response.model}")
    print(f"Tokens : {response.input_tokens} en entrée, {response.output_tokens} en sortie")
    print(f"Réponse brute : {response.text}")

    data = extract_json(response.text)
    if data.get("status") != "ok":
        print("ECHEC : statut inattendu")
        return 1
    if data.get("donnees_masquees_visibles") is not True:
        print("ECHEC : le modèle ne voit pas de balises de masquage, vérifier ai_core/masking.py")
        return 1
    print("OK : chaîne IA fonctionnelle et données sensibles masquées avant envoi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
