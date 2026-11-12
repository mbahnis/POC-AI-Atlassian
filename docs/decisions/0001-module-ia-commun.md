# 0001. Un module IA commun, indépendant du fournisseur

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

Les quatre briques du POC appellent toutes un modèle d'IA. Les clients grands comptes ont des contraintes différentes : certains imposent un hébergement chez leur cloud provider (AWS Bedrock, Google Vertex AI, Azure), d'autres un modèle interne. La question "et si on change de fournisseur ?" revient systématiquement.

## Décision

Tous les appels passent par un point d'entrée unique, `ai_core.ask()`, qui applique toujours la même séquence : prompt versionné, masquage des données, appel au fournisseur, journal d'audit.

Le fournisseur est une classe interchangeable (`ai_core/providers/`) choisie par variable d'environnement (`AI_PROVIDER`). Les briques ne connaissent ni le modèle ni le fournisseur, seulement le nom du prompt et un niveau ("fast" pour les tâches simples, "smart" pour le raisonnement).

## Alternatives écartées

- **Appeler l'API directement dans chaque script** (ScriptRunner, workflow...) : plus rapide à écrire, mais la logique de sécurité serait dupliquée et un changement de fournisseur toucherait tout le code.
- **Un framework d'orchestration (LangChain ou équivalent)** : surdimensionné pour des appels simples, ajoute une dépendance lourde à expliquer au client.

## Conséquences

- Changer de fournisseur = ajouter une classe d'environ 30 lignes et changer une variable.
- Les règles de sécurité (masquage, audit) s'appliquent partout sans effort, impossible de les oublier.
- Un faux fournisseur (`fake`) permet de tester sans coût et de répéter une démo hors connexion.
- Les déclencheurs (ScriptRunner, Jira Automation, GitHub Actions) restent de simples "portes d'entrée" vers ce module.
