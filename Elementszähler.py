import streamlit as st
import pandas as pd
import numpy as np
import csv
import io

st.title("Elementszähler")
st.text("Dieses Tool dient zur Auszählung von verschieden Elementen einer CSV-Datei deren Häufigkeit")

st.divider()

st.subheader("Lade deine CSV-Datei hoch")

file = st.file_uploader("Lade deine CSV hoch", type='CSV')

st.divider()

col_1, col_2 = st.columns(2)


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

    n = len(df.iloc[0])
    spalten = df.columns.tolist()

    

    for i, x in zip(range(0,n), spalten):
        zahlen_array = df[df.columns[i]].values

        einzelne_zahlen, anzahl = np.unique(zahlen_array, return_counts=True)

        with col_1:
            st.write("Alleinige Zahlen:", einzelne_zahlen)

        with col_2:
            st.write("Häufigkeit dazu: ", anzahl)

        st.divider()
        häufigkeiten_dict = dict(zip(einzelne_zahlen.tolist(), anzahl.tolist()))

        st.write(häufigkeiten_dict)
