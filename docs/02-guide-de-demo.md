# 🎬 Guide de démo

> [!NOTE]
> **Pour qui ?** Le présentateur, pendant un rendez-vous client.
> **Comment l'utiliser ?** Le déroulé se lit de haut en bas : pour chaque étape, **ce que tu fais**, **ce que tu dis**, **ce qui doit apparaître**. Les sections dépliables "🙋 Si le client demande..." ne servent que si la question arrive.
> **Mis à jour le** 16/11/2026 : scénario de bout en bout répété (triage, revue de PR, livraison). Le post-mortem est en annexe.

**L'histoire racontée :** une journée normale dans une équipe. Un ticket arrive, un développeur code, on livre. À chaque étape, l'IA enlève une corvée, sans jamais décider à la place de l'équipe.

---

## ✅ Avant le rendez-vous

### Ce que Claude prépare (à lui demander : "remets le terrain à zéro pour une démo")

- [ ] Un ticket **"Appliquer un code promo au panier"** neuf (Story, 5 critères d'acceptation, label `poc-demo`), noté ci-dessous **PI-X**
- [ ] Une branche **`PI-X-code-promo`** poussée avec un **oubli volontaire** : les codes expirés ne sont pas refusés. Le ticket est donc déjà **En cours**
- [ ] Aucune PR ouverte ; les tickets de répétition clôturés (sinon ils apparaissent comme doublons)

### Ce que tu vérifies (5 min)

- [ ] Les flux Jira **"IA - Triage à la création"**, **"Dev - Branche créée"** et **"Dev - PR fusionnée"** sont **activés** (projet POC-IA > Paramètres de l'espace > Automatisation)
- [ ] Tu connais la **prochaine version** : regarde la dernière sur https://github.com/mbahnis/POC-AI-Atlassian/releases et ajoute 1 au chiffre du milieu (ex. après `v1.1.0` : `v1.2.0`)
- [ ] Ces onglets sont ouverts, dans cet ordre :
  1. Le **tableau Jira POC-IA** : https://one-atlas-bfqf-sandbox.atlassian.net/jira/software/projects/PI/boards
  2. Le **ticket PI-X**
  3. Les **pull requests GitHub** : https://github.com/mbahnis/POC-AI-Atlassian/pulls
  4. L'**espace Confluence POC IA** : https://one-atlas-bfqf.atlassian.net/wiki/spaces/POCIA
  5. Ce guide

> [!TIP]
> **Plans B** si le réseau lâche : le triage de **PI-13**, la revue de la PR **#20** (PI-12), la page **Release notes v1.1.0** dans Confluence. Tout est déjà visible.

---

## 🗺️ Déroulé (15 min)

| # | Séquence | Durée | Message clé |
|---|---|---|---|
| 0 | Ouverture | 1 min | "On ne vous vend pas de l'IA, on vous rend du temps" |
| 1 | Triage IA d'un ticket flou | 4 min | "Un ticket flou devient exploitable en 30 secondes" |
| 2 | Revue IA de la PR contre le ticket | 5 min | "L'oubli est repéré avant la recette" |
| 3 | Livraison tracée et notes de version | 4 min | "Le code, le ticket et la doc restent alignés, sans ressaisie" |
| 4 | Conclusion et garde-fous | 1 min | "L'IA propose, votre équipe décide" |

---

## 0️⃣ Ouverture (1 min)

**Tu dis :**
> "Vos équipes passent du temps sur des tâches à faible valeur : trier des tickets mal rédigés, vérifier que le code fait bien ce qui était demandé, mettre à jour des statuts, écrire des notes de version. Je vais vous montrer comment l'IA s'en charge **dans les outils que vous utilisez déjà**, Jira, Confluence et votre chaîne CI/CD, **sans jamais décider à votre place**."

**Tu montres :** le tableau Jira POC-IA.

---

## 1️⃣ Triage IA d'un ticket flou (4 min)

**Le problème :** le ticket du lundi matin, "ça marche pas", sans détail. Le chef de projet perd un quart d'heure à rappeler l'auteur et à chercher si quelqu'un a déjà signalé la même chose.

### 1.1 Créer le ticket

**Tu fais :** sur le tableau, **+ Créer**, puis :

| Champ | Valeur |
|---|---|
| Type | Bug |
| Résumé | `ça marche pas le paiement` |
| Description | `les clients se plaignent ça plante quand ils valident le panier pour payer, page d'erreur. urgent !! voir avec sophie.martin@maison-lumen.example elle a eu le client au tel` |
| Priorité | Medium |

Pas d'étiquette. **Créer**.

**Tu dis pendant la saisie :**
> "Voilà le ticket typique : pas d'étapes, pas d'environnement, un 'urgent' et un e-mail."

### 1.2 Laisser travailler (environ 30 s)

**Tu dis :**
> "Jira vient de prévenir notre chaîne d'automatisation. Avant d'envoyer quoi que ce soit à l'IA, on masque les données personnelles : l'e-mail de Sophie ne sort pas de chez vous. L'IA reçoit aussi les tickets ouverts, pour repérer les doublons."

### 1.3 Lire le résultat

**Tu fais :** rafraîchis le ticket, descends lentement dans le commentaire.

| Ce qui apparaît | Tu dis |
|---|---|
| 🔵 "Proposition de triage IA, à valider" | "Aucun champ modifié : c'est une proposition." |
| Titre reformulé | "Compréhensible par toute l'équipe sans ouvrir le ticket." |
| 🟠 Priorité Haute, justifiée | "Elle raisonne sur l'impact, pas sur le 'urgent' de l'auteur, et dit ce qui la ferait passer en Critique." |
| 🔁 PI-2 en confiance **forte** | "Quelqu'un avait déjà signalé la même chose. Sans elle, deux devs auraient pu travailler sur le même bug." |
| Doublon voisin en confiance **faible** | "Elle nuance : sujet voisin, problème différent." |
| ❓ Questions à l'auteur | "Le chef de projet n'a plus qu'à les copier." |
| 🛡️ "Données personnelles masquées" | "L'e-mail de Sophie n'apparaît nulle part." |

**Phrase de transition :**
> "10 minutes de tri deviennent 30 secondes de validation. Passons côté développeur."

---

## 2️⃣ Revue IA de la PR contre le ticket (5 min)

**Le problème :** le dev livre, les tests passent... mais il a oublié un critère du ticket. On le découvre en recette, une semaine plus tard.

### 2.1 Le ticket suit le code

**Tu fais :** ouvre **PI-X**. Montre les 5 critères d'acceptation, puis le panneau **Développement** (branche `PI-X-code-promo`) et le statut **En cours**.

**Tu dis :**
> "Le dev a commencé à coder. Il n'a rien mis à jour dans Jira : la clé du ticket dans le nom de sa branche a suffi. C'est du natif Atlassian."

### 2.2 Ouvrir la PR

**Tu fais :**
1. Onglet **Pull requests** de GitHub, **New pull request** (ou **Compare & pull request** si le bandeau jaune s'affiche).
2. base `main`, compare `PI-X-code-promo`.
3. Titre : `PI-X codes promo au panier`. Description : `Implémente les codes promo au panier.`
4. **Create pull request**.

**Tu dis pendant l'attente (environ 1 min) :**
> "Les tests passent, tout a l'air bon. Pendant ce temps, l'IA compare le code à chacun des 5 critères du ticket."

### 2.3 L'IA trouve l'oubli

**Tu fais :** rafraîchis la PR. Commentaire **🤖 Revue IA** : 4 critères ✅, et **❌ "Un code expiré est refusé"**.

**Tu dis :**
> "Le dev a oublié de vérifier la date d'expiration. Les tests passaient parce que ce cas n'était pas testé. Sans l'IA, on le découvrait en recette, ou un client utilisait un code périmé. Et le chef de projet est prévenu dans Jira."

Montre le commentaire **"Points à compléter"** dans **PI-X**.

### 2.4 Corriger en direct

**Tu fais :**
1. Dans la PR, onglet **Files changed**, fichier `app/promo.py`, **⋯** puis **Edit file**.
2. Sous ces deux lignes :
```python
    if offre is None:
        raise CodePromoRefuse("Code promo inconnu")
```
   colle (4 espaces avant `if`, 8 avant `raise`) :
```python
    if (aujourd_hui or date.today()) > offre["fin"]:
        raise CodePromoRefuse("Ce code promo a expiré")
```
3. **Commit changes...**, message `PI-X refus des codes expirés`, **Commit directly to the PI-X-code-promo branch**, **Commit changes**.

### 2.5 L'IA reconnaît la correction

**Tu fais :** attends environ 1 min, rafraîchis la PR : le **même** commentaire passe ✅ **Conforme**. PI-X reçoit un nouveau commentaire.

**Tu dis :**
> "Même commentaire mis à jour : pas de bruit à chaque push. L'IA ne remplace pas la revue humaine : elle répond à une seule question, est-ce que le code fait ce que le ticket demande ?"

---

## 3️⃣ Livraison tracée et notes de version (4 min)

**Le problème :** statuts Jira jamais à jour, et notes de version écrites à la main le vendredi soir, quand elles le sont.

### 3.1 Fusionner : le ticket se ferme seul

**Tu fais :** dans la PR, **Merge pull request**, **Confirm merge**. Reviens sur **PI-X** et rafraîchis : statut **Terminé**.

**Tu dis :**
> "Personne n'a touché au ticket : la fusion l'a fermé. Encore du natif."

### 3.2 Publier la version

**Tu fais :**
1. https://github.com/mbahnis/POC-AI-Atlassian/releases/new
2. **Tag: Select tag**, tape la prochaine version (ex. `v1.2.0`), puis **Create new tag ... on publish**. Target `main`.
3. Titre : la version. **Publish release**.

**Tu dis pendant l'attente (1 à 2 min) :**
> "On déploie, puis l'IA lit tout ce qui a été fusionné depuis la dernière version, les tickets associés, et rédige les notes de version pour vos métiers, pas pour les développeurs."

### 3.3 Montrer le résultat

**Tu fais :** dans Confluence (espace POC IA > Release notes), ouvre **"Release notes v1.2.0"**. Puis reviens sur **PI-X**.

| Ce qui apparaît | Tu dis |
|---|---|
| Le résumé en haut | "Lisible par le support et le produit." |
| La nouveauté "codes promo" | "Classée et expliquée par son effet pour l'utilisateur." |
| Les liens ticket et PR | "Chaque ligne est traçable ; l'IA ne peut citer que ce qui existe." |
| Dans PI-X : version et commentaire "Livré" | "Le support sait dans quelle version c'est sorti." |

---

## 4️⃣ Conclusion et garde-fous (1 min)

**Tu dis :**
> "Trois règles tout au long de ce que vous avez vu :
> 1. **L'IA propose, votre équipe décide.** Aucun champ modifié, aucune fusion bloquée.
> 2. **Vos données sont protégées** : masquées avant l'envoi, chaque appel est tracé.
> 3. **Vous n'êtes pas prisonniers** : on change de modèle, de cloud ou d'outil de CI sans tout refaire.
>
> Chaque brique est indépendante. **On commence par celle qui vous fait gagner le plus de temps.** Laquelle vous parle ?"

---

## 🙋 Si le client demande...

<details>
<summary><b>"Et nos données, elles partent où ?"</b></summary>

**À montrer :** le ticket **PI-6** ("bug login sur mobile"), qui contient un nom, un e-mail, un téléphone et une IP. Lancer un triage dessus (Actions > Brique 1 - Triage IA > Run workflow > `PI-6`), puis montrer que le commentaire ne reprend ni l'e-mail, ni le téléphone, ni l'IP.

**À dire :**
> "Le masquage se fait **avant** l'envoi, chez vous. L'IA ne reçoit que des balises `[EMAIL]`, `[TELEPHONE]`, `[IP]`. Limite honnête : les noms de personnes ne sont pas encore masqués ; on peut brancher un outil spécialisé si c'est un prérequis."

**Pour aller plus loin :** l'hébergement peut se faire chez AWS (Bedrock), Google (Vertex AI) ou Azure selon vos contraintes, à valider avec votre RSSI.
</details>

<details>
<summary><b>"Et si l'IA se trompe ?"</b></summary>

**À dire :**
> "Elle se trompe parfois, comme un humain. C'est pour ça qu'elle **propose** au lieu d'agir. Et le code contrôle ce qu'elle dit : si elle invente un composant qui n'existe pas chez vous, il est retiré avant d'arriver dans Jira. Si sa réponse est mal formée, on relance une fois, puis on abandonne plutôt que d'écrire quelque chose de faux."

**Argument bonus :** on a rencontré et corrigé ce cas pendant la construction du POC (voir la [décision 0008](decisions/0008-sorties-structurees.md)). C'est la preuve que les garde-fous ne sont pas théoriques.
</details>

<details>
<summary><b>"Pourquoi pas Rovo, qu'on a déjà ?"</b></summary>

**À dire :**
> "Rovo est excellent pour les usages standard, et on vous aidera à en tirer le maximum. Notre approche intervient quand vous avez besoin de **maîtriser** : votre modèle, votre hébergement, vos règles versionnées et relues, un audit détaillé, et surtout le lien avec votre chaîne CI/CD."

**À montrer :** le tableau de positionnement dans le [guide de la brique 1](guides/brique-1-triage.md#et-rovo-).

**Constat sur notre sandbox :** le modèle Atlassian "Utiliser l'agent Rovo pour trier les bugs" utilise par défaut une consigne générique (*"Analyse the description... How could it improve?"*) : il suggère d'améliorer la description, sans classement, doublons ni référentiel. Et son utilisation **nécessite qu'un administrateur de l'organisation active Rovo**.

> [!CAUTION]
> La qualité réelle de la réponse de Rovo n'a pas encore été testée (Rovo non activé). Ne pas affirmer que notre approche "fait mieux" : dire qu'elle **fait autre chose**, avec plus de maîtrise.
</details>

<details>
<summary><b>"On peut adapter le comportement à nos équipes ?"</b></summary>

**À montrer :** sur GitHub, le fichier `config/triage.yaml` (la liste des composants et labels autorisés), puis `ai_core/prompts/triage.md` (la consigne donnée à l'IA, en français lisible).

**À dire :**
> "Tout est lisible et modifiable : vos composants, vos labels, vos règles de priorité. Chaque modification passe par une relecture, comme du code, et on sait toujours quelle version des règles a produit quelle proposition."
</details>

<details>
<summary><b>"On est sous GitLab / Azure DevOps / Jenkins"</b></summary>

**À dire :**
> "Le cœur est indépendant de l'outil de CI. Seul le fichier de déclenchement change ; le flux Jira appelle simplement une autre adresse."

**À montrer :** le tableau "Adapter le POC à un autre client" dans [l'architecture](architecture.md#adapter-le-poc-à-un-autre-client).
</details>

<details>
<summary><b>"Ça coûte combien ?"</b></summary>

**À dire :**
> "Une fraction de centime par ticket. Chaque appel est tracé avec sa consommation, donc vous connaissez le coût réel au centime près. Pour 1 000 tickets par mois, on parle de quelques euros."

**À montrer (si besoin) :** l'artefact `ai-audit-log` d'un run GitHub Actions : tokens consommés, modèle, version du prompt.
</details>

<details>
<summary><b>"On n'utilise pas Confluence pour nos release notes"</b></summary>

**À dire :**
> "Aucun problème : la publication est interchangeable. Sans Confluence, les notes vont dans la release GitHub ; on peut aussi les envoyer vers votre wiki, SharePoint ou un canal Teams. Le cœur ne change pas."
</details>

<details>
<summary><b>"Et si un développeur oublie la clé du ticket ?"</b></summary>

**À dire :**
> "Sa PR n'est rattachée à aucun ticket : elle apparaît quand même dans les notes, mais sans lien Jira. On peut ajouter un contrôle dans la CI qui bloque une PR sans clé de ticket : c'est une règle simple qui améliore la traçabilité de toute l'équipe."
</details>

<details>
<summary><b>"Le déploiement, c'est un vrai déploiement ?"</b></summary>

**À dire :**
> "Dans la démo, il est simulé. Chez vous, on branche votre vraie chaîne : Terraform, Helm, ArgoCD... Ce qui compte, c'est que le déploiement soit déclaré dans un environnement nommé, ce qui le fait remonter dans Jira, et qu'on puisse y ajouter une validation manuelle avant la production."
</details>

<details>
<summary><b>"On a déjà un outil d'IA qui relit le code (Copilot, etc.)"</b></summary>

**À dire :**
> "Très bien, gardez-le : il juge la qualité du code. Le nôtre répond à une autre question, que ces outils ne peuvent pas trancher sans Jira : est-ce que le code fait ce que le métier a demandé ? Les deux se complètent."
</details>

<details>
<summary><b>"Et si l'IA dit qu'un critère manque alors qu'il est là ?"</b></summary>

**À dire :**
> "C'est possible, c'est pour ça que la revue ne bloque pas la fusion et qu'elle donne sa preuve : le développeur voit tout de suite si elle se trompe. On mesure le taux de faux positifs pendant quelques semaines avant d'envisager de la rendre bloquante."
</details>

<details>
<summary><b>"Notre code part chez un fournisseur d'IA ?"</b></summary>

**À dire :**
> "Seul le diff de la PR est envoyé, avec le masquage des données sensibles (e-mails, clés d'API...). Si c'est un point bloquant, le modèle peut être hébergé chez votre cloud provider (Bedrock, Vertex AI, Azure) : on change une variable, pas le code."
</details>

<details>
<summary><b>"On utilise PagerDuty / Opsgenie / JSM pour l'astreinte"</b></summary>

**À dire :**
> "Gardez votre outil d'astreinte : il reste celui qui réveille les gens. On se branche sur l'alerte ou sur l'incident Jira, et ce qu'on apporte, c'est le post-mortem. Avec Jira Service Management, l'incident est natif, avec ses délais de résolution."
</details>

<details>
<summary><b>"Et si l'IA se trompe de cause ?"</b></summary>

**À dire :**
> "C'est pour ça qu'elle parle d'hypothèse, avec un niveau de confiance et les faits qui l'appuient, et que la page est marquée brouillon. La revue du post-mortem reste un moment d'équipe : on lui fait juste gagner la partie la plus pénible, la mise en forme et la chronologie."
</details>

<details>
<summary><b>"Pourquoi 30 secondes ? C'est lent."</b></summary>

**À dire :**
> "Pour la démo, on utilise une machine qui démarre à la demande, gratuite. En production, le même code tourne en serverless et répond en quelques secondes. Et 30 secondes contre plusieurs heures d'allers-retours, c'est déjà un autre monde."
</details>

<details>
<summary><b>"Combien de temps pour le mettre en place chez nous ?"</b></summary>

**À dire :**
> "Pour le triage sur un projet : une demi-journée d'installation, puis deux ou trois semaines d'observation où l'on mesure le taux de propositions acceptées et où l'on ajuste les règles. Ensuite, on étend aux autres projets ou on ajoute une brique."
</details>

<details>
<summary><b>"Que se passe-t-il si l'IA est en panne ?"</b></summary>

**À dire :**
> "Le ticket est créé normalement, il n'a simplement pas de commentaire. Le run apparaît en échec côté automatisation, avec la cause. Rien n'est bloqué pour vos équipes : l'IA est un plus, pas un point de passage obligé."
</details>

---

## ➕ Annexe : de l'alerte au post-mortem (4 min, hors démo standard)

> [!IMPORTANT]
> **À préparer juste avant le rendez-vous :** lancer **Actions > Brique 4 - Alerte vers incident** (chronologie cochée). L'alerte est datée de 45 minutes avant le lancement, et la chronologie de l'astreinte est calée dessus. Passer ensuite l'incident à **En investigation** puis **Atténué** : la durée d'impact sera calculée sur ce passage.

> [!TIP]
> Plan B : le post-mortem de **PIOPS-1** est déjà publié dans Confluence (espace POC IA > Post-mortems).

### Étape 4.1 : l'alerte devient un incident

**À montrer :** l'incident dans le projet **POC IA - Exploitation** : "[Incident] Mémoire saturée sur api-commandes (98 %)".

**À dire :**
> "Cette nuit, la supervision a détecté une saturation mémoire. L'incident s'est créé tout seul, avec la gravité, le service touché, la procédure, et surtout le **dernier déploiement** : la version d'hier. C'est la première question que se pose l'astreinte. Ensuite, l'équipe a simplement commenté ce qu'elle faisait."

### Étape 4.2 : l'incident est clos, le post-mortem s'écrit

**À faire :** passer l'incident à **Terminé**, attendre 1 à 2 minutes, rafraîchir l'incident puis ouvrir le lien vers Confluence.

**À dire pendant l'attente :**
> "D'habitude, à ce moment-là, quelqu'un se promet d'écrire le post-mortem... et ne le fait jamais. Ici, l'IA relit l'incident, les commentaires et l'historique, et prépare le brouillon."

**À pointer sur la page :**

| Point | À dire |
|---|---|
| Le statut "BROUILLON À RELIRE" | "C'est un brouillon : l'équipe relit et corrige en 10 minutes au lieu de partir de zéro." |
| Les durées d'impact et totale | "Calculées par le code : du début de l'alerte jusqu'au service rétabli, puis jusqu'à la clôture. Pas estimées par l'IA." |
| La cause probable et sa confiance | "Une hypothèse, avec les faits qui l'appuient. L'équipe confirme en revue." |
| Aucun nom de personne | "Les commentaires citaient des prénoms : le post-mortem n'en contient aucun. Des rôles, pas des personnes." |
| Les actions proposées | "Proposées, pas créées : l'équipe choisit lesquelles devenir des tickets." |

---

---

## 🧹 Après le rendez-vous

- [ ] Demander à Claude de **remettre le terrain à zéro** (clôture des tickets de la démo, nouveau ticket PI-X et nouvelle branche)
- [ ] Noter les questions posées qui ne sont pas dans ce guide, pour l'enrichir
