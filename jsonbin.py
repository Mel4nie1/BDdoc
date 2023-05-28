import requests

BIN_API_URL = r'https://api.jsonbin.io/v3/b'

def load_data(api_key, bin_id):
    """
    Gesamte Bin laden
    """
    url = f"{BIN_API_URL}/{bin_id}/latest"
    headers = {'X-Master-Key': api_key}
    res = requests.get(url, headers=headers).json()
    return res['record']


def save_data(api_key, bin_id, data):
    """
    Gesamte Bin speichern
    """
    url = f"{BIN_API_URL}/{bin_id}"
    headers = {'X-Master-Key': api_key, 'Content-Type': 'application/json'}
    res = requests.put(url, headers=headers, json=data).json()
    return res

def load_key(api_key, bin_id, key, empty_value=[]):
    """
    Schlüssel aus der Bin laden
    """
    url = f"{BIN_API_URL}/{bin_id}/latest"
    headers = {'X-Master-Key': api_key}
    res = requests.get(url, headers=headers).json()
    res = res['record']
    if key in res:
        return res[key]
    else:
        return empty_value


def save_key(api_key, bin_id, key, data):
    """
    Schlüssel in der Bin speichern
    """
    url = f"{BIN_API_URL}/{bin_id}"
    headers = {'X-Master-Key': api_key, 'Content-Type': 'application/json'}
    res = requests.get(url, headers=headers).json()
    res = res['record']
    if type(res) != dict:
        res = {key: data}  # Neues Dictionary generieren
    else:
        res[key] = data
    res = requests.put(url, headers=headers, json=res).json()
    return res


def load_notes(api_key):
    """
    Notizen aus der Bin laden
    """
    data = load_data(api_key)
    return data.get('notizen', [])


def save_notes(api_key, notes):
    """
    Notizen in der Bin speichern
    """
    data = load_data(api_key)
    data['notizen'] = notes
    return save_data(api_key, data)


def delete_notes(api_key):
    """
    Notizen aus der Bin löschen
    """
    return save_notes(api_key, [])


class ProfileManager:
    def __init__(self, api_key, bin_id):
        self.api_key = api_key
        self.bin_id = bin_id
        self.address_list = self.load_profiles()

    def load_profiles(self):
        # Laden der vorhandenen Profile aus der JSON-Bin
        address_list = []
        # Code zum Laden der Profile hier einfügen
        return address_list

    def save_profiles(self):
        # Speichern der Profile in der JSON-Bin
        # Code zum Speichern der Profile hier einfügen
        pass

    def update_profile(self, profile):
        # Aktualisieren des Profils in der JSON-Bin
        # Code zum Aktualisieren des Profils hier einfügen
        pass

    def create_profile(self, profile):
        # Hinzufügen des neuen Profils zur JSON-Bin
        # Code zum Hinzufügen des Profils hier einfügen
        pass


