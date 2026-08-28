import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Praktikum Auswertung")

# Titel
st.title("Praktikumstool NUMERO UNO")

# Hallo
st.header("Hallo!")
st.markdown(
        fr"""
        Dies ist dein ultimativer Praktikumsassistent. Hier findest du alle
        möglichen Tools, um dein Leben im Praktikum zu erleichtern. Von Regressionrechnern und Plottern
        bis hin zu Tools für $\LaTeX$ wie Tabellenersteller deiner Excel-Tabellen.
        Der Autor dieses gesamten Projekts ist Philipp Romhi. Für jegliche Hilfe gibt es in jedem
        einzelnen Tool einen Tutorial Guide, der dir hilft zurechtzufinden. Ansonsten solltest du selbst die Logik des Tools erfassen.
        Frohes Schaffen!
    """
    )
st.subheader("Wichtiger Hinweis")
st.markdown(
        fr"""
        Achte darauf, dass deine Daten korrekt sind und, dass vor allem das Dateiformat stimmt. Es gibt hier einen Checker unten, welcher prüft, ob deine Dateien
        für das Tool korrekt sind. Es ist wichtig diese Vorschriften einzuhalten, da sonst Fehlerhafte Ausgaben resultieren werden. Dies liegt daran, dass es in Microsoft-Office
        selbst beim gleichen Dateientyp wie .CSV mindestens 3 verschiedene Formate gibt (dasselbe gilt für .xlsx), welche in der Auswertung brutale Fehler verursachen 
        (nur Syntaxfehler, keine Sorge). Da ich dieses Exception-Handling noch machen muss (das ist so lästig), hab ich hier einen einfachen Checker gebaut, der prüft ob deine
        Dateien kompatibel sind.
    """
)
file_ex = st.file_uploader("Lade deine zu prüfende Excel-Datei hoch", type=['xlsx'])
if file_ex:
    st.text(type(file_ex))
    df = pd.read_excel(file_ex)
    st.success("Deine Datei ist funktionierend")
    