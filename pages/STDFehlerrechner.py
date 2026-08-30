import streamlit as st
import pandas as pd
import numpy as np
import math
import csv
import io

st.header("Standard-Fehlerrechner")

file = st.file_uploader("Lade eine CSV Datei hoch", type=["CSV"])
st.divider()

if file:
    # --------------------------------------- CSV READER S (CHATGPT)--------------------------------------------------
    raw_data = file.read()
    
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
        df = pd.read_csv(io.StringIO(text_data), sep=sep, on_bad_lines='skip', decimal=',')
    except pd.errors.EmptyDataError:
        st.error("Die hochgeladene Datei ist leer.")
        st.stop()
    except Exception as e:
        st.error(f"Unbekannter Fehler beim Lesen der CSV: {e}")
        st.stop()
    # --------------------------------------- CSV READER E (CHATGPT)--------------------------------------------------



    anzeigen = st.checkbox("Tabelle Anzeigen", value=True)
    if anzeigen:
        st.write(df)

    n = len(df.iloc[0])
    spalten = df.columns.tolist()

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Standardabweichungen")
        for i,x in zip(range(0,n), spalten):
            try:
                st.write(fr"STD für '{x}':")
                st.code(np.std(df[df.columns[i]].values))
                st.divider()
            except TypeError:
                st.warning("Dies ist eine Liste mit Strings und funktioniert somit nicht")
                st.divider()
    with col2:  
        st.subheader("Mittelwerte")
        for i,x in zip(range(0,n), spalten):
            try:
                st.write(fr"MEAN für '{x}'")
                st.code(np.mean(df[df.columns[i]].values))
                st.divider()
            except TypeError:
                st.warning("Dies ist eine Liste mit Strings oder Sonderzeichen und funktioniert somit nicht")
                st.divider()
