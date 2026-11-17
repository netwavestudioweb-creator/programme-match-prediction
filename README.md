# ⚽ Programme Match — Prédicteur de statistiques

Prédit le **nombre de corners, fautes et cartons** d'un match à venir, à partir de la **forme récente** des deux équipes.

> Projet d'**Adriano DODO**. Version reconstruite (`predicteur_stats.py`).

---

## 🎯 Ce que fait le prédicteur

Pour un match `Équipe A (domicile) vs Équipe B (extérieur)`, il estime :
- le nombre de **corners**,
- le nombre de **fautes**,
- le nombre de **cartons**.

Exemple :
```
🔮 Prédiction — Arsenal (dom.) vs Chelsea (ext.) :
   corners   : ~10.0
   fautes    : ~19.6
   cartons   : ~3.7
```

---

## 🧠 La méthode (et pourquoi la précédente ne marchait pas)

| Avant | Maintenant |
|---|---|
| Scraping HTML de sofascore (site JavaScript → impossible) | **CSV gratuits** de [football-data.co.uk](https://www.football-data.co.uk) (sans clé API) |
| Prédire le résultat à partir des stats **du match** (impossible : elles n'existent pas encore → fuite de données) | Prédire des **compteurs** à partir de variables **connues avant le match** |
| — | Forme générale (6 derniers matchs) **+ forme domicile/extérieur** (4 derniers) **+ tendance de l'arbitre** (12 derniers) |

Variables (27 au total) : pour chaque équipe, ses moyennes de corners/fautes/cartons **marqués et concédés** (en général et selon le lieu), plus les moyennes de l'arbitre.

Un modèle **Ridge** (régression linéaire régularisée) est entraîné **par cible**, évalué sur les matchs les plus récents (jamais vus à l'entraînement) et comparé à une **baseline** (prédire toujours la moyenne).

---

## 📊 Résultats (Premier League, 3 saisons, ~1140 matchs)

Erreur moyenne (MAE) sur les matchs de test, jamais vus à l'entraînement :

| Cible | MAE modèle | MAE baseline | Prévisible ? |
|---|---|---|---|
| **fautes** | **3.89** | 4.07 | ✅ oui — vrai signal |
| corners | 2.82 | 2.82 | ➖ à peine (≈ moyenne) |
| cartons | 1.72 | 1.70 | ➖ non — la moyenne fait aussi bien |

### 🔎 Conclusion honnête

- Les **fautes** sont réellement prévisibles : elles dépendent du style des équipes, qui est stable. Le modèle bat nettement la simple moyenne.
- Les **corners** le sont à peine : le modèle ne fait pas mieux que de prédire la moyenne.
- Les **cartons** ne le sont **pas** mieux que la moyenne, même en ajoutant la tendance de l'arbitre : trop d'aléatoire (un tacle, une décision).

C'est un résultat **utile en soi** : il dit *ce qu'on peut raisonnablement prédire* (les fautes) et ce qui reste dominé par le hasard (corners, cartons). Ajouter des variables bruitées n'améliore pas — au contraire. D'où le choix d'un modèle **simple et régularisé** (Ridge) plutôt qu'une forêt aléatoire qui sur-apprend.

---

## 🚀 Utilisation

### Prérequis
```bash
pip install pandas scikit-learn numpy
```

### Exemples
```bash
python predicteur_stats.py                              # Premier League
python predicteur_stats.py --ligue F1                   # Ligue 1
python predicteur_stats.py --predire "Arsenal" "Chelsea"
python predicteur_stats.py --n 8                        # forme sur 8 matchs
```

Ligues : `E0` (Premier League), `F1` (Ligue 1), `SP1` (La Liga), `I1` (Serie A), `D1` (Bundesliga).
Les données se téléchargent automatiquement dans `data/`.

---

## 🔭 Pistes pour aller plus loin

- Ajouter la **tendance de l'arbitre** (moyenne de cartons/fautes sifflés) — surtout utile pour les cartons.
- Séparer la forme **domicile / extérieur**.
- Prédire par équipe (corners de A, corners de B) plutôt que le total.

---

## 🗂️ Anciens fichiers

Les scripts d'origine (`api_calls.py`, `analyse.py`, `data_merge.py`…) correspondent à l'ancienne approche (scraping + APIs). Ils sont conservés pour mémoire mais remplacés par `predicteur_stats.py`. Les clés API qui y figuraient en clair ont été retirées (à régénérer).
