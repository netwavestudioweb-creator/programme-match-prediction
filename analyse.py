from bs4 import BeautifulSoup
import pandas as pd

def extract_match_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        
        # Exemple de récupération des données des matchs (à adapter selon la structure HTML des pages)
        matches = soup.find_all('div', class_='Box dsHhBj sc-30651487-0 kgwpFk')  # Remplacer 'match' par la classe ou le tag approprié
        
        data = []
        for match in matches:
            # Extraire les informations sur les équipes et les statistiques
            try:
                team1 = match.find('div', class_='team1').text.strip()
                team2 = match.find('div', class_='team2').text.strip()
                stats = match.find('div', class_='__NEXT_DATA__')  # Remplacer 'stats' par la classe ou le tag approprié
                
                if stats:
                    fouls_team1 = stats.find('span', class_='fouls_team1').text.strip()
                    fouls_team2 = stats.find('span', class_='fouls_team2').text.strip()
                    yellow_cards_team1 = stats.find('span', class_='yellow_cards_team1').text.strip()
                    yellow_cards_team2 = stats.find('span', class_='yellow_cards_team2').text.strip()
                    corners_team1 = stats.find('span', class_='corners_team1').text.strip()
                    corners_team2 = stats.find('span', class_='corners_team2').text.strip()
                    
                    data.append({
                        'team1': team1,
                        'team2': team2,
                        'fouls_team1': fouls_team1,
                        'fouls_team2': fouls_team2,
                        'yellow_cards_team1': yellow_cards_team1,
                        'yellow_cards_team2': yellow_cards_team2,
                        'corners_team1': corners_team1,
                        'corners_team2': corners_team2
                    })
            except Exception as e:
                print(f"Une erreur est survenue lors de l'extraction des données : {e}")
                
        return data

def save_to_excel(data, output_filename):
    df = pd.DataFrame(data)
    df.to_excel(output_filename, index=False, engine='openpyxl')

def main():
    filenames = [
        'premier_league.html',
        'la_liga.html',
        'bundesliga.html',
        'ligue_1.html',
        'serie_a.html'
    ]
    
    all_data = []
    
    for filename in filenames:
        print(f"Extraction des données pour {filename}...")
        match_data = extract_match_data(filename)
        all_data.extend(match_data)
        
    save_to_excel(all_data, 'matches_data.xlsx')
    print("Données enregistrées dans 'matches_data.xlsx'.")

if __name__ == "__main__":
    main()
