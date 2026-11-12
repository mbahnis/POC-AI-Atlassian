# 0003. Masquage des données et journal d'audit systématiques

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

Les tickets Jira contiennent souvent des données personnelles (e-mails et téléphones de clients finaux), des adresses de serveurs, parfois des secrets collés par erreur. La première question d'un RSSI sera : "qu'est-ce qui part vers l'IA, et comment le prouvez-vous ?".

## Décision

1. **Masquage avant envoi**, activé par défaut : e-mails, téléphones, adresses IP, IBAN, numéros de carte et formats de secrets connus (clés AWS, tokens GitHub...) sont remplacés par des balises (`[EMAIL]`, `[IP]`...) avant l'appel au modèle.
2. **Journal d'audit** : une ligne JSON par appel, avec l'appelant, le modèle, le prompt et sa version, les tokens consommés, la latence et le nombre d'éléments masqués par type.
3. **Le contenu n'est jamais journalisé**, seulement une empreinte (hash) qui permet de rapprocher deux appels sans exposer la donnée.

## Alternatives écartées

- **Masquage par un service spécialisé (ex. Microsoft Presidio)** : plus complet (détection des noms propres, adresses postales), mais lourd pour un POC. Le module est conçu pour le brancher plus tard sans rien changer d'autre.
- **Journaliser les prompts complets** : pratique pour déboguer, mais crée une copie des données sensibles hors de Jira.

## Conséquences

- Le masquage par expressions régulières ne détecte pas les noms de personnes : limite assumée et à annoncer au client.
- Le journal sert aussi au suivi des coûts (tokens par brique et par modèle).
- En CI, le journal est publié comme artefact de chaque exécution ; en production, il irait vers l'outil de logs du client (CloudWatch, ELK, Datadog...).
- Le masquage est désactivable (`AI_MASKING=off`) pour les environnements où le client l'estime inutile.
