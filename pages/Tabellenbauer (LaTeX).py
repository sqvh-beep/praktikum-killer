import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
import math
import csv
import io

#Layout
st.title(fr"Tabellenbauer für $\LaTeX$")
st.markdown(
    "Hinweis: Du kannst die Daten hier im Fenster direkt editieren, aber die Header nicht. "
    "Nutze deshalb direkt CSV-Datei deine Einheit oder editiere später direkt in LaTeX. "
    "Es ist zudem hilfreich exakt dieselben Packages zu nutzen wie in dem Beispiel-Latexprotokoll auf Moodle angegeben."
)

file = st.file_uploader("Lade deine CSV-Tabelle hoch", type=["csv"], accept_multiple_files=False)
st.divider()


if file is not None:
    #Dateienimport
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
        lf = pd.read_csv(io.StringIO(text_data), sep=sep, on_bad_lines='skip', decimal=',')
    except pd.errors.EmptyDataError:
        st.error("Die hochgeladene Datei ist leer.")
        st.stop()
    except Exception as e:
        st.error(f"Unbekannter Fehler beim Lesen der CSV: {e}")
        st.stop()
    # --------------------------------------- CSV READER E (CHATGPT)--------------------------------------------------
    
    #Variablen
    n_g = len(lf.iloc[0])
    n_w = lf.shape[0]
    spaltenzahl = "c" * n_g

    #Funktionen (zum checken der Ints)
    def round_up(k, decimals = 0):
        multiplier = 10 ** decimals
        return math.ceil(k * multiplier) / multiplier
    def int_checker(number):
        if round_up(number) == number:
            return int(number)

    #Listeneditor
    edited = st.checkbox("Liste anzeigen, oder editieren")
    if edited:
        lf = st.data_editor(lf)

    #Main-Magie
    transfer = st.button("Umwandeln", type="primary", icon="🎈") 

    if transfer:

        st.balloons()

        spalten = lf.columns.tolist()

        #Kopfspalte
        table = fr"\begin{{table}}[h] \caption{{Caption}} \label{{Tab_1}} \begin{{center}} \begin{{tabular}}" fr"{{" fr"{spaltenzahl}" fr"}}" "\n" fr"\toprule" "\n"
        for l in range(0, n_g):
            if l == n_g-1:
                table += fr" {spalten[l]}"
            else:
                table += fr" {spalten[l]} &"

        table += fr" \\" "\n" fr"\midrule " f"\n"

        #Einzelne Zahlenwerte / Strings
        for i in range(0,n_w):
            for n,z in zip(lf.iloc[i], range(0,n_g)):
                try:
                    try:
                        if z == n_g-1:
                            try:
                                if type(int_checker(n)) == int:
                                    table += fr" ${int(n)}$"
                                else: 
                                    table += fr" ${n}$"
                            except TypeError:
                                table += fr" {n}"

                        else:
                            try:
                                if type(int_checker(n)) == int:
                                    table += fr" ${int(n)}$ &"
                                else: 
                                    table += fr" ${n}$ &"
                            except TypeError:
                                table += fr" {n} &"
                    except ValueError:
                        if z == n_g-1:
                            table += fr" NONE"
                        else: 
                            table += fr" NONE &"
                except OverflowError:
                    if z == n_g-1:
                        table += fr" $\infty$"
                    else:
                        table += fr" $\infty$ &"
                    
            table += fr" \\" "\n"
        table += fr" \bottomrule \end{{tabular}} \end{{center}} \end{{table}}%"
        st.code(table)
