# Atlas Commerce — Dashboard de pilotage des ventes (Projet Streamlit 2026)

Dashboard Streamlit complet : filtres géographiques en cascade, KPIs,
répartition par catégorie/région, top clients, profil démographique,
évolution mensuelle, carte des ventes par État, prévisions à 6 mois et
export CSV.

## 1. Installation

```bash
pip install -r requirements.txt
```

## 2. Données

Deux fichiers sont fournis :

- **`ventes_enriched.csv`** — un jeu de données de démo (3 000 lignes,
  échantillon) déjà prêt à l'emploi. Il permet de lancer l'app
  immédiatement pour tester / présenter.
- **`prepare_data_real.py`** — le script à lancer **une fois** sur ton
  vrai fichier `donnees_ventes_etudiants.csv` (85 Mo, 286 392 lignes)
  pour générer le `ventes_enriched.csv` complet avec toutes les
  colonnes attendues par `app.py` :

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

Remplace ensuite le `ventes_enriched.csv` de démo par celui généré à
partir du fichier complet (même nom de fichier, `app.py` n'a rien à
changer).

## 3. Lancer l'app

```bash
streamlit run app.py
```

## 4. Personnalisation avant la présentation

Tout en haut de `app.py` :

```python
TEAM_MEMBERS = ["Étudiant 1", "Étudiant 2", "Étudiant 3", "Étudiant 4"]
CLIENT_NAME = "Atlas Commerce Inc."
```

Remplace par les vrais noms de l'équipe et, si besoin, un nom de
client fictif pour la mise en scène "rapport commandé par un client".

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
├── ventes_enriched.csv     # Données prêtes à l'emploi (démo/sample)
├── requirements.txt
├── .streamlit/config.toml  # Thème sombre (fond, couleur d'accent...)
└── README.md
```
