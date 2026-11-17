import requests

def download_page(url, filename):
    try:
        # Envoi de la requête HTTP
        response = requests.get(url)
        
        # Vérifie que la requête a réussi
        if response.status_code == 200:
            # Écriture du contenu HTML dans un fichier
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f"Page téléchargée avec succès et sauvegardée dans '{filename}'.")
        else:
            print(f"Erreur lors de la récupération de la page {url} : {response.status_code}")
    except Exception as e:
        print(f"Une erreur est survenue pour {url} : {e}")

# Liste des URL et des noms de fichiers
urls = [
    ('https://www.sofascore.com/tournament/football/england/premier-league/17#id:61627', 'premier_league.html'),
    ('https://www.sofascore.com/tournament/football/spain/laliga/8#id:61643', 'la_liga.html'),
    ('https://www.sofascore.com/tournament/football/germany/bundesliga/35#id:63516', 'bundesliga.html'),
    ('https://www.sofascore.com/tournament/football/france/ligue-1/34#id:61736', 'ligue_1.html'),
    ('https://www.sofascore.com/tournament/football/italy/serie-a/23#id:63515', 'serie_a.html')
]

# Télécharge chaque page
for url, filename in urls:
    download_page(url, filename)
