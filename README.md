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

## Exemples

```bash
# 7 derniers jours bruts pour un worker
GET /v1/{address}/worker/{workername}/forever/last/7

# 180 derniers jours en agrégat journalier
GET /v1/{address}/worker/{workername}/daily/last/180

# 30 derniers jours pool-level (brut)
GET /v1/{address}/pool/forever/last/30

# Erreurs 400 attendues
GET /v1/{address}/worker/{workername}/forever/last/120  # n > 90
GET /v1/{address}/worker/{workername}/unknown/last/7   # source invalide
GET /v1/{address}/worker/{workername}/forever/last/abc # n non entier
```
