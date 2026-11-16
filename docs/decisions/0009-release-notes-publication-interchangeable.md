# 0009. Brique 2 : statuts en natif, notes de version IA, publication interchangeable

- Statut : Acceptée
- Date : 16/11/2026

## Contexte

La brique 2 doit montrer une livraison tracée de bout en bout : ticket, branche, PR, déploiement, documentation. Une partie existe en natif (GitHub for Jira, déclencheurs Jira Automation sur les branches et PR). Par ailleurs, Confluence n'était pas accessible sur la sandbox au moment de construire la brique.

## Décision

1. **Statuts et affichage des branches, PR et déploiements : natif** (GitHub for Jira + deux flux Automation). Aucune ligne de code.
2. **Le code ne fait que ce que le natif ne sait pas faire** : rédiger les notes de version à partir des PR et des tickets, créer la version Jira, la rattacher aux tickets livrés et les commenter.
3. **La publication est interchangeable** : Confluence si `CONFLUENCE_SPACE_KEY` est défini, sinon la GitHub Release du tag.
4. **Les tickets sont retrouvés par leur clé** dans le nom de branche, le titre ou la description de la PR : c'est la convention que GitHub for Jira utilise déjà.
5. **Le modèle "smart" (Sonnet)** est utilisé : un texte lu par les métiers mérite un meilleur rédacteur, pour un coût qui reste de l'ordre du centime par release.
6. **Le premier tag sert de référence** : il ne génère pas de notes, pour éviter de résumer tout l'historique du dépôt.

## Alternatives écartées

- **Recoder les transitions de statut dans GitHub Actions** : ce que fait déjà le natif, en moins bien.
- **Attendre Confluence pour construire la brique** : aurait bloqué le POC ; la publication alternative démontre en plus l'indépendance vis-à-vis de l'outil de documentation.

## Conséquences

- La brique fonctionne même sans Confluence, ce qui est un argument pour les clients qui documentent ailleurs.
- La qualité des notes dépend de la discipline de nommage (clé de ticket dans la branche ou le titre de PR) : c'est aussi un bénéfice, puisque la démo encourage une bonne pratique.
- L'IA ne peut citer que des tickets et PR réellement présents : les références inventées sont retirées par le code.
