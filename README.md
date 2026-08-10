# Atlas Commerce — Dashboard de pilotage des ventes (Projet Streamlit 2026)

Dashboard Streamlit complet : filtres géographiques en cascade, KPIs,
répartition par catégorie/région, top clients, profil démographique,
évolution mensuelle, carte des ventes par État, prévisions à 6 mois et
export CSV.

**Équipe** — Alpha Oumar Diallo, Rokhaya Beye, Abdourahmane Ndiaye,
Mourtalla Guye, Serigne Saliou Mbacké

## 1. Installation

```bash
git clone https://github.com/Alpha-vsc/Atlas-Commerce-dashboard.git
cd Atlas-Commerce-dashboard
pip install -r requirements.txt
```

> ⚠️ Le fichier de données (`ventes_enriched.csv`, ~55 Mo) est suivi
> avec **Git LFS**. Installe-le avant de cloner pour récupérer le
> vrai fichier (sinon tu n'auras qu'un pointeur texte) :
> ```bash
> git lfs install
> ```
> Si tu as cloné avant d'avoir installé LFS, rattrape avec :
> ```bash
> git lfs pull
> ```

## 2. Données

Le dépôt contient déjà `ventes_enriched.csv`, généré à partir du jeu
de données complet du cours (`donnees_ventes_etudiants.csv`,
286 392 lignes) via `prepare_data_real.py`. **Rien à faire de plus**
pour lancer l'app — les données sont prêtes.

Si vous devez régénérer ce fichier (nouvelles données, colonnes
modifiées...), le script original est fourni :

```bash
python prepare_data_real.py donnees_ventes_etudiants.csv ventes_enriched.csv
```

Cela va :
- renommer/aligner les colonnes sur le schéma attendu (`Order_id`,
  `Cust_id`, `Full_name`, `Order_Date`, `Order_Status`, `Category`,
  `Region`, `State_Code`, `State_Complet`, `City`, `Country`, `Gender`,
  `Age`, `Total`, `Month_Year`, `Latitude`/`Longitude`...)
- reconstruire le nom complet des états à partir du code à 2 lettres
  (`State_Complet`, ex. `CA` → `California`)
- ajouter les coordonnées lat/long par État pour la carte bonus
- retirer les colonnes sensibles (SSN, e-mail, téléphone...) qui ne
  sont pas nécessaires au dashboard

## 3. Lancer l'app

```bash
streamlit run app.py
```

## 4. Personnalisation

Tout en haut de `app.py` :

```python
TEAM_MEMBERS = ["Alpha Oumar Diallo", "Rokhaya Beye", "Abdourahmane Ndiaye", "Mourtalla Guye", "Serigne Saliou Mbacké"]
CLIENT_NAME = "Atlas Commerce Inc."
```

Ces valeurs alimentent automatiquement l'en-tête et le pied de page
du dashboard.

## 5. Notes techniques

- La carte (section 8) charge son fond de carte depuis le CDN de
  Plotly — une connexion internet est nécessaire pour l'afficher,
  comme pour toute carte web (Google Maps, Power BI Maps, etc.).
- Le module de prévision (Holt-Winters, `statsmodels`) a besoin d'au
  moins 8 mois de données dans la période sélectionnée pour s'activer.
- Les filtres Région → State → Country → City sont en cascade : les
  options de chaque filtre dépendent des filtres précédents. Le bouton
  "Réinitialiser les filtres" vide toute la sélection.
- Le CSV complet (286k lignes) reste fluide grâce au cache
  `@st.cache_data` sur le chargement des données.

## 6. Structure des fichiers

```
.
├── app.py                  # L'application Streamlit
├── prepare_data_real.py    # Script de préparation des données réelles
├── ventes_enriched.csv     # Données complètes (286 392 lignes, suivi via Git LFS)
├── requirements.txt
├── .gitignore
├── .streamlit/config.toml  # Thème sombre (fond, couleur d'accent...)
└── README.md
```