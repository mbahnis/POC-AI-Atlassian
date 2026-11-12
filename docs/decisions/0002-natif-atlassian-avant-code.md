# 0002. Utiliser le natif Atlassian avant d'écrire du code

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

Une partie de ce que montre le POC existe déjà dans l'écosystème Atlassian :
- l'application "GitHub for Jira" relie branches, commits, PR et déploiements aux tickets ;
- Jira Automation sait réagir à ces événements (branche créée, PR fusionnée...) pour changer un statut ;
- Rovo apporte une IA native dans Jira et Confluence.

Recoder ces fonctions serait contre-productif face à un client qui les connaît, et incohérent pour une offre dont le but est de vendre et d'intégrer les produits Atlassian.

## Décision

Pour chaque besoin, on regarde d'abord ce que fournit Atlassian en standard. On n'écrit du code que pour ce que le natif ne couvre pas : l'IA appliquée au contexte du client (triage, release notes, revue contre le ticket, post-mortem) et le lien avec ses outils DevOps.

Concrètement pour la brique 2 : statuts Jira pilotés par GitHub for Jira + Jira Automation (zéro code), et code uniquement pour les release notes générées par l'IA et la remontée du déploiement.

## Alternatives écartées

- **Tout coder dans GitHub Actions** : démontre une compétence technique mais pas la maîtrise de l'outil vendu, et crée de la maintenance inutile chez le client.

## Conséquences

- Message commercial plus juste : "on tire le maximum de ce que vous payez déjà, et on ajoute l'IA là où elle apporte quelque chose".
- Positionnement face à Rovo à préparer pour chaque démo : Rovo pour les usages standard, notre approche pour le sur-mesure relié à la chaîne CI/CD, avec le choix du modèle et de l'hébergement.
- Certaines briques existent en deux variantes (native et sur-mesure) pour s'adapter aux licences du client (ex. avec ou sans ScriptRunner).
