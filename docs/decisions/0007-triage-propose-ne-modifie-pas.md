# 0007. Le triage IA propose en commentaire, il ne modifie pas le ticket

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

L'IA pourrait remplir directement la priorité, le composant et les labels du ticket. C'est plus spectaculaire en démo, mais une erreur de l'IA (priorité "Critique" à tort) déclencherait des notifications, fausserait les tableaux de bord et serait difficile à repérer après coup.

## Décision

1. Le résultat du triage est publié sous forme de **commentaire structuré**, clairement signalé comme une proposition à valider.
2. Le seul champ modifié est un label technique (`ia-triage`), qui sert à ne pas trier deux fois le même ticket.
3. L'IA ne peut proposer que des composants et labels issus du référentiel du projet (`config/triage.yaml`), pour éviter les valeurs inventées.
4. Le déclenchement automatique passe par **Jira Automation** (natif, présent dans toutes les licences Jira Cloud), qui appelle GitHub Actions. ScriptRunner reste une variante pour les clients qui l'ont déjà.

## Alternatives écartées

- **Écriture directe dans les champs** : à proposer seulement en phase 2, une fois que l'équipe du client fait confiance aux propositions (par exemple après un mois où l'on mesure le taux de propositions acceptées sans modification).
- **Déclenchement par ScriptRunner uniquement** : ferme la porte aux clients sans cette application.

## Conséquences

- Message clé en démo : "l'IA propose, votre équipe décide", démontré concrètement.
- Le commentaire garde une trace de ce que l'IA a proposé, même si l'équipe a choisi autre chose : utile pour mesurer la qualité dans le temps.
- Le token GitHub utilisé par Jira Automation n'a qu'un droit très limité (déclencher un workflow sur un seul dépôt).
