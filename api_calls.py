import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# Clés API — lues depuis l'environnement (jamais codées en dur).
# Définissez-les avant de lancer : FOOTBALL_DATA_API_KEY, API_FOOTBALL_KEY
api_key_football_data = os.environ.get('FOOTBALL_DATA_API_KEY', '')
api_key_api_football = os.environ.get('API_FOOTBALL_KEY', '')

if not api_key_football_data or not api_key_api_football:
    raise SystemExit(
        "❌ Clés API manquantes. Définissez les variables d'environnement "
        "FOOTBALL_DATA_API_KEY et API_FOOTBALL_KEY (voir README).")

# URLs des APIs
url_football_data = 'https://api.football-data.org/v4/competitions/{}/matches'
url_api_football = 'https://v3.football.api-sports.io/fixtures'

# Date actuelle et la semaine suivante en UTC
today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
next_week = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

# Liste des IDs des championnats (Football-Data.org)
championship_ids = {
    'PL': 'PL',      # Premier League
    'PD': 'PD',      # La Liga
    'SA': 'SA',      # Serie A
    'BL1': 'BL1',    # Bundesliga
    'L1': 'L1'       # Ligue 1
}

# Fonction pour obtenir le prochain match pour un championnat donné
def get_next_match(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    # Afficher la réponse complète pour debug
    print("Réponse API:", data)
    
    if 'matches' in data:
        # Filtrer les matchs pour la période entre aujourd'hui et une semaine plus tard
        upcoming_matches = [
            match for match in data['matches']
            if today <= match['utcDate'] <= next_week
        ]
        
        if upcoming_matches:
            # Retourner le match le plus proche
            next_match = min(upcoming_matches, key=lambda x: x['utcDate'])
            return next_match
        else:
            print("Aucun match dans la période spécifiée.")
            return None
    else:
        print("Aucune donnée de match disponible ou mauvais format de réponse.")
        return None

# Récupérer et sauvegarder les données pour chaque championnat
for champ, champ_id in championship_ids.items():
    # Football-Data.org
    url = url_football_data.format(champ_id)
    next_match = get_next_match(url, {'X-Auth-Token': api_key_football_data})
    if next_match:
        df_football_data = pd.DataFrame([next_match])
        df_football_data.to_csv(f'data_next_match_football_data_{champ}.csv', index=False)

    # API-Football
    params = {
        'season': 2024,  # Saison 2024/2025
        'league': champ_id,
        'from': today,  # Filtrer à partir d'aujourd'hui
        'to': next_week  # Jusqu'à la semaine prochaine
    }
    next_match_api = get_next_match(url_api_football, {
        'x-rapidapi-key': api_key_api_football,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }, params)
    if next_match_api:
        df_api_football = pd.DataFrame([next_match_api])
        df_api_football.to_csv(f'data_next_match_api_football_{champ}.csv', index=False)
