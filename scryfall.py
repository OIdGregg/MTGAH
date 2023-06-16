import requests

class Scryfall:
    API_URL = 'https://api.scryfall.com/cards/search'

    def search(self, query):
        response = requests.get(self.API_URL, params={'q': query})
        response.raise_for_status()  # raise exception if invalid response
        return response.json().get('data', [])
