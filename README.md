# history-server API

Base URL : `http://<host>:<port>/v1`

---

## Endpoints existants

### `GET /{address}/worker/{workername}/{period}`

Retourne tout l'historique disponible pour un worker.

| Paramètre | Valeurs | Description |
|---|---|---|
| `address` | adresse BTC | Identifiant du pool/utilisateur |
| `workername` | string | Nom du worker |
| `period` | `forever` \| `daily` | Source de données |

- `forever` → `worker_stats_raw` (90 jours, résolution 1 min/5 min/1 h)
- `daily` → `worker_stats_1d` (archive long terme, 1 ligne par jour)

---

### `GET /{address}/pool`

Retourne l'historique pool-level (somme de tous les workers) depuis `worker_stats_raw`.

---

## Nouveaux endpoints — derniers N jours

### `GET /{address}/worker/{workername}/{source}/last/{n}`

Retourne les N derniers jours d'historique pour un worker.

| Paramètre | Valeurs | Description |
|---|---|---|
| `address` | adresse BTC | Identifiant du pool/utilisateur |
| `workername` | string | Nom du worker |
| `source` | `forever` \| `daily` | Source de données (voir tableau ci-dessous) |
| `n` | entier > 0 | Nombre de jours |

| `source` | Table interrogée | Résolution | Limite |
|---|---|---|---|
| `forever` | `worker_stats_raw` | brut (toutes les 30 min) | n ≤ 90 (rétention) |
| `daily` | `worker_stats_1d` | 1 ligne/jour | aucune |

**Réponse 200 :**
```json
[
  {
    "timestamp": "2026-02-20T00:00:00+00:00",
    "avg_hashrate1m": 12500000,
    "avg_hashrate5m": 12400000,
    "avg_hashrate1h": 12300000,
    "avg_hashrate1d": 12200000,
    "avg_hashrate7d": 12100000,
    "avg_weight": 1.0
  }
]
```

> **Note :** avec `source=daily`, le bucket du jour courant n'est jamais présent (TimescaleDB n'agrège que les journées complètes). La donnée la plus récente est donc celle d'hier.

**Erreurs :**

| Code | Raison |
|---|---|
| 400 | `source` inconnu (ni `forever` ni `daily`) |
| 400 | `n` n'est pas un entier positif |
| 400 | `source=forever` et `n > 90` (données purgées par la rétention) |

---

### `GET /{address}/pool/{source}/last/{n}`

Retourne les N derniers jours d'historique pool-level (somme de tous les workers).

Mêmes paramètres et mêmes règles de validation que l'endpoint worker ci-dessus.

**Réponse 200 :**
```json
[
  {
    "timestamp": "2026-02-20T00:00:00+00:00",
    "avg_hashrate1h": 98000000,
    "avg_hashrate1d": 97500000
  }
]
```

---

### `GET /{address}/distribution?at=<date ISO 8601>`

Répartition du travail entre les workers d'une adresse à une date donnée (utilisée pour le paiement des récompenses de block).

| Paramètre | Description |
|---|---|
| `address` | adresse BTC (identifiant du pool/utilisateur) |
| `at` | date ISO 8601 **avec fuseau obligatoire** (`2026-11-04T17:09:23Z`, `...+01:00`). Un `+` doit être encodé (`%2B`) ; un offset reçu sous la forme ` 01:00` est toléré. Normalisée en UTC. |

**Source** : `worker_stats_raw.avg_weight` (pourcentage de chaque worker calculé par pool-api sur sa fenêtre glissante `distribution_window_days`, échantillonné toutes les 30 min par le crawler). Aucune interpolation : on prend le dernier échantillon dont le timestamp est `<= at` (toutes les lignes de l'adresse dans les 60 s précédant ce timestamp, une par worker). Les poids sont renormalisés par leur somme : `part` est une **fraction 0-1** et **la somme des parts vaut 1** (aux erreurs flottantes près). Le résultat est déterministe pour un `at` donné (tri par `part` décroissant puis `workername`).

L'échantillon est refusé s'il est plus vieux que 2 h par rapport à `at` (4 passes du crawler manquées).

**Réponse 200 :**
```json
[
  {"workername": "asic1", "part": 0.75, "sampled_at": "2026-11-04T16:59:23+00:00"},
  {"workername": "asic2", "part": 0.25, "sampled_at": "2026-11-04T16:59:23+00:00"}
]
```

`diff_sum`, `shares_ok` et `shares_ko` (cf. `PoolDistributionElement` de chauff-cmn) ne sont **pas** disponibles : history-server ne stocke que le poids relatif, pas les shares.

**Erreurs :**

| Code | Raison |
|---|---|
| 400 | `at` absent, non ISO 8601, sans fuseau (ex. timestamp unix) ou dans le futur |
| 404 | aucun échantillon `<= at` (adresse inconnue, `at` antérieur à la rétention de `worker_stats_raw`, ou trou de collecte > 2 h), ou poids total nul |

Les données compressées par TimescaleDB restent lisibles ; seule la rétention (purge) rend une date inaccessible.

---

## Exemples

```bash
# 7 derniers jours bruts pour un worker
GET /v1/{address}/worker/{workername}/forever/last/7

# 180 derniers jours en agrégat journalier
GET /v1/{address}/worker/{workername}/daily/last/180

# 30 derniers jours pool-level (brut)
GET /v1/{address}/pool/forever/last/30

# Répartition à la date de minage du block
GET /v1/{address}/distribution?at=2026-11-04T17:09:23Z

# Erreurs 400 attendues
GET /v1/{address}/worker/{workername}/forever/last/120  # n > 90
GET /v1/{address}/worker/{workername}/unknown/last/7   # source invalide
GET /v1/{address}/worker/{workername}/forever/last/abc # n non entier
```
