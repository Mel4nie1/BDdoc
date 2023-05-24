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

# Falls ein Bild hochgeladen wurde, dieses anzeigen
if file is not None:
    image = Image.open(io.BytesIO(file.read()))
    st.sidebar.image(image, caption="Dein Profilbild", use_column_width=True)

# Sidebar with profile form
name = st.sidebar.text_input("Name")
geburtsdatum = st.sidebar.date_input("Geburtsdatum")
geschlecht = st.sidebar.selectbox("Geschlecht", ("", "männlich", "weiblich", "divers"))
gewicht = st.sidebar.text_input("Gewicht [kg]")
krankheiten = st.sidebar.text_input("Krankheiten")

# JSON object with profile data
profil = {
    "name": name,
    "geburtsdatum": str(geburtsdatum),
    "geschlecht": geschlecht,
    "gewicht": gewicht,
    "krankheiten": krankheiten.split(", ")
}

# Load existing profiles from the JSON-Bin
address_list = load_key(api_key, bin_id1, username)

# Append or update the profile in the address_list
existing_profile = next((item for item in address_list if item["name"] == name), None)
if existing_profile:
    existing_profile.update(profil)
else:
    address_list.append(profil)

# Save the updated address_list to the JSON-Bin
save_key(api_key, bin_id1, username, address_list)


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

# Zeige den empfangenen Blutdruckwert an, wenn er verfügbar ist
if systolic is not None and diastolic is not None:
 st.subheader("Aktueller Blutdruckwert")

st.write("Systolischer Wert: {}".format(systolic))

st.write("Diastolischer Wert: {}".format(diastolic))
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

        # Daten in der JSONBin-Bin speichern
        address_list = load_key(api_key, bin_id2, username)
        address_list.append(data)
        save_key(api_key, bin_id2, username, address_list)


# Daten aus der JSONBin-Bin laden
address_list = load_key(api_key, bin_id2, username)


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

# JSON-Bin-Daten laden oder leeren DataFrame erstellen
data = load_key(api_key, bin_id6, 'medikamente', empty_value=[])
df = pd.DataFrame(data)

# Funktion zur Umwandlung von lokaler Zeit in UTC
def local_to_utc(local_time):
    local_tz = dt.timezone(dt.timedelta(hours=1))  # Lokale Zeitzone hier angeben (z.B. dt.timezone('Europe/Berlin'))
    utc_tz = pytz.timezone('UTC')
    local_time = local_tz.localize(local_time)
    utc_time = local_time.astimezone(utc_tz)
    return utc_time


# Leere Liste erstellen
data = []

# Anzahl der Medikamente
anzahl_medikamente = st.number_input('Anzahl der Medikamente:', min_value=1, step=1, value=1)

# Eingabefelder für die Medikamente
for i in range(anzahl_medikamente):
    st.write(f"Medikament {i+1}:")
    neues_medikament = st.text_input('Name:', key=f'medikament_name_{i}')
    neue_einnahme_menge = st.number_input('Einnahme-Menge:', min_value=0, step=1, value=1, key=f'medikament_menge_{i}')
    neue_uhrzeit = st.time_input('Uhrzeit:', key=f'medikament_zeit_{i}', value=dt.time(9, 0))
    
    # Schaltfläche zum Hinzufügen des Medikaments
    if st.button(f'Medikament {i+1} hinzufügen'):
        # Neue Zeile zum DataFrame hinzufügen
        data.append({
            'Medikament': neues_medikament,
            'Einnahme_Menge': neue_einnahme_menge,
            'Uhrzeit': neue_uhrzeit.strftime('%H:%M'),
            'Eingenommen': False
        })

# DataFrame erstellen
df = pd.DataFrame(data)

# Tabelle mit den Medikamenten anzeigen
for i, row in df.iterrows():
    eingenommen = st.checkbox(row['Medikament'] + ' um ' + row['Uhrzeit'] + ' Uhr eingenommen?')
    df.at[i, 'Eingenommen'] = eingenommen

st.table(df)

        


