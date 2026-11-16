# 0008. Sorties structurées garanties par l'API (tool use)

- Statut : Acceptée
- Date : 12/11/2026

## Contexte

La première version du triage demandait à Claude de répondre "en JSON" dans du texte libre. Au premier essai réel, la réponse contenait des guillemets non échappés dans une phrase (`le bouton "Payer"`), ce qui rendait le JSON invalide et faisait échouer tout le traitement.

C'est un problème classique : tant que le format repose sur une consigne écrite, il finit par être enfreint de temps en temps, et chaque échec en démo coûte cher en crédibilité.

## Décision

Quand un usage a besoin d'une réponse structurée, on décrit le format dans un **schéma JSON** (`ai_core/prompts/<nom>.schema.json`), et le fournisseur **oblige** le modèle à le remplir via le mécanisme de *tool use* de l'API : Claude doit "appeler un outil" dont les paramètres sont exactement les champs attendus. L'API renvoie alors un objet déjà décodé, conforme au schéma.

Le schéma sert aussi de documentation : les listes fermées (priorités, niveaux de confiance) y sont définies une seule fois.

## Alternatives écartées

- **Renforcer la consigne dans le prompt** ("échappe les guillemets") : réduit le problème sans l'éliminer.
- **Réparer le JSON après coup** (bibliothèques de "JSON repair") : rattrape certains cas, en masque d'autres, et ajoute une dépendance.

## Conséquences

- Plus d'erreur de format sur les briques qui utilisent un schéma.
- La plupart des grands fournisseurs proposent un mécanisme équivalent (function calling, structured outputs) : le principe reste transposable si l'on change de fournisseur.
- La lecture "texte" (`extract_json`) est conservée en secours pour un fournisseur qui n'aurait pas ce mécanisme.

## Mise à jour du 16/11/2026 : mode strict et contrôle des réponses

Un test réel sur PI-2 a montré que le *tool use* simple ne suffit pas : le modèle a produit un objet dont un champ texte contenait du balisage d'appel d'outil (`</justification_priorite><parameter name="composant">Paiement`). Le champ "composant" s'est retrouvé avalé dans la justification, et le commentaire Jira affichait ce balisage.

Trois protections ont été ajoutées, du plus en amont au plus en aval :

1. **Mode strict de l'API** (`strict: true` sur l'outil) : la génération est contrainte par le schéma. Le schéma est adapté automatiquement (objets fermés, contraintes non prises en charge retirées) par `ai_core/validation.py`.
2. **Contrôle de chaque réponse** dans le moteur : conformité au schéma et détection de balisage parasite. Une réponse rejetée est relancée une fois ; un second échec arrête le traitement plutôt que de publier un commentaire faux. Le nombre de tentatives et les rejets sont écrits dans le journal d'audit.
3. **Règles métier appliquées par le code** (`normalize` dans le script de triage) : composant et labels hors référentiel retirés, nombre de questions plafonné, note bornée. Le code a le dernier mot sur ce que l'IA a le droit d'écrire.

Message pour les clients : on ne fait pas confiance aveuglément à la sortie d'un modèle, même structurée. On la contrôle comme n'importe quelle donnée entrante.

## Mise à jour du 16/11/2026 (2) : abandon du tool use au profit du format de réponse natif

Malgré le mode strict, le défaut est réapparu sur PI-11 (deux tentatives rejetées, toujours entre `justification_priorite` et `composant`). Le contrôle a joué son rôle (aucun commentaire faux publié), mais un triage en échec reste inacceptable en démo.

**Cause racine** : en tool use, le modèle produit ses paramètres dans une syntaxe interne d'appel d'outil. Le petit modèle (Haiku) laisse parfois fuir cette syntaxe à l'intérieur d'un champ texte. Le mode strict ne l'empêche pas, car le résultat reste un JSON valide : le balisage est *dans* une chaîne de caractères.

**Correction** :
- utilisation du **format de réponse structuré natif** de l'API (`output_config.format` de type `json_schema`) : le modèle écrit directement le JSON contraint par le schéma, sans passer par la syntaxe d'outil ;
- le champ `composant` n'accepte plus `null` (type unique `string`, valeur `inconnu` si rien ne convient), les champs sont réordonnés (classement d'abord, justification ensuite) ;
- le contrôle et la relance restent en place comme filet de sécurité.

**Leçon** : un garde-fou qui se déclenche est une information, pas seulement une protection. Le journal d'audit et les avertissements du run ont permis de localiser précisément le défaut.
