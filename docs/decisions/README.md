# 📒 Décisions d'architecture

Chaque choix structurant du POC est consigné dans une fiche courte : le contexte, la décision, les alternatives écartées et leurs conséquences. Objectif : pouvoir répondre en rendez-vous client à la question "pourquoi avez-vous fait comme ça ?", et réutiliser le raisonnement chez un autre client.

| # | Décision | Statut |
|---|---|---|
| [0001](0001-module-ia-commun.md) | Un module IA commun, indépendant du fournisseur | Acceptée |
| [0002](0002-natif-atlassian-avant-code.md) | Utiliser le natif Atlassian avant d'écrire du code | Acceptée |
| [0003](0003-masquage-et-audit.md) | Masquage des données et journal d'audit systématiques | Acceptée |
| [0004](0004-github-actions-moteur-execution.md) | GitHub Actions comme moteur d'exécution du POC | Acceptée |
| [0005](0005-prompts-versionnes.md) | Prompts versionnés dans Git | Acceptée |
| [0006](0006-donnees-demo-reinitialisables.md) | Données de démo fictives et réinitialisables | Acceptée |
| [0007](0007-triage-propose-ne-modifie-pas.md) | Le triage IA propose en commentaire, il ne modifie pas le ticket | Acceptée |
| [0008](0008-sorties-structurees.md) | Sorties structurées garanties par l'API (tool use) | Acceptée |

## Modèle de fiche

```markdown
# NNNN. Titre court

- Statut : Proposée | Acceptée | Remplacée par NNNN
- Date : JJ/MM/AAAA

## Contexte
## Décision
## Alternatives écartées
## Conséquences
```
