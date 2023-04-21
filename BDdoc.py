# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 15:24:04 2023

@author: Melanie
"""

import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import datetime as dt
import pytz
from tzlocal import get_localzone
import io
from PIL import Image
import random
import os
import plotly.graph_objects as go


# Setzen des Titels und Untertitels
st.set_page_config(page_title="BDdoc - Überblick über deine Blutdruckwerte",
                   page_icon=":pill:",
                   layout="wide")
st.title("BDdoc")
st.subheader("Überblick über deine Blutdruckwerte")

# Hintergundbildfarbe auf rot ändern
st.markdown(""" <style>.stApp {background-color: #FFC0CB;}</style>""",
 unsafe_allow_html=True)

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

# JSON-Datei mit Profildaten speichern
with open("profil.json", "w") as f:
    json.dump(profil, f)

# JSON-Datei mit Profildaten laden
with open("profil.json", "r") as f:
    profil = json.load(f)


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

# Daten aus der Datei laden
with open("BD.json", "r") as f:

 data = json.load(f)

# Daten aus der Datei laden
with open("BD.json", "r") as f:
 data = json.load(f)


# Eingabefeld für den systolischen Blutdruck in mmHg
systolic_bp = st.number_input("Systolischer Blutdruck (mmHg):", step=1, format="%d")

# Eingabefeld für den diastolischen Blutdruck in mmHg
diastolic_bp = st.number_input("Diastolischer Blutdruck (mmHg):", step=1, format="%d")

# Daten aktualisieren
data["systolic_bp"] = systolic_bp
data["diastolic_bp"] = diastolic_bp

# Daten als JSON in Datei schreiben
with open("BD.json", "w") as f:
 json.dump(data, f)

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

# Gruppierte Daten als JSON-Datei speichern
json_data = df_grouped.to_json(orient='records')

with open('diagramm.json', 'w') as f:
    json.dump(json_data, f)


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
notizen = st.text_area("Notizen hier eingeben:")

# Schaltfläche zum Speichern der Notizen
if st.button("Notizen speichern"):
   # Daten als JSON-Objekt formatieren
   data = {'notizen': notizen.split('\n')}

   # JSON-Objekt in Datei schreiben
   with open('notizen.json', 'a') as f:
       json.dump(data, f)

   st.success("Notizen gespeichert!")

   # Löschfunktion definieren
   def delete_notes():
       # JSON-Datei leeren
       with open('notizen.json', 'w') as f:
           json.dump({'notizen': []}, f)
       # Erfolgsmeldung anzeigen
       st.success("Notizen gelöscht!")
       # Textarea zurücksetzen
       return ''

   # Schaltfläche zum Löschen der Notizen
   if st.button("Notizen löschen"):
       # Löschfunktion aufrufen
       notizen = delete_notes()

# Notizen-Box anzeigen
st.write("Aktuelle Notizen:")
st.write(notizen)

# Titel hinzufügen
st.subheader("Terminkalender")

# JSON-Dateipfad
json_path = 'termine.json'

# Wenn die JSON-Datei existiert, laden Sie die Termine
if os.path.isfile(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data)
# Ansonsten ein leeres DataFrame initialisieren
else:
    df = pd.DataFrame(columns=['Termin', 'Datum', 'Uhrzeit'])

# Eingabefelder für den neuen Termin
neuer_termin = st.text_input('Neuer Termin:', '')
neues_datum = st.date_input('Datum:', dt.date.today())
neue_uhrzeit = st.time_input('Uhrzeit:', dt.time(9, 0))

# Schaltfläche zum Hinzufügen des neuen Termins
if st.button('Termin hinzufügen'):
    neue_zeit = dt.datetime.combine(neues_datum, neue_uhrzeit)
    neue_uhrzeit = neue_zeit.strftime('%H:%M')
    df = df.append({
        'Termin': neuer_termin,
        'Datum': neues_datum.strftime('%Y-%m-%d'),
        'Uhrzeit': neue_uhrzeit
    }, ignore_index=True)

# Tabelle mit den Terminen anzeigen
st.table(df)

# Termin-Daten im JSON-Format speichern
if st.button('Daten speichern'):
    # Die Daten in ein Dictionary umwandeln
    data = df.to_dict(orient='records')
    # JSON-Datei öffnen und Daten schreiben
    with open(json_path, 'w') as f:
        json.dump(data, f)
    st.success('Daten wurden erfolgreich gespeichert.')


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
    if st.checkbox(row['Medikament'] + ' um ' + row['Uhrzeit'].strftime('%H:%M') + ' Uhr eingenommen?'):
        df.at[i, 'Eingenommen'] = True
st.table(df)

if st.button('Daten speichern', key=str(dt.datetime.now())):
    

# Termin-Daten im JSON-Format speichern
  if st.button('Daten speichern'):
    # Die Daten in ein Dictionary umwandeln
    data = df.to_dict(orient='records')
    
    # JSON-Datei öffnen und Daten schreiben
    with open('medikamente.json', 'w') as f:
        json.dump(data, f)
        
    st.success('Daten wurden erfolgreich gespeichert.')
