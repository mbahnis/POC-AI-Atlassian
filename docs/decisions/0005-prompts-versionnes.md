# 0005. Prompts versionnés dans Git

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

La qualité des réponses de l'IA dépend surtout du prompt. Un prompt modifié peut améliorer un cas et en dégrader un autre. Il faut pouvoir savoir quel prompt a produit quelle réponse, et revenir en arrière.

## Décision

Chaque prompt est un fichier Markdown dans `ai_core/prompts/`, avec un en-tête (nom, version, niveau de modèle) et deux sections (`# System`, `# User`). Les variables s'écrivent `$variable`. La version du prompt est écrite dans le journal d'audit à chaque appel.

## Alternatives écartées

- **Prompts dans le code Python** : moins lisibles pour un non-développeur, modifications noyées dans le reste du code.
- **Prompts stockés dans Confluence** : séduisant pour l'édition par les métiers, mais sans historique fiable ni relecture par PR. Piste à garder pour une V2.

## Conséquences

- Un changement de prompt passe par une PR, donc par une relecture.
- Une variable oubliée fait échouer l'appel immédiatement, au lieu d'envoyer un prompt incomplet.
- Les présentateurs peuvent montrer les prompts tels quels au client : c'est souvent ce qui rassure le plus ("voilà exactement ce qu'on demande à l'IA").
