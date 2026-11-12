# 0006. Données de démo fictives et réinitialisables

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

Le POC sera présenté par plusieurs personnes, à des clients différents. Une démo qui dépend de l'état laissé par la précédente finit toujours par rater devant le client.

## Décision

- Un jeu de tickets **100 % fictif** (boutique en ligne imaginaire "Maison Lumen") décrit dans `demo/seed_tickets.yaml`, chaque ticket documentant son rôle dans le fil rouge.
- Un script `scripts/demo_reset.py` qui supprime les tickets portant le label `poc-demo` (et uniquement eux) puis recrée le jeu à l'identique.
- Le script fonctionne en simulation par défaut et n'agit qu'avec `--apply`.

## Conséquences

- N'importe quel collègue remet la démo à zéro en une commande avant un rendez-vous.
- Aucune donnée réelle de client dans le POC.
- Le script s'adapte à la langue de l'instance Jira (types "Task" ou "Tâche"), ce qui le rend réutilisable sur le Jira d'un client.
