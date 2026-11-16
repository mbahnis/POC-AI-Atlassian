# 🎬 Guide de démo

> [!NOTE]
> **Pour qui ?** Le présentateur, pendant un rendez-vous client.
> **Comment l'utiliser ?** Le déroulé principal se lit de haut en bas. Les sections dépliables **"🙋 Si le client demande..."** ne se jouent que si la question arrive.
> **Mis à jour le** 16/11/2026 : brique 1 (triage IA) prête et répétée en conditions réelles (PI-11). Brique 2 (livraison tracée) validée le 16/11 (release `v1.1.0`). Briques 3 et 4 à venir.

---

## ✅ Avant le rendez-vous (10 min)

- [ ] **Remettre la démo à zéro** : `python -m scripts.demo_reset --apply` (voir [mise en place](guides/mise-en-place.md#5-remettre-la-démo-à-zéro-en-local))
- [ ] **Supprimer les tickets de test et celui de la démo précédente** (tous les tickets **sans** label `poc-demo` : PI-9, PI-11...). Sinon, ils apparaîtront comme doublons du ticket créé en direct
- [ ] **Vérifier la priorité par défaut** du projet : elle doit être *Moyenne*, pas *Critique*
- [ ] **Vérifier que le flux** `IA - Triage à la création` est **activé** (Jira > Paramètres de l'espace > Automatisation)
- [ ] **Ouvrir ces onglets**, dans cet ordre :
  1. Le tableau Jira du projet **POC-IA**
  2. L'onglet **Actions** du dépôt GitHub (facultatif, pour montrer "la machine")
  3. Ce guide
- [ ] **Préparer le texte du ticket** à créer en direct (ci-dessous) dans un bloc-notes
- [ ] **Lancer un triage de test** sur un ticket jetable pour "réveiller" la chaîne, puis le supprimer

> [!TIP]
> Si le réseau du client est capricieux, gardez une capture d'un commentaire de triage réussi (par exemple sur PI-2) en plan B.

---

## 🗺️ Déroulé

| # | Séquence | Durée | Message clé |
|---|---|---|---|
| 0 | Ouverture | 1 min | "On ne vous vend pas de l'IA, on vous rend du temps" |
| 1 | Triage IA en direct | 4 min | "Un ticket flou devient exploitable en 30 secondes" |
| 2 | Les garde-fous | 2 min | "L'IA propose, votre équipe décide" |
| 3 | Conclusion | 1 min | "On commence par la brique qui vous fait gagner le plus" |

---

## 0️⃣ Ouverture (1 min)

**À dire :**
> "Vos équipes passent du temps sur des tâches à faible valeur : trier des tickets mal rédigés, mettre à jour des statuts, écrire des release notes, rédiger des post-mortems. Je vais vous montrer comment l'IA peut s'en charger **dans les outils que vous utilisez déjà**, Jira et Confluence, et **sans jamais décider à votre place**."

**À montrer :** le tableau Jira avec quelques tickets existants.

---

## 1️⃣ Triage IA en direct (4 min)

### Étape 1.1 : créer un ticket mal rédigé

**À faire :** cliquer sur **Créer** et saisir, sans le corriger :

| Champ | Valeur |
|---|---|
| Type | Bug |
| Résumé | `ça marche pas le paiement` |
| Description | `les clients se plaignent ça plante quand ils valident le panier pour payer, page d'erreur. urgent !! voir avec sophie.martin@maison-lumen.example elle a eu le client au tel` |

> [!WARNING]
> **Ne pas ajouter le label `poc-demo`** : le flux ignore volontairement les tickets qui le portent.

**À dire pendant la saisie :**
> "Voilà le ticket typique qu'un chef de projet reçoit le lundi matin : pas d'étapes, pas d'environnement, un 'urgent' et un e-mail. Normalement, il faut rappeler l'auteur."

### Étape 1.2 : laisser travailler (30 secondes)

**À faire (facultatif) :** basculer sur l'onglet **GitHub Actions** : un run "Brique 1 - Triage IA" démarre tout seul.

**À dire pendant l'attente :**
> "Jira vient de prévenir notre chaîne d'automatisation. Avant d'envoyer quoi que ce soit à l'IA, on **masque les données personnelles** : l'e-mail de Sophie ne sortira pas de chez vous. L'IA reçoit aussi la liste des tickets ouverts, pour repérer les doublons."

### Étape 1.3 : montrer le résultat

**À faire :** rafraîchir le ticket. Faire défiler le commentaire **lentement**, en s'arrêtant sur 4 points :

| Point | Ce qu'on pointe | À dire |
|---|---|---|
| 🔵 Encadré bleu | "Proposition de triage IA, à valider" | "C'est une **proposition**. Rien n'a été modifié dans le ticket." |
| 📝 Reformulation | Le nouveau titre | "Le titre devient compréhensible par toute l'équipe." |
| 🟠 Priorité | Haute, avec sa justification | "L'IA ne s'est pas laissé influencer par le 'urgent' : elle justifie, et dit ce qui ferait passer en Critique." |
| 🔁 Doublons | PI-2 en confiance **forte**, PI-1 en **moyenne** | "Elle a retrouvé PI-2, le même signalement fait la semaine dernière par quelqu'un d'autre. Et elle rapproche PI-1, un bug voisin mieux documenté, en disant qu'il faut **le confirmer**. Elle ne surinterprète pas." |
| ❓ Questions | 3 à 5 questions | "Le chef de projet n'a plus qu'à copier ces questions à l'auteur." |
| 🛡️ Bas du commentaire | "Données personnelles masquées" | "Et l'e-mail de Sophie n'apparaît nulle part." |

**Phrase de transition :**
> "Votre chef de projet passe de 10 minutes de tri et d'allers-retours à 30 secondes de validation."

---

## 2️⃣ bis. Livraison tracée (4 min)

> [!IMPORTANT]
> **À préparer avant le rendez-vous :** une branche au nom d'un ticket ouvert (ex. `PI-5-...`) avec une PR prête à être fusionnée, et le numéro de la prochaine version (la dernière publiée est `v1.1.0` : utiliser `v1.2.0`). Le guide de la brique 2 explique [comment rejouer la démo](guides/brique-2-release.md#rejouer-la-démo).

> [!TIP]
> Plan B si le réseau est lent : montrer la page **Release notes v1.1.0** déjà publiée dans l'espace Confluence **POC IA**, et les tickets PI-1 et PI-4 (version `v1.1.0`, commentaire "Livré").

### Étape 2.1 : le ticket suit le code, tout seul

**À faire :** ouvrir PI-1 dans Jira, montrer le panneau **Développement** (branche et PR liées), puis fusionner la PR sur GitHub et rafraîchir PI-1.

**À dire :**
> "Le développeur n'a rien mis à jour dans Jira. Il a juste mis la clé du ticket dans le nom de sa branche. Le ticket est passé En cours à la création de la branche, et Terminé à la fusion. Tout ça, c'est du **natif Atlassian** : votre licence le fait déjà, on l'a simplement branché."

### Étape 2.2 : la release documente elle-même

**À faire :** publier la release suivante (`v1.2.0`) sur GitHub (Releases > Draft a new release > Tag : saisir `v1.2.0` puis **Create new tag**), montrer le workflow qui se lance, puis ouvrir la page de notes de version dans l'espace Confluence **POC IA** et revenir sur le ticket.

**À dire pendant l'attente (environ 1 min) :**
> "On déploie. Pendant ce temps, l'IA lit les PR fusionnées depuis la dernière version et les tickets qu'elles citent, et elle rédige les notes de version pour vos métiers, pas pour les développeurs."

**À pointer sur la page :**

| Point | À dire |
|---|---|
| Le résumé en haut | "Lisible par le support et le produit, sans jargon." |
| Les catégories (nouveautés, corrections, technique) | "Classées automatiquement." |
| Les liens vers les tickets et PR | "Chaque ligne est traçable. L'IA ne peut citer que ce qui existe réellement." |
| Dans le ticket : la version et le commentaire "Livré" | "Le support sait immédiatement dans quelle version le bug est corrigé." |

**Phrase de transition :**
> "Fini les statuts oubliés et les release notes écrites le vendredi soir : le code, le ticket et la documentation restent alignés."

---

## 2️⃣ Les garde-fous (2 min)

**À dire, en montrant le commentaire :**
> "Trois règles non négociables :
> 1. **L'IA propose, votre équipe décide.** Aucun champ modifié sans validation humaine.
> 2. **Vos données sont protégées** : masquées avant l'envoi, et chaque appel est tracé dans un journal d'audit.
> 3. **Vous n'êtes pas prisonniers** d'un fournisseur d'IA : on peut changer de modèle ou l'héberger chez votre cloud provider."

---

## 3️⃣ Conclusion (1 min)

**À dire :**
> "Ce que vous avez vu est la première de quatre briques indépendantes : le triage, la livraison tracée avec release notes automatiques, la revue de code contre le ticket, et le post-mortem automatique après incident. **On commence par celle qui vous fait gagner le plus de temps.** Laquelle vous parle le plus ?"

> [!TIP]
> Terminer par une **question ouverte** : elle lance la discussion sur leur contexte, bien plus utile qu'une démo plus longue.

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

## 🧹 Après le rendez-vous

- [ ] Supprimer le ticket créé en direct (ou relancer `demo_reset`)
- [ ] Noter les questions posées qui ne sont pas dans ce guide, pour l'enrichir
