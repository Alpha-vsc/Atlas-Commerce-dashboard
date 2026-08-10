
import sys
import pandas as pd
import numpy as np

IN_PATH = sys.argv[1] if len(sys.argv) > 1 else "donnees_ventes_etudiants.csv"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "ventes_enriched.csv"

print(f"Lecture de {IN_PATH} ...")
df = pd.read_csv(IN_PATH, low_memory=False)
print(f"  -> {len(df):,} lignes, {df.shape[1]} colonnes".replace(",", " "))


# Mapping code état (2 lettres) -> nom complet, + centroïdes pour
# la carte bonus (State est déjà abrégé dans ce dataset : AK, AL, AZ...)

abbrev_to_state = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "PR": "Puerto Rico", "VI": "Virgin Islands", "GU": "Guam", "AS": "American Samoa",
}

state_centroids = {
    "AL": (32.806671, -86.791130), "AK": (61.370716, -152.404419), "AZ": (33.729759, -111.431221),
    "AR": (34.969704, -92.373123), "CA": (36.116203, -119.681564), "CO": (39.059811, -105.311104),
    "CT": (41.597782, -72.755371), "DE": (39.318523, -75.507141), "DC": (38.897438, -77.026817),
    "FL": (27.766279, -81.686783), "GA": (33.040619, -83.643074), "HI": (21.094318, -157.498337),
    "ID": (44.240459, -114.478828), "IL": (40.349457, -88.986137), "IN": (39.849426, -86.258278),
    "IA": (42.011539, -93.210526), "KS": (38.526600, -96.726486), "KY": (37.668140, -84.670067),
    "LA": (31.169546, -91.867805), "ME": (44.693947, -69.381927), "MD": (39.063946, -76.802101),
    "MA": (42.230171, -71.530106), "MI": (43.326618, -84.536095), "MN": (45.694454, -93.900192),
    "MS": (32.741646, -89.678696), "MO": (38.456085, -92.288368), "MT": (46.921925, -110.454353),
    "NE": (41.125370, -98.268082), "NV": (38.313515, -117.055374), "NH": (43.452492, -71.563896),
    "NJ": (40.298904, -74.521011), "NM": (34.840515, -106.248482), "NY": (42.165726, -74.948051),
    "NC": (35.630066, -79.806419), "ND": (47.528912, -99.784012), "OH": (40.388783, -82.764915),
    "OK": (35.565342, -96.928917), "OR": (44.572021, -122.070938), "PA": (40.590752, -77.209755),
    "RI": (41.680893, -71.511780), "SC": (33.856892, -80.945007), "SD": (44.299782, -99.438828),
    "TN": (35.747845, -86.692345), "TX": (31.054487, -97.563461), "UT": (40.150032, -111.862434),
    "VT": (44.045876, -72.710686), "VA": (37.769337, -78.169968), "WA": (47.400902, -121.490494),
    "WV": (38.491226, -80.954453), "WI": (44.268543, -89.616508), "WY": (42.755966, -107.302490),
    "PR": (18.220833, -66.590149), "VI": (18.335765, -64.896335), "GU": (13.444304, 144.793732),
    "AS": (-14.270972, -170.132217),
}


# Renommage / construction des colonnes canoniques

df["Order_id"] = df["order_id"]
df["Order_Date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["Order_Status"] = df["status"].str.replace("_", " ", regex=False).str.strip().str.title()

df["Cust_id"] = pd.to_numeric(df["cust_id"], errors="coerce").astype("Int64")

# Nom complet propre "Prénom Nom" (la colonne full_name d'origine est au
# format "Nom, Prénom" issu du dataset brut)

df["Full_name"] = (
    df["First Name"].fillna("").str.strip() + " " + df["Last Name"].fillna("").str.strip()
).str.strip()
df.loc[df["Full_name"] == "", "Full_name"] = df["full_name"]

df["Gender"] = df["Gender"].map({"M": "Male", "F": "Female"}).fillna(df["Gender"])
df["Age"] = pd.to_numeric(df["age"], errors="coerce")
df["Age"] = df["Age"].fillna(df["Age"].median()).astype(int)

df["Category"] = df["category"]
df["City"] = df["City"]
df["County"] = df["County"]
df["Zip"] = df["Zip"]
df["Region"] = df["Region"]
df["Country"] = "United States"

df["State_Code"] = df["State"].str.upper().str.strip()
df["State_Complet"] = df["State_Code"].map(abbrev_to_state)
df["State_Complet"] = df["State_Complet"].fillna(df["State_Code"])  # filet de sécurité

df["Latitude"] = df["State_Code"].map(lambda c: state_centroids.get(c, (np.nan, np.nan))[0])
df["Longitude"] = df["State_Code"].map(lambda c: state_centroids.get(c, (np.nan, np.nan))[1])

df["Total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0.0)
df["Price"] = pd.to_numeric(df["price"], errors="coerce")
df["Qty"] = pd.to_numeric(df["qty_ordered"], errors="coerce")
df["Discount_Amount"] = pd.to_numeric(df["discount_amount"], errors="coerce")
df["Discount_Percent"] = pd.to_numeric(df["Discount_Percent"], errors="coerce")
df["Payment_Method"] = df["payment_method"]

df["Month_Year"] = df["Order_Date"].dt.to_period("M").dt.to_timestamp()


# Nettoyage : lignes sans date exploitable, colonnes sensibles retirées
# (SSN / e-mail / téléphone ne sont pas nécessaires au dashboard et ne
# doivent pas être diffusés, même si le dataset est synthétique)

before = len(df)
df = df.dropna(subset=["Order_Date", "State_Code"])
print(f"  -> {before - len(df):,} lignes retirées (date ou état manquant)".replace(",", " "))

FINAL_COLS = [
    "Order_id", "Order_Date", "Month_Year", "Order_Status",
    "Cust_id", "Full_name", "Gender", "Age",
    "Country", "Region", "State_Code", "State_Complet", "City", "County", "Zip",
    "Latitude", "Longitude",
    "Category", "Total", "Price", "Qty", "Discount_Amount", "Discount_Percent",
    "Payment_Method",
]
df_out = df[FINAL_COLS].copy()

df_out.to_csv(OUT_PATH, index=False)
print(f"Fichier écrit : {OUT_PATH}  ({len(df_out):,} lignes, {df_out.shape[1]} colonnes)".replace(",", " "))
print(df_out.dtypes)
print(df_out.head(5).to_string())
