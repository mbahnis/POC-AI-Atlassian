# 🔧 Mise en place

Guide pas à pas pour faire tourner le POC sur un nouvel environnement (environ 20 minutes).

## 1. Clé API Anthropic

1. Aller sur [console.anthropic.com](https://console.anthropic.com), rubrique **Settings > API Keys**.
2. **Create Key**, nom explicite (ex. `poc-atlassian-github`). Copier la clé, elle ne sera plus affichée.
3. Dans **Settings > Limits**, fixer une limite de dépense mensuelle (5 $ suffisent pour le POC).

> ⚠️ Ne jamais coller une clé dans un chat, un ticket ou un e-mail. Si c'est arrivé, la supprimer et en recréer une.

## 2. Token API Atlassian

1. Aller sur [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).
2. **Create API token**, nom explicite, durée de validité courte (le temps du POC).
3. Copier le token.

## 3. Secrets GitHub

Dans le dépôt : **Settings > Secrets and variables > Actions > New repository secret**.

| Nom | Valeur |
|---|---|
| `ANTHROPIC_API_KEY` | la clé de l'étape 1 |
| `JIRA_EMAIL` | l'e-mail du compte Atlassian |
| `JIRA_API_TOKEN` | le token de l'étape 2 |

Puis dans l'onglet **Variables** du même écran :

| Nom | Valeur |
|---|---|
| `JIRA_BASE_URL` | `https://<votre-site>.atlassian.net` |
| `JIRA_PROJECT_KEY` | `PI` |

## 4. Vérifier que tout fonctionne

1. Onglet **Actions** du dépôt > **Smoke test IA** > **Run workflow**.
2. Le job doit finir en vert avec le message `OK : chaîne IA fonctionnelle et données sensibles masquées avant envoi`.
3. Le journal d'audit est téléchargeable en bas de la page d'exécution (artefact `ai-audit-log`).

## 5. Remettre la démo à zéro (en local)

```bash
pip install -r requirements.txt
cp .env.example .env    # puis remplir les valeurs
set -a && source .env && set +a
python -m scripts.demo_reset            # simulation : affiche ce qui serait fait
python -m scripts.demo_reset --apply    # exécution
```

## Coût

Chaque exécution du smoke test coûte une fraction de centime. Le détail des tokens consommés figure dans le journal d'audit.
