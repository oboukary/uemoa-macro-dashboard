# 🌍 UEMOA Macro Dashboard

Tableau de bord **Streamlit** des indicateurs macroéconomiques des huit pays de
l'**UEMOA** (Union Économique et Monétaire Ouest-Africaine) : Bénin, Burkina Faso,
Côte d'Ivoire, Guinée-Bissau, Mali, Niger, Sénégal, Togo.

Les données sont extraites en temps réel depuis l'**API de la Banque mondiale**
(V1), avec une architecture prête pour le **FMI / WEO** et **FRED** (V2).

---

## ✨ Fonctionnalités (V1)

- **Vue régionale** — synthèse, évolution et classement des 8 pays pour un indicateur.
- **Comparaison pays** — trajectoires comparées, période ajustable, classement.
- **Fiche pays** — tableau de bord mono-pays (KPI + petits graphiques).
- **Sources & méthodologie** — provenance des données, catalogue d'indicateurs, limites.
- **Export CSV** sur chaque vue.
- Interface soignée : barre latérale sombre, cartes KPI, graphiques Plotly interactifs.

12 indicateurs (PIB, croissance, inflation, population, chômage, dette, commerce
extérieur, IDE, espérance de vie…) configurables dans
[`app/data/indicators.yml`](app/data/indicators.yml).

---

## 🗂️ Structure du projet

```
app streamlit/
├── app/
│   ├── main.py                    # Page d'accueil : Vue régionale
│   ├── pages/
│   │   ├── 1_Comparaison_pays.py
│   │   ├── 2_Fiche_pays.py
│   │   └── 3_Sources_methodologie.py
│   ├── data/
│   │   ├── extract_worldbank.py   # ✅ API Banque mondiale (V1)
│   │   ├── extract_imf.py         # 🧩 API FMI / DataMapper (V2)
│   │   ├── extract_fred.py        # 🔑 API FRED (V2, clé requise)
│   │   └── indicators.yml         # Catalogue d'indicateurs
│   └── utils/
│       ├── config.py   countries.py   sidebar.py
│       ├── charts.py   format.py       theme.py
├── assets/styles.css              # Habillage CSS
├── .streamlit/config.toml         # Thème & serveur
├── requirements.txt
├── Dockerfile · docker-compose.yml
├── .github/workflows/deploy.yml   # CI : checks + build/push image
├── .env.example · .gitignore · .dockerignore
└── README.md
```

---

## 🚀 Démarrage rapide (local)

> Prérequis : Python 3.11+ (testé sur 3.13).

### Avec uv (recommandé)

[uv](https://docs.astral.sh/uv/) crée le venv et installe les dépendances en
une fraction du temps, et fige la version de Python (évite les venv incohérents).

```bash
# 1. Environnement virtuel (Python épinglé)
uv venv --python 3.13 .venv

# 2. Dépendances
uv pip install -r requirements.txt

# 3. Lancement
uv run --python .venv streamlit run app/main.py
```

### Avec pip (classique)

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
streamlit run app/main.py
```

L'application est disponible sur http://localhost:8501.

> ⚠️ Ne lancez jamais `python -m venv .venv` par-dessus un venv existant avec une
> version de Python différente : cela réécrit l'interpréteur sans réinstaller les
> paquets (numpy/pandas compilés deviennent incompatibles). En cas de doute,
> supprimez `.venv` et recréez-le avec uv.

---

## 🐳 Docker

```bash
# Build + run avec docker-compose (recommandé)
docker compose up --build

# …ou en deux temps
docker build -t uemoa-macro-dashboard .
docker run -p 8501:8501 uemoa-macro-dashboard
```

Puis ouvrir http://localhost:8501.

---

## 🔐 Configuration

Copiez `.env.example` en `.env` et renseignez si besoin :

| Variable | Rôle | Défaut |
|---|---|---|
| `FRED_API_KEY` | Clé API FRED (contexte mondial, V2) | — (optionnel) |
| `CACHE_TTL` | Durée de cache des appels API (secondes) | `21600` (6 h) |

Clé FRED gratuite : https://fred.stlouisfed.org/docs/api/api_key.html

---

## 🔄 CI/CD (GitHub Actions)

[`/.github/workflows/deploy.yml`](.github/workflows/deploy.yml) à chaque push sur `main` :

1. **checks** — installe les dépendances, compile les sources, smoke test des imports.
2. **docker** — build l'image et la publie sur **GitHub Container Registry**
   (`ghcr.io/<owner>/uemoa-macro-dashboard`).

Pour activer la publication, vérifiez que les *workflow permissions* du dépôt
autorisent l'écriture des packages (Settings → Actions → General).

---

## 🛣️ Feuille de route

| Version | Contenu |
|---|---|
| **V1** ✅ | Banque mondiale · 8 pays · 12 indicateurs · graphiques comparatifs · export CSV |
| **V2** 🧩 | FMI (WEO) · FRED (contexte mondial) · cache DuckDB · rafraîchissement auto |
| **V3** 🔭 | Prévisions simples · scoring macro par pays · rapport PDF automatique |

---

## 📚 Sources de données

- **Banque mondiale** — API v2 : <https://datahelpdesk.worldbank.org/knowledgebase/articles/889392>
- **FMI** — DataMapper : <https://www.imf.org/external/datamapper/api/help>
- **FRED** — St. Louis Fed : <https://fred.stlouisfed.org/docs/api/fred/>

> Les codes pays suivent la norme **ISO 3166-1 alpha-3**, commune à la Banque
> mondiale et au FMI.
