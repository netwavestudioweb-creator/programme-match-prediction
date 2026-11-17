import pandas as pd

# Liste des championnats
championships = ['PL', 'PD', 'SA', 'BL1', 'L1']

# Fusionner les données pour chaque championnat
for champ in championships:
    df_football_data = pd.read_csv(f'data_next_match_football_data_{champ}.csv')
    df_api_football = pd.read_csv(f'data_next_match_api_football_{champ}.csv')
    
    # Fusionner les données
    data_combined = pd.merge(df_football_data, df_api_football, left_on='homeTeam', right_on='teams', how='left')
    
    # Sauvegarder les données combinées
    data_combined.to_csv(f'data_next_match_combined_{champ}.csv', index=False)
