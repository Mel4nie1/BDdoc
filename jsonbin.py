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


def load_key(api_key, bin_id, key, empty_value):
    headers = {
        'X-Master-Key': api_key
    }
    url = f'https://api.jsonbin.io/b/{bin_id}/latest'
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if key in data:
            return data[key]
    
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


