import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_match_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Exemple d'extraction des matchs (à adapter selon la structure du site)
        matches = soup.find_all('div', class_='match-class')  # Remplace 'match-class' par la classe appropriée
        match_data = []

        for match in matches:
            date_str = match.find('div', class_='date-class').text  # Remplace 'date-class' par la classe appropriée
            date = datetime.strptime(date_str, '%d %b %Y %H:%M')
            if date.weekday() in [4, 5, 6]:  # Vérifie si le match est entre vendredi et lundi
                team1 = match.find('div', class_='team1-class').text  # Remplace 'team1-class' par la classe appropriée
                team2 = match.find('div', class_='team2-class').text  # Remplace 'team2-class' par la classe appropriée
                score = match.find('div', class_='score-class').text  # Remplace 'score-class' par la classe appropriée
                statistics = match.find('div', class_='stats-class').text  # Remplace 'stats-class' par la classe appropriée
                predictions = match.find('div', class_='predictions-class').text  # Remplace 'predictions-class' par la classe appropriée

                match_data.append({
                    'date': date,
                    'team1': team1,
                    'team2': team2,
                    'score': score,
                    'statistics': statistics,
                    'predictions': predictions
                })

        return match_data
    else:
        print(f"Erreur lors de la récupération de la page : {response.status_code}")
        return []

# URLs des championnats (à mettre à jour avec les bonnes URLs)
urls = {
    'Premier League': 'https://www.sofascore.com/tournament/football/england/premier-league/17#id:61627',  # Exemple d'URL
    'La Liga': 'https://www.sofascore.com/tournament/football/spain/laliga/8#id:61643',  # Exemple d'URL
    'Bundesliga': 'https://www.sofascore.com/tournament/football/germany/bundesliga/35#id:63516',  # Exemple d'URL
    'Ligue 1': 'https://www.sofascore.com/tournament/football/france/ligue-1/34#id:61736',  # Exemple d'URL
    'Serie A': 'https://www.sofascore.com/tournament/football/italy/serie-a/23#id:63515'  # Exemple d'URL
}

# Extraction des données pour chaque championnat
for league, url in urls.items():
    print(f"Collecte des données pour {league}")
    match_data = get_match_data(url)
    for data in match_data:
        print(data)
