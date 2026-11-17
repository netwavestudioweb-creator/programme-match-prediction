#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programme Match — Prédicteur de statistiques (corners / fautes / cartons)
========================================================================

Prédit le NOMBRE de corners, fautes et cartons d'un match à venir, à partir de
variables connues AVANT le match :
  - la forme récente de chaque équipe (6 derniers matchs, toutes compétitions),
  - sa forme spécifique à domicile / à l'extérieur (4 derniers),
  - la TENDANCE de l'arbitre (moyenne de cartons/fautes/corners sur ses 12
    derniers matchs) — surtout utile pour prédire les cartons.

On n'utilise JAMAIS les stats du match à prédire comme entrée (pas de fuite de
données). Données : football-data.co.uk (CSV gratuits, sans clé API).

Usage :
    python predicteur_stats.py
    python predicteur_stats.py --ligue F1
    python predicteur_stats.py --predire "Arsenal" "Chelsea"
    python predicteur_stats.py --predire "Arsenal" "Chelsea" --arbitre "M Oliver"
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DOSSIER = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DOSSIER, "data")

LIGUES = {"E0": "Premier League", "F1": "Ligue 1", "SP1": "La Liga",
          "I1": "Serie A", "D1": "Bundesliga"}
SAISONS = ["2223", "2324", "2425"]

CIBLES = {
    "corners": lambda r: r["HC"] + r["AC"],
    "fautes":  lambda r: r["HF"] + r["AF"],
    "cartons": lambda r: r["HY"] + r["AY"] + r["HR"] + r["AR"],
}

N_FORME = 6      # forme générale
N_LIEU = 4       # forme à domicile / extérieur
N_ARBITRE = 12   # fenêtre pour la tendance de l'arbitre


# --------------------------- Données ---------------------------
def telecharger(ligue: str) -> None:
    os.makedirs(DATA, exist_ok=True)
    for saison in SAISONS:
        chemin = os.path.join(DATA, f"{ligue}_{saison}.csv")
        if os.path.exists(chemin):
            continue
        url = f"https://www.football-data.co.uk/mmz4281/{saison}/{ligue}.csv"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            data = urllib.request.urlopen(req, timeout=30).read()
            with open(chemin, "wb") as f:
                f.write(data)
            print(f"  téléchargé : {ligue}_{saison}.csv")
        except Exception as e:
            print(f"  ⚠️  {ligue}_{saison} indisponible ({e})")


def charger(ligue: str) -> pd.DataFrame:
    telecharger(ligue)
    frames = []
    for saison in SAISONS:
        chemin = os.path.join(DATA, f"{ligue}_{saison}.csv")
        if os.path.exists(chemin):
            frames.append(pd.read_csv(chemin, encoding="utf-8-sig"))
    if not frames:
        raise SystemExit("❌ Aucune donnée disponible.")
    df = pd.concat(frames, ignore_index=True)

    besoin = ["Date", "HomeTeam", "AwayTeam", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR"]
    df = df.dropna(subset=besoin)
    if "Referee" not in df.columns:
        df["Referee"] = "?"
    df["Referee"] = df["Referee"].fillna("?")
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    for c in ["HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR"])


# --------------------------- Features ---------------------------
def stats_equipe(r, cote: str) -> dict:
    soi, adv = ("H", "A") if cote == "H" else ("A", "H")
    return {
        "corners_pour": r[soi + "C"], "corners_contre": r[adv + "C"],
        "fautes_pour": r[soi + "F"], "fautes_contre": r[adv + "F"],
        "cartons_pour": r[soi + "Y"] + r[soi + "R"], "cartons_contre": r[adv + "Y"] + r[adv + "R"],
    }


def totaux_match(r) -> dict:
    return {"corners": r["HC"] + r["AC"], "fautes": r["HF"] + r["AF"],
            "cartons": r["HY"] + r["AY"] + r["HR"] + r["AR"]}


def _moy(hist: list, n: int):
    if len(hist) < n:
        return None
    recent = hist[-n:]
    return {k: float(np.mean([h[k] for h in recent])) for k in recent[0]}


def nouvel_etat() -> dict:
    return {"all": {}, "domicile": {}, "exterieur": {}, "arbitre": {},
            "arb_somme": {"corners": 0.0, "fautes": 0.0, "cartons": 0.0}, "arb_n": 0}


def construire_features(etat: dict, dom: str, ext: str, arbitre: str):
    """Renvoie un dict de features, ou None si l'historique général manque."""
    mh = _moy(etat["all"].get(dom, []), N_FORME)
    ma = _moy(etat["all"].get(ext, []), N_FORME)
    if mh is None or ma is None:
        return None

    mh_lieu = _moy(etat["domicile"].get(dom, []), N_LIEU) or mh
    ma_lieu = _moy(etat["exterieur"].get(ext, []), N_LIEU) or ma

    feat = {}
    for k, v in mh.items():       feat["dom_" + k] = v
    for k, v in ma.items():       feat["ext_" + k] = v
    for k, v in mh_lieu.items():  feat["domLieu_" + k] = v
    for k, v in ma_lieu.items():  feat["extLieu_" + k] = v

    # Tendance de l'arbitre (sinon moyenne courante de la ligue)
    arb = etat["arbitre"].get(arbitre, [])
    if len(arb) >= 3:
        for k in ("corners", "fautes", "cartons"):
            feat["arb_" + k] = float(np.mean([a[k] for a in arb[-N_ARBITRE:]]))
    else:
        n = max(etat["arb_n"], 1)
        for k in ("corners", "fautes", "cartons"):
            feat["arb_" + k] = etat["arb_somme"][k] / n
    return feat


def maj_etat(etat: dict, r) -> None:
    dom, ext, arbitre = r["HomeTeam"], r["AwayTeam"], r["Referee"]
    etat["all"].setdefault(dom, []).append(stats_equipe(r, "H"))
    etat["all"].setdefault(ext, []).append(stats_equipe(r, "A"))
    etat["domicile"].setdefault(dom, []).append(stats_equipe(r, "H"))
    etat["exterieur"].setdefault(ext, []).append(stats_equipe(r, "A"))
    t = totaux_match(r)
    etat["arbitre"].setdefault(arbitre, []).append(t)
    for k in ("corners", "fautes", "cartons"):
        etat["arb_somme"][k] += t[k]
    etat["arb_n"] += 1


def construire_dataset(df: pd.DataFrame):
    etat = nouvel_etat()
    lignes, y = [], {k: [] for k in CIBLES}
    for _, r in df.iterrows():
        feat = construire_features(etat, r["HomeTeam"], r["AwayTeam"], r["Referee"])
        if feat is not None:
            lignes.append(feat)
            for cible, fonc in CIBLES.items():
                y[cible].append(fonc(r))
        maj_etat(etat, r)
    X = pd.DataFrame(lignes)
    return X, {k: np.array(v) for k, v in y.items()}, etat


# --------------------------- Modèle ---------------------------
def entrainer_et_evaluer(X, y_dict):
    coupe = int(len(X) * 0.8)
    modeles = {}
    print(f"\n📊 Évaluation (entraînement {coupe} matchs, test {len(X) - coupe}) :\n")
    print(f"{'Cible':<10}{'MAE modèle':>12}{'MAE baseline':>14}")
    for cible, y in y_dict.items():
        Xtr, Xte, ytr, yte = X[:coupe], X[coupe:], y[:coupe], y[coupe:]
        # Ridge (régression linéaire régularisée) : plus stable que la forêt
        # aléatoire sur ces données bruitées, et aussi bon ou meilleur.
        modele = Ridge(alpha=10.0)
        modele.fit(Xtr, ytr)
        mae = mean_absolute_error(yte, modele.predict(Xte))
        mae_base = mean_absolute_error(yte, np.full_like(yte, ytr.mean(), dtype=float))
        print(f"{cible:<10}{mae:>12.2f}{mae_base:>14.2f}   {'✅' if mae < mae_base else '➖'}")
        modele.fit(X, y)
        modeles[cible] = modele
    return modeles


def predire(modeles, etat, colonnes, dom, ext, arbitre):
    feat = construire_features(etat, dom, ext, arbitre or "?")
    if feat is None:
        print(f"❌ Pas assez d'historique pour {dom} ou {ext}.")
        return
    X = pd.DataFrame([feat]).reindex(columns=colonnes, fill_value=0)
    arb_txt = f" — arbitre : {arbitre}" if arbitre else ""
    print(f"\n🔮 Prédiction — {dom} (dom.) vs {ext} (ext.){arb_txt} :")
    for cible, modele in modeles.items():
        print(f"   {cible:<10}: ~{modele.predict(X)[0]:.1f}")


def main():
    parser = argparse.ArgumentParser(description="Prédicteur de stats de match (corners/fautes/cartons).")
    parser.add_argument("--ligue", default="E0", choices=list(LIGUES))
    parser.add_argument("--predire", nargs=2, metavar=("DOMICILE", "EXTERIEUR"))
    parser.add_argument("--arbitre", default=None, help="Nom de l'arbitre (optionnel, améliore les cartons)")
    args = parser.parse_args()

    print(f"🏟️  {LIGUES[args.ligue]} — forme {N_FORME} matchs, lieu {N_LIEU}, arbitre {N_ARBITRE}")
    df = charger(args.ligue)
    print(f"   {len(df)} matchs ({df['Date'].min():%d/%m/%Y} → {df['Date'].max():%d/%m/%Y})")

    X, y, etat = construire_dataset(df)
    print(f"   {len(X)} matchs exploitables — {X.shape[1]} variables par match")

    modeles = entrainer_et_evaluer(X, y)

    if args.predire:
        predire(modeles, etat, X.columns, args.predire[0], args.predire[1], args.arbitre)
    else:
        print("\n💡 Exemple : python predicteur_stats.py --predire \"Arsenal\" \"Chelsea\" --arbitre \"M Oliver\"")


if __name__ == "__main__":
    main()
