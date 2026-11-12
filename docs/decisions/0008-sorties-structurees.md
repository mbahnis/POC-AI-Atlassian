# 0008. Sorties structurées garanties par l'API (tool use)

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

La première version du triage demandait à Claude de répondre "en JSON" dans du texte libre. Au premier essai réel, la réponse contenait des guillemets non échappés dans une phrase (`le bouton "Payer"`), ce qui rendait le JSON invalide et faisait échouer tout le traitement.

C'est un problème classique : tant que le format repose sur une consigne écrite, il finit par être enfreint de temps en temps, et chaque échec en démo coûte cher en crédibilité.

## Décision

Quand un usage a besoin d'une réponse structurée, on décrit le format dans un **schéma JSON** (`ai_core/prompts/<nom>.schema.json`), et le fournisseur **oblige** le modèle à le remplir via le mécanisme de *tool use* de l'API : Claude doit "appeler un outil" dont les paramètres sont exactement les champs attendus. L'API renvoie alors un objet déjà décodé, conforme au schéma.

Le schéma sert aussi de documentation : les listes fermées (priorités, niveaux de confiance) y sont définies une seule fois.

## Alternatives écartées

- **Renforcer la consigne dans le prompt** ("échappe les guillemets") : réduit le problème sans l'éliminer.
- **Réparer le JSON après coup** (bibliothèques de "JSON repair") : rattrape certains cas, en masque d'autres, et ajoute une dépendance.

## Conséquences

- Plus d'erreur de format sur les briques qui utilisent un schéma.
- La plupart des grands fournisseurs proposent un mécanisme équivalent (function calling, structured outputs) : le principe reste transposable si l'on change de fournisseur.
- La lecture "texte" (`extract_json`) est conservée en secours pour un fournisseur qui n'aurait pas ce mécanisme.
