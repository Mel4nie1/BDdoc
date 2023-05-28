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

# Funktion zum Laden der Profilbilder
def load_profile_picture(api_key, bin_id):
    response = requests.get(f"https://api.jsonbin.io/v3/b/{bin_id}/latest", headers={"X-Master-Key": api_key})
    if response.status_code == 200:
        data = response.json()
        return data.get("record", {}).get("profile_picture")
    return None

# Funktion zum Speichern der Profilbilder
def save_profile_picture(api_key, bin_id, profile_picture_data):
    data = {
        "profile_picture": profile_picture_data
    }
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key
    }
    response = requests.put(f"https://api.jsonbin.io/v3/b/{bin_id}", json=data, headers=headers)
    return response.status_code == 200


