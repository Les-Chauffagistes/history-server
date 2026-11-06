import os

# Les settings sont chargés à l'import (init.py -> database -> settings) : valeurs factices pour les tests unitaires.
os.environ.setdefault("GATHER_STATS", "false")
os.environ.setdefault("PORT", "8050")
os.environ.setdefault("STATS_API_TOKEN", "test")
os.environ.setdefault("STATS_URL", "http://localhost")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
