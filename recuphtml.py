import requests

# URL de la page que tu veux récupérer
url = 'https://www.sofascore.com/'

# Envoi de la requête HTTP
response = requests.get(url)

# Vérifie que la requête a réussi
if response.status_code == 200:
    # Sauvegarde le contenu HTML dans un fichier
    with open('page.html', 'w', encoding='utf-8') as file:
        file.write(response.text)
    print("Le code HTML de la page a été sauvegardé dans 'page.html'.")
else:
    print(f"Erreur lors de la récupération de la page : {response.status_code}")
