---
name: smoke_test
version: 1
tier: fast
---
# System
Tu es un assistant intégré à une chaîne DevOps. Tu réponds en français, en JSON valide uniquement.

# User
Vérification de bon fonctionnement de la chaîne d'appel.
Contexte reçu : "$context"

Réponds avec exactement cet objet JSON, en remplissant les champs :
{"status": "ok", "resume_contexte": "<le contexte en 10 mots maximum>", "donnees_masquees_visibles": <true si tu vois des balises comme [EMAIL], sinon false>}
