import requests


BIN_API_URL = "https://api.jsonbin.io/v3/b"

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


# Funktion zum Laden des Profils aus der JSON-Bin
def load_profile(api_key, bin_id1):
    url = f"https://api.jsonbin.io/v3/b/{bin_id}/latest"
    headers = {
        "X-Master-Key": api_key
    }


# Funktion zum Speichern des Profils in der JSON-Bin
def save_profile(api_key, bin_id1, profile_data):
    url = f"https://api.jsonbin.io/v3/b/{bin_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key
    }
