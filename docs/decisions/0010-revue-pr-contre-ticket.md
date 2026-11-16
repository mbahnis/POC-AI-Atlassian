# 0010. Brique 3 : revue IA de PR limitée à "le code fait-il ce que demande le ticket ?"

- Statut : Acceptée
- Date : 16/11/2026

## Contexte

Les outils de revue de code par IA se multiplient (y compris côté GitHub et Atlassian). La plupart commentent le style, les bugs potentiels et la sécurité. Ce qu'aucun ne fait bien sans contexte, c'est relier le code au **besoin métier exprimé dans Jira**. C'est exactement l'irritant cité dans le POC : un oubli fonctionnel (ex. la version anglaise d'un message) découvert en recette une semaine plus tard.

## Décision

1. **Une seule question** posée à l'IA : chaque critère d'acceptation du ticket est-il couvert par le diff ? Pas de revue de style ni d'architecture : c'est le rôle des humains et des outils existants.
2. **Quatre statuts** par critère (couvert, partiel, absent, non vérifiable) avec une **preuve** obligatoire. "Non vérifiable" évite que l'IA invente une conclusion sur ce que le code seul ne permet pas de juger (rendu visuel, comportement en production).
3. **Un seul commentaire par PR**, retrouvé grâce à un marqueur invisible et **mis à jour** à chaque push.
4. **Jira n'est commenté que si le verdict change**, pour informer le chef de projet sans bruit.
5. **Non bloquant** : la revue informe, elle ne refuse pas une fusion.
6. **Le code du relecteur vient de `main`**, jamais de la PR examinée (une PR ne doit pas pouvoir modifier ce qui la contrôle et accède aux secrets).
7. Modèle **"smart" (Sonnet)** : comparer un diff à des critères demande du raisonnement.

## Alternatives écartées

- **Revue de code générique par IA** : redondante avec l'existant et bruyante ; ne répond pas à l'irritant visé.
- **Revue bloquante dès le départ** : un faux positif bloquerait une livraison et décrédibiliserait l'outil. À envisager seulement après mesure de la fiabilité.
- **Nouveau commentaire à chaque push** : rapidement illisible.

## Conséquences

- La qualité dépend de la qualité des critères d'acceptation : un ticket flou donne une revue floue. La brique 1 (triage) aide justement à obtenir des critères clairs : les briques se renforcent.
- Les diffs très longs sont tronqués (limite réglable) et la revue le signale.
