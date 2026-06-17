import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import json

# ── 1. CARICAMENTO MATERIALE E PULIZIA──────────────────────────────────────────────
df = pd.read_csv("07_Marvel_DC_Comic_Characters.csv")

# qui voglio solo le colonne utili 
cols = ["name", "ALIGN", "SEX", "EYE", "HAIR", "ID", "ALIVE", "APPEARANCES", "publisher"]
df = df[cols].dropna()

# Teniamo solo personaggi con almeno 20 apparizioni (più famosi e significativi)
df = df[df["APPEARANCES"] >= 100].copy()


df["ALIGN"] = df["ALIGN"].replace({
    "Reformed Criminals": "Neutral Characters"
})

# qua creo una fascia di popolarità in base al numero di apparizioni
df["POPULARITY"] = pd.cut(
    df["APPEARANCES"],
    bins=[0, 50, 200, 500, 99999],
    labels=["Bassa", "Media", "Alta", "Leggenda"]
)

print(f"Personaggi nel dataset pulito: {len(df)}")
print(df["ALIGN"].value_counts())

# ── 2. ENCODING ────────────────────────────────────────────────────────
feature_cols = ["ALIGN", "SEX", "EYE", "HAIR", "ID", "ALIVE", "publisher", "POPULARITY"]
encoders = {}

for col in feature_cols:
    le = LabelEncoder()
    df[col + "_enc"] = le.fit_transform(df[col].astype(str))
    encoders[col] = le

# ── 3. ADDESTRAMENTO DEL MODELLO ───────────────────────────────────────────
X = df[[c + "_enc" for c in feature_cols]].values
y = df["name"].values

model = DecisionTreeClassifier(max_depth=20, min_samples_leaf=1, random_state=667)
model.fit(X, y)

# ── 4. IN QUESTO PUNTO STO SALVANDO TUTTE COSE ───────────────────────────────────────────────────
joblib.dump(model, "model.pkl")
joblib.dump(encoders, "encoders.pkl")

# questa parte è importante per il form di streamlit. 
options = {}
for col in feature_cols:
    options[col] = sorted(df[col].astype(str).unique().tolist())

with open("options.json", "w") as f:
    json.dump(options, f, ensure_ascii=False, indent=2)

print("\n✅ model.pkl, encoders.pkl e options.json salvati!")
print("Valori per colonna:")
for k, v in options.items():
    print(f"  {k}: {v}")