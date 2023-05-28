# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 15:24:04 2023

@author: Melanie
"""

import json
import pandas as pd
import streamlit as st
import plotly.express as px
import datetime as dt
from pytz import utc
from tzlocal import get_localzone
import io
from PIL import Image
import random
import os
import plotly.graph_objects as go
from jsonbin import load_key, save_key
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import base64

# Hintergrundfarbe auf Rot setzen
st.markdown(""" <style>.stApp {background-color: #FFC0CB;}</style>""", unsafe_allow_html=True)

# -------- load secrets for jsonbin.io --------
jsonbin_secrets = st.secrets["jsonbin"]
api_key = jsonbin_secrets["api_key"]
bin_id1 = jsonbin_secrets["bin_id1"]
bin_id2 = jsonbin_secrets["bin_id2"]
bin_id3 = jsonbin_secrets["bin_id3"]
bin_id4 = jsonbin_secrets["bin_id4"]
bin_id5 = jsonbin_secrets["bin_id5"]
bin_id6 = jsonbin_secrets["bin_id6"]

# -------- user login --------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

fullname, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == True:   # login successful
    authenticator.logout('Logout', 'main')   # show logout button
elif authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()
elif authentication_status == None:
    st.warning('Please enter your username and password')
    st.stop()

# Setzen des Titels
st.title("BDdoc")

# Anzeigen des Untertitels in kleinerer Schriftgröße und anderem Stil
st.subheader("Überblick über deine Blutdruckwerte")

# Profilbild hochladen
st.sidebar.subheader("Profil")
file = st.sidebar.file_uploader("👤 Profilbild auswählen", type=["jpg", "jpeg", "png"])

# Falls ein Bild hochgeladen wurde, dieses anzeigen und speichern
if file is not None:
    image = Image.open(file)
    st.sidebar.image(image, caption="Dein Profilbild", use_column_width=True)

    # Base64-Codierung des Bilds
    profile_picture_data = base64.b64encode(file.read()).decode('utf-8')

    # Speichern des Bilds in der JSON-Bin
    save_key(api_key, bin_id1, username, profile_picture_data)

# Profile Manager erstellen
profile_manager = ProfileManager(api_key, bin_id2)

# Sidebar mit Profilformular
name = st.sidebar.text_input("Name")
geburtsdatum = st.sidebar.date_input("Geburtsdatum")
geschlecht = st.sidebar.selectbox("Geschlecht", ["", "männlich", "weiblich", "divers"])
gewicht = st.sidebar.text_input("Gewicht [kg]")
krankheiten = st.sidebar.text_input("Krankheiten")

# JSON-Objekt mit Profildaten
profil = {
    "name": name,
    "geburtsdatum": str(geburtsdatum),
    "geschlecht": geschlecht,
    "gewicht": gewicht,
    "krankheiten": krankheiten.split(", ")
}

# Laden vorhandener Profile
names = [address["name"] for address in profile_manager.address_list]

# Überprüfen, ob das aktuelle Benutzerprofil in der JSON-Bin existiert
if name in names:
    st.sidebar.success("Profil gefunden")
    existing_profile = next((address for address in profile_manager.address_list if address["name"] == name), None)
    # Formularfelder mit vorhandenen Profildaten ausfüllen
    if existing_profile is not None:
        name = st.sidebar.text_input("Name", existing_profile["name"])
        geburtsdatum = st.sidebar.date_input("Geburtsdatum", dt.datetime.strptime(existing_profile["geburtsdatum"], "%Y-%m-%d").date())
        geschlecht = st.sidebar.selectbox("Geschlecht", ["", "männlich", "weiblich", "divers"], existing_profile["geschlecht"])
        gewicht = st.sidebar.text_input("Gewicht [kg]", existing_profile["gewicht"])
        krankheiten = st.sidebar.text_input("Krankheiten", ", ".join(existing_profile["krankheiten"]))

        # Profildaten in der JSON-Bin aktualisieren
        existing_profile["name"] = name
        existing_profile["geburtsdatum"] = str(geburtsdatum)
        existing_profile["geschlecht"] = geschlecht
        existing_profile["gewicht"] = gewicht
        existing_profile["krankheiten"] = krankheiten.split(", ")

        profile_manager.update_profile(existing_profile)
else:
    st.sidebar.warning("Profil nicht gefunden")
    if st.sidebar.button("Profil erstellen"):
        # Neues Profil zur JSON-Bin hinzufügen
        profile_manager.create_profile(profil)
        st.sidebar.success("Profil erstellt")

# Weitere Streamlit-Code hier einfügen (z. B. Anzeige des Profils)


# Dummy-Daten
systolic = "-"

diastolic = "-"

# Erstelle einen Button zum Verbinden mit einem Bluetooth-Gerät
connect_button = st.button("Verbinde mit Blutdruckgerät ❤️")

if connect_button:
 st.write("Erfolgreich verbunden")

 # Simuliere das Empfangen von Daten vom Bluetooth-Gerät
 # Ersetze dies durch deinen tatsächlichen Code zum Empfangen von Daten
 systolic = 120
 diastolic = 80

# Funktion zum Anzeigen der zuletzt gespeicherten Blutdruckmessung
def show_last_blood_pressure(address_list):
    if len(address_list) > 0:
        last_measurement = address_list[-1]
        st.subheader("Letzte Blutdruckmessung")
        st.write("Systolischer Wert: {}".format(last_measurement["systolic_bp"]))
        st.write("Diastolischer Wert: {}".format(last_measurement["diastolic_bp"]))
    else:
        st.subheader("Keine gespeicherte Blutdruckmessung")

# Laden der gespeicherten Blutdruckdaten aus der JSON-Bin
address_list = load_key(api_key, bin_id2, username)

# Aufruf der Funktion zur Anzeige der zuletzt gespeicherten Blutdruckmessung
show_last_blood_pressure(address_list)

# Eingabefeld für den systolischen Blutdruck in mmHg
systolic_bp = st.number_input("Systolischer Blutdruck (mmHg):", step=1, format="%d")

# Eingabefeld für den diastolischen Blutdruck in mmHg
diastolic_bp = st.number_input("Diastolischer Blutdruck (mmHg):", step=1, format="%d")

# Schaltfläche zum Speichern der Daten
if st.button("Daten speichern"):
    # Speichern der Daten nur, wenn beide Werte eingegeben wurden
    if systolic_bp is not None and diastolic_bp is not None:
        # Daten aktualisieren
        data = {
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp
        }

        # Daten in der JSON-Bin speichern
        address_list.append(data)
        save_key(api_key, bin_id2, username, address_list)


# Zufällige Blutdruckwerte generieren
dates = pd.date_range(start='2022-01-01', end='2022-12-31', freq='D')
sbp_values = [random.randint(90, 200) for _ in range(len(dates))]
dbp_values = [random.randint(50, 120) for _ in range(len(dates))]

df = pd.DataFrame({'Datum': dates, 'Systolischer BD': sbp_values, 'Diastolischer BD': dbp_values})

# Titel
st.subheader('Blutdruckverlauf')
# Dropdown-Menü für die Auswahl des Zeitraums
time_range = st.selectbox('Ansicht:', ('Woche', 'Monat'))

# Daten nach ausgewähltem Zeitraum gruppieren
if time_range == 'Woche':
    df_grouped = df.groupby(pd.Grouper(key='Datum', freq='D')).mean().reset_index()
    df_grouped['Wochentag'] = df_grouped['Datum'].dt.strftime('%A')
    df_grouped = df_grouped.groupby('Wochentag').mean().reset_index()
    df_grouped['Datum'] = df_grouped['Wochentag']
else:
    df_grouped = df.groupby(pd.Grouper(key='Datum', freq='MS')).mean().reset_index()
    df_grouped['Datum'] = df_grouped['Datum'].dt.strftime('%Y-%m-%d')

# Gruppierte Daten als JSON-String speichern
json_data = df_grouped.to_json(orient='records')

# Daten mit save_key() Funktion speichern
res = save_key(api_key, bin_id3, username, json_data)


# Linienchart mit Plotly Express erstellen
fig_line = px.line(df_grouped, x='Datum', y=['Systolischer BD', 'Diastolischer BD'])
fig_line.update_layout(xaxis_title='Datum', yaxis_title='Blutdruck (mmHg)')

# Balkendiagramm mit Plotly erstellen
fig_bar = go.Figure(data=[go.Bar(x=df_grouped['Datum'], y=df_grouped['Systolischer BD'], name='Systolischer BD'),
                          go.Bar(x=df_grouped['Datum'], y=df_grouped['Diastolischer BD'], name='Diastolischer BD')])
fig_bar.update_layout(barmode='group', xaxis_title='Datum', yaxis_title='Blutdruck (mmHg)')

# Ansicht auswählen und entsprechende Chart anzeigen
chart_type = st.selectbox('Chart-Typ:', ('Liniendiagramm', 'Balkendiagramm'))
if chart_type == 'Liniendiagramm':
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.plotly_chart(fig_bar, use_container_width=True)


# Normalwert definieren
normalwerte = {"Systolisch": [0, 120], "Diastolisch": [0, 80]}

# Definiere Hypertonie Einteilung
hypertonie = {

    "Hypotonie": [0, 90],

    "Normal": [91, 119],

    "Hypertonie Grad 1": [120, 139],

    "Hypertonie Grad 2": [140, 179],

    "Hypertonie Grad 3": [180, 1000]

}

# Anzeigen der Normalwerte
st.subheader(" Normalwerte (mmHg)")

for key, value in normalwerte.items():

    st.write(key + ": " + str(value[0]) + " - " + str(value[1]))

# Anzeigen der Hypertonie Einteilung
st.subheader(" Hypertonie Einteilung (mmHg)")

for key, value in hypertonie.items():

    st.write(key + ": " + str(value[0]) + " - " + str(value[1]))

# Titel hinzufügen
st.subheader("Notizen")

# Notizen-Box
eingabe_notizen = st.text_area("Notizen hier eingeben:", value="", key="notizen_input")

# Speichern der Notizen nur wenn der Benutzer eine Eingabe gemacht hat
if st.button("Notiz speichern"):
    if eingabe_notizen:
        # Daten als JSON-Objekt formatieren
        data = {'notizen': eingabe_notizen.split('\n')}

        # Daten mit save_key() Funktion speichern
        save_key(api_key, bin_id4, username, data)

        # Aktualisierte Notizen laden
        address_data = load_key(api_key, bin_id4, username)
        notizen = address_data.get('notizen', [])
            
# Laden der aktuellen Notizen
address_data = load_key(api_key, bin_id4, username)
notizen = address_data.get('notizen', [])

# Aktuelle Notizen anzeigen
st.write("Aktuelle Notizen:")
st.write('\n'.join(notizen))

# Löschfunktion definieren
def delete_notes():
    # Daten mit leerem Notizen-Text speichern
    empty_data = {'notizen': []}
    save_key(api_key, bin_id4, username, empty_data)

    # Aktualisierte Notizen laden
    address_data = load_key(api_key, bin_id4, username)
    notizen.clear()
    notizen.extend(address_data.get('notizen', []))

    # Aktuelle Notiz entfernen
    eingabe_notizen = ""

# Schaltfläche zum Löschen der Notizen
if st.button("Notizen löschen"):
    # Löschfunktion aufrufen
    delete_notes()



# Funktion zum Laden der Termindaten aus der JSON-Bin
def load_termine(api_key, bin_id5):
    data = load_key(api_key, bin_id5, 'termine', empty_value=[])
    df = pd.DataFrame(data)
    return df

# Funktion zum Speichern der Termindaten in der JSON-Bin
def save_termine(api_key, bin_id5, df):
    data = df.to_dict(orient='records')
    save_key(api_key, bin_id5, 'termine', data)

# Streamlit-Anwendung
def main():
    st.subheader("Terminkalender")
  
    
    # Laden der Termindaten
    df = load_termine(api_key, bin_id5)
    
    # Eingabefelder für den neuen Termin
    neuer_termin = st.text_input('Neuer Termin:', '')
    neues_datum = st.date_input('Datum:', dt.date.today())
    neue_uhrzeit = st.time_input('Uhrzeit:', dt.time(9, 0))
    
    if st.button('Termin hinzufügen'):
        neue_zeit = dt.datetime.combine(neues_datum, neue_uhrzeit)
        neue_uhrzeit = neue_zeit.strftime('%H:%M')
        neue_termin = {
            'Termin': neuer_termin,
            'Datum': neues_datum.strftime('%Y-%m-%d'),
            'Uhrzeit': neue_uhrzeit
        }
        df = pd.concat([df, pd.DataFrame(neue_termin, index=[0])], ignore_index=True)
    
    # Tabelle mit den Terminen anzeigen
    st.table(df)
    
    # Löschbutton für hinzugefügte Termine
    delete_termine = st.button('Hinzugefügte Termine löschen')
    if delete_termine:
        df = df.iloc[:-1]  # Letzten hinzugefügten Termin entfernen
    
    # Termin-Daten speichern
    save_termine(api_key, bin_id5, df)

# Streamlit-Anwendung ausführen
if __name__ == '__main__':
    main()


# Titel der App
st.subheader('Medikamenten-Tracker')

# JSON-Datei laden oder leere DataFrame erstellen
try:
    with open('medikamente.json', 'r') as f:
        df = pd.read_json(f)
except:
    df = pd.DataFrame(columns=['Medikament', 'Einnahme_Menge', 'Uhrzeit', 'Eingenommen'])

# Funktion zur Umwandlung von lokaler Zeit in UTC
def local_to_utc(local_time):
    local_tz = get_localzone()
    utc_tz = pytz.utc
    local_time = local_tz.localize(local_time)
    utc_time = local_time.astimezone(utc_tz)
    return utc_time

# Eingabefelder für das neue Medikament
neues_medikament = st.text_input('Neues Medikament:', '')
neue_einnahme_menge = st.number_input('Einnahme-Menge:', min_value=0, step=1, value=1)
neue_uhrzeit = st.time_input('Uhrzeit:', key='meds_time_input', value=dt.time(9, 0))

# Schaltfläche zum Hinzufügen des neuen Medikaments
if st.button('Medikament hinzufügen'):
    df = df.append({
        'Medikament': neues_medikament,
        'Einnahme_Menge': neue_einnahme_menge,
        'Uhrzeit': local_to_utc(dt.datetime.combine(dt.date.today(), neue_uhrzeit)),
        'Eingenommen': False
    }, ignore_index=True)

# Tabelle mit den Medikamenten anzeigen
for i, row in df.iterrows():
    if st.checkbox(f"{row['Medikament']} um {row['Uhrzeit'].strftime('%H:%M')} Uhr eingenommen?"):
        df.at[i, 'Eingenommen'] = True
st.table(df)

if st.button('Daten speichern', key=str(dt.datetime.now())):
    # Die Daten in ein Dictionary umwandeln
    data = df.to_dict(orient='records')

    # JSON-Datei öffnen und Daten schreiben
    with open('medikamente.json', 'w') as f:
        json.dump(data, f)

    st.success('Daten wurden erfolgreich gespeichert.')


# Medikamentendaten in JSON-Bin speichern
data = df.to_dict(orient='records')
save_key(api_key, bin_id6, 'medikamente', data)


