# 0011. Brique 4 : alerte vers incident, post-mortem IA en brouillon "blameless"

- Statut : Acceptée
- Date : 16/11/2026

## Contexte

Les post-mortems sont souvent écrits des jours après l'incident, de mémoire, ou jamais. Le cas idéal pour un client Atlassian est Jira Service Management (JSM) pour les incidents et Confluence pour les post-mortems. Sur notre sandbox, JSM n'est pas activé : on ne peut ni créer de projet JSM, ni utiliser les projets d'exemple.

## Décision

1. **Format d'entrée Alertmanager** (le plus répandu dans l'écosystème Prometheus/Grafana), normalisé dans une seule fonction (`parse_alert`) pour s'adapter aux autres outils.
2. **Incidents dans un projet dédié et configurable** : Jira Software (`PIOPS`) en attendant JSM, sans dépendance du code au type de projet.
3. **Une alerte = un incident** : une alerte qui se répète commente l'incident ouvert (identifié par l'empreinte de l'alerte) ; une alerte résolue ne ferme pas l'incident, l'équipe décide.
4. **Le dernier déploiement est ajouté au contexte de l'incident** : c'est le lien entre la brique 2 et la brique 4, et souvent la première piste.
5. **Le post-mortem est un brouillon** : statut visible "BROUILLON À RELIRE", cause présentée comme une hypothèse avec niveau de confiance, questions ouvertes pour la revue.
6. **Blameless garanti à deux niveaux** : consigne au modèle (des rôles, jamais des noms) et nettoyage par le code des noms d'auteurs Jira.
7. **Le code calcule ce qui est factuel** (durée, dates) ; l'IA rédige et analyse.
8. **Aucun ticket d'action créé automatiquement** : l'équipe choisit en revue.
9. Modèle **"smart" (Sonnet)** : un post-mortem demande de relier des faits épars.

## Alternatives écartées

- **Attendre JSM** : aurait bloqué la brique ; le code est prêt à basculer.
- **Créer les incidents dans POC-IA** : mélange backlog de développement et exploitation, peu crédible en démo.
- **Post-mortem publié comme définitif** : un document d'analyse non relu risque d'ancrer une mauvaise cause.

## Conséquences

- La qualité du post-mortem dépend des commentaires de l'équipe pendant l'incident : la démo encourage cette bonne pratique.
- Les noms écrits dans le texte des commentaires (ex. "Astreinte (Léa)") ne sont retirés que par la consigne au modèle, pas par le code : point à vérifier à chaque relecture.
- Bascule JSM : deux variables à changer, plus éventuellement le nom du statut final dans le flux Automation.
