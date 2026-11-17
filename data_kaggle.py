# data_kaggle.py
import os

import pandas as pd

# Chemins relatifs au dossier du script (plus de chemin absolu codé en dur).
BASE = os.path.dirname(os.path.abspath(__file__))

# Charger les données Kaggle
data_kaggle = pd.read_csv(os.path.join(BASE, "S2324-laliga-players.csv"))

# Sauvegarder les données prétraitées si nécessaire
data_kaggle.to_csv(os.path.join(BASE, "data_kaggle_prepared.csv"), index=False)
