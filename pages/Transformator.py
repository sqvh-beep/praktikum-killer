import streamlit as st
import pandas as pd
import sympy as sp
import math
import numpy as np
import openpyxl
import io
import csv

st.set_page_config(layout="wide")

st.title("Transformierung der Messwerte")
st.text("Transformiere deine Spalten für deine Messwerte, indem du Rechenoperationen für die jeweilige Spalte auswählst.", text_alignment="center")

uploaded_file = st.file_uploader("Lade deine CSV-Datei hoch", type=["CSV"])
st.divider()

col1, col2, col3 = st.columns(3)

if not uploaded_file is None:
    # --------------------------------------- CSV READER S (CHATGPT)--------------------------------------------------
    raw_data = uploaded_file.read()
    
    # 1. Automatisches Durchprobieren der häufigsten Encodings, damit es keine Decode-Errors gibt
    text_data = ""
    for enc in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
        try:
            text_data = raw_data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    
    # Fallback, falls alle Encodings scheitern (ignoriert kaputte Zeichen)
    if not text_data:
        text_data = raw_data.decode('utf-8', errors='replace')
        
    # 2. Automatisches Erkennen des Trennzeichens (Sniffer)
    try:
        # Schaut sich die ersten paar Tausend Zeichen an, um das Trennzeichen zu erraten
        dialect = csv.Sniffer().sniff(text_data[:4096])
        sep = dialect.delimiter
    except Exception:
        sep = ',' # Wenn er nichts erkennt, nimm Standard-Komma

    # 3. Einlesen in Pandas (on_bad_lines='skip' verhindert Abstürze bei kaputten Reihen)
    try:
        df = pd.read_csv(io.StringIO(text_data), sep=sep, on_bad_lines='skip')
    except pd.errors.EmptyDataError:
        st.error("Die hochgeladene Datei ist leer.")
        st.stop()
    except Exception as e:
        st.error(f"Unbekannter Fehler beim Lesen der CSV: {e}")
        st.stop()
    # --------------------------------------- CSV READER E (CHATGPT)--------------------------------------------------
    

    with col1:

        anzahl = st.number_input("Gebe die Spaltenzahl an, die transformiert werden soll: (Hinweis: Du kannst nicht deine Fehlerspalte transformieren (siehe Fehleraddierer))", min_value=1, max_value=len(df.iloc[0]), step=1)

        new = df[df.columns[anzahl-1]]

        selection = st.segmented_control("Transform", ["Addition", "Multiplikation"], selection_mode="single")

        Zahl = st.text_input(fr"Gebe deinen Faktor/Summanden ein (Beispiel: $100$, $\frac{{1}}{{100}}$ (1/100), $\pi$ (pi), $10^{{-9}}$ (10^(-9)), ...)")
        if Zahl == "":
            Zahl = 1
        transformation = float(sp.sympify(Zahl).evalf())

        header = list(df)
        spalte = header[anzahl-1]

        with st.expander("Mehr Transformationen"):

            more = st.radio(
                "Wähle deine Transformation (sie wird nach der Zahltransformation ausgeführt).",
                ["None", fr":rainbow[$\ln(n)$]", fr":rainbow[$\exp(n)$]", fr":rainbow[$\sin(n)$]", fr":rainbow[$\cos(n)$]", fr":rainbow[$\tan(n)$]"]
            )
        with st.expander("Fehleraddierer"):

            fehlerspalte = st.number_input("Gebe die Fehlerspalte an:", min_value=1, max_value=len(df.iloc[0]), step=1)
            s_fehler = st.text_input("Gebe deinen systematischen Fehler an:")
            if s_fehler == "":
                s_fehler = 0
            s_fehler_wert = float(sp.sympify(s_fehler).evalf())
        
            
    with col2:
        st.subheader("Inertialliste")
        st.write(df)

    with col3:

        z = new

        st.subheader("Transformierte Liste")
        if selection == "Addition":
            z = transformation + z
        elif selection == "Multiplikation":
            z = transformation * z
        
        if not fehlerspalte == "":
            y = df[df.columns[fehlerspalte-1]]
            y = np.sqrt((np.square(y) + s_fehler_wert**2))

        if more == "None":
            z = z
        if more == fr":rainbow[$\ln(n)$]":
            z = np.log(z)
        if more == fr":rainbow[$\exp(n)$]":
            z = np.exp(z)
        if more == fr":rainbow[$\sin(n)$]":
            z = np.sin(z)
        if more == fr":rainbow[$\cos(n)$]":
            z = np.cos(z)
        if more == fr":rainbow[$\tan(n)$]":
            z = np.tan(z)
        

    if 'z' in locals():
        
        df[spalte] = z

        if 'y' in locals():
            df[header[fehlerspalte-1]] = y

        with col3:
            st.write(df)

            def convert_for_download(df):
                return df.to_csv(index=False).encode("utf-8")

            csv = convert_for_download(df)

            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=fr"{uploaded_file.name}_transformed.csv",
                mime="text/csv",
                icon=":material/download:",
            )
    
