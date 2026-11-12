# 0004. GitHub Actions comme moteur d'exécution du POC

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

Le code IA doit tourner quelque part quand un événement survient (ticket créé, PR ouverte, incident clos). Options possibles : ScriptRunner (dans Jira), une fonction serverless (AWS Lambda, Cloud Run, Azure Functions), ou GitHub Actions.

## Décision

Pour le POC, le code s'exécute dans **GitHub Actions**. Jira déclenche les traitements via Jira Automation ("Send web request" vers l'API GitHub `repository_dispatch`) ou ScriptRunner.

## Pourquoi

- **Gratuit et déjà là** : aucun compte cloud à ouvrir, pas d'infrastructure à maintenir pour la démo.
- **Lisible** : chaque exécution est visible dans l'onglet Actions avec ses logs, utile pendant une démo.
- **Transposable** : les clients ont presque tous un équivalent (GitLab CI, Azure Pipelines, Jenkins). Le code Python ne dépend pas de GitHub, seul le fichier de workflow change.

## Alternatives écartées

- **Tout dans ScriptRunner** : réponse la plus rapide, mais logique enfermée dans une app payante que tous les clients n'ont pas. ScriptRunner reste proposé comme variante de déclenchement pour la brique 1.
- **AWS Lambda** : la meilleure option en production (réponse en quelques secondes, intégration IAM et secrets), mais demande un compte cloud et de l'infrastructure dès le départ.

## Conséquences

- Latence d'environ 20 à 40 secondes entre l'événement et le commentaire IA (démarrage du runner). Acceptable en démo, à annoncer.
- Chemin d'évolution documenté : même code Python déployé en Lambda (ou équivalent chez le client) quand la latence compte.
- Les secrets (clé IA, token Jira) sont stockés dans les Secrets GitHub, jamais dans le code.
