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
from PIL import Image
from datetime import datetime

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

st.title("BDdoc")
st.subheader("Überblick über deine Blutdruckwerte")

# Hintergundbildfarbe auf rot ändern
st.markdown(""" <style>.stApp {background-color: #FFC0CB;}</style>""",
 unsafe_allow_html=True)


import streamlit as st
import json
from datetime import date

# Laden der vorhandenen Profildaten aus der JSON-Bin
profil = load_key(api_key, bin_id1, 'profil', empty_value={})

# Sidebar with profile form
name = st.sidebar.text_input("Name", profil.get("name", ""))


geburtsdatum = st.sidebar.text_input("Geburtsdatum", profil.get("geburtsdatum", ""))


geschlecht_options = ["", "männlich", "weiblich", "divers"]
geschlecht = st.sidebar.selectbox("Geschlecht", geschlecht_options, index=geschlecht_options.index(profil.get("geschlecht", "")))


gewicht = st.sidebar.text_input("Gewicht [kg]", profil.get("gewicht", ""))


krankheiten = st.sidebar.text_input("Krankheiten", ", ".join(profil.get("krankheiten", [])))


# JSON object with profile data
profil = {
    "name": name,
    "geburtsdatum": str(geburtsdatum),
    "geschlecht": geschlecht,
    "gewicht": gewicht,
    "krankheiten": krankheiten.split(", ")
}

# Profildaten in der JSON-Bin speichern
res = save_key(api_key, bin_id1, 'profil', profil)




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
        st.write("Systolischer Wert: {}".format(last_measurement["Systolischer BD"]))
        st.write("Diastolischer Wert: {}".format(last_measurement["Diastolischer BD"]))
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
        # Aktuelles Datum erfassen
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Daten aktualisieren
        data = {
            "Datum": current_date,
            "Systolischer BD": systolic_bp,
            "Diastolischer BD": diastolic_bp
        }

        # Daten in der JSON-Bin speichern
        address_list.append(data)
        save_key(api_key, bin_id2, username, address_list)


# Funktion zum Erzeugen des Blutdruckverlaufs
def generate_blood_pressure_chart(address_list):
    # Datenrahmen für den Blutdruckverlauf erstellen
    df = pd.DataFrame(address_list)

    # Linienchart mit Plotly Express erstellen
    fig_line = px.line(df, x='Datum', y=['Systolischer BD', 'Diastolischer BD'])
    fig_line.update_layout(xaxis_title='Datum', yaxis_title='Blutdruck (mmHg)')

    # Balkendiagramm mit Plotly erstellen
    fig_bar = go.Figure(data=[go.Bar(x=df['Datum'], y=df['Systolischer BD'], name='Systolischer BD'),
                              go.Bar(x=df['Datum'], y=df['Diastolischer BD'], name='Diastolischer BD')])
    fig_bar.update_layout(barmode='group', xaxis_tickformat='%Y-%m-%d', xaxis_title='Datum', yaxis_title='Blutdruck (mmHg)')

    # Ansicht auswählen und entsprechende Chart anzeigen
    chart_type = st.selectbox('Chart-Typ:', ('Liniendiagramm', 'Balkendiagramm'))
    if chart_type == 'Liniendiagramm':
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.plotly_chart(fig_bar, use_container_width=True)


# Aufruf der Funktion zum Erzeugen des Blutdruckverlaufs
generate_blood_pressure_chart(address_list)




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

# Streamlit-Anwendung
def main():
    st.subheader("Medikamenten-Tracker")   

# Laden der vorhandenen Daten aus der JSON-Bin
data = load_key(api_key, bin_id6, 'medikamente', empty_value=[])

# Eingabefelder für das neue Medikament
neues_medikament = st.text_input('Neues Medikament:', '')
neue_einnahme_menge = st.number_input('Einnahme-Menge:', min_value=0, step=1, value=1)
neue_uhrzeit = st.time_input('Uhrzeit:', key='meds_time_input', value=dt.time(9, 0))

# Schaltfläche zum Hinzufügen des neuen Medikaments
if st.button('Medikament hinzufügen'):
    # Neuen Datensatz erstellen
    neuer_datensatz = {
        'Medikament': neues_medikament,
        'Einnahme_Menge': neue_einnahme_menge,
        'Uhrzeit': neue_uhrzeit.strftime('%H:%M'),
        'Eingenommen': False
    }
    # Daten mit save_key() Funktion speichern
    data.append(neuer_datensatz)
    res = save_key(api_key, bin_id6, 'medikamente', data)


# DataFrame erstellen
df = pd.DataFrame(data)

# Tabelle mit den Medikamenten anzeigen
for i, row in df.iterrows():
    eingenommen = st.checkbox(row['Medikament'] + ' um ' + row['Uhrzeit'] + ' Uhr eingenommen?', value=row['Eingenommen'])
    df.at[i, 'Eingenommen'] = eingenommen

# Schaltfläche zum Löschen einer Eingabe
if st.button('Eingabe löschen'):
    # Dropdown-Menü zum Auswählen der zu löschenden Eingabe anzeigen
    ausgewählte_eingabe = st.selectbox('Eingabe auswählen:', df['Medikament'])
    # Eingabe aus dem DataFrame entfernen
    df = df[df['Medikament'] != ausgewählte_eingabe]
    # Daten mit save_key() Funktion aktualisieren
    data = df.to_dict(orient='records')
    res = save_key(api_key, bin_id6, 'medikamente', data)




st.table(df)




