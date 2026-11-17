import pandas as pd
from sklearn.linear_model import LinearRegression

# Demander à l'utilisateur quel championnat analyser
championship = input('Pour quel championnat souhaitez-vous analyser les données ? (PL, PD, SA, BL1, L1) ')
data_combined = pd.read_csv(f'data_next_match_combined_{championship}.csv')

# Demander à l'utilisateur quelle équipe analyser
team = input('Quelle équipe souhaitez-vous analyser ? ')

# Filtrer les données pour l'équipe choisie
data_team = data_combined[(data_combined['homeTeam'] == team) | (data_combined['awayTeam'] == team)]

# Vérifier que des données sont disponibles
if data_team.empty:
    print(f"Aucune donnée disponible pour l'équipe {team} dans le championnat {championship}.")
else:
    # Sélectionner les colonnes pertinentes pour la prédiction
    X = data_team[['fautes_A', 'fautes_B', 'corners_A', 'corners_B', 'possessions_A', 'possessions_B']]
    y = data_team['résultat']

    # Créer le modèle de régression linéaire
    model = LinearRegression()
    model.fit(X, y)

    # Prédire les résultats pour le prochain match
    y_pred = model.predict(X)
    data_team['predicted_result'] = y_pred

    # Afficher les résultats des prédictions
    print(data_team[['homeTeam', 'awayTeam', 'predicted_result']])
    
    # Sauvegarder les résultats des prédictions
    data_team.to_csv('predictions.csv', index=False)
