import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
import math

#Layout
st.title(fr"Tabellenbauer für $\LaTeX$")
st.markdown(
    "Hinweis: Du kannst die Daten hier im Fenster direkt editieren, aber die Header nicht. "
    "Nutze deshalb direkt in der Excel- oder CSV-Datei deine Einheit oder editiere später direkt in LaTeX. "
    "Es ist zudem hilfreich exakt dieselben Packages zu nutzen wie in dem Beispiel-Latexprotokoll auf Moodle angegeben."
)

file = st.file_uploader("Lade deine CSV- oder Excel-Tabelle hoch", type=["xlsx", "csv"], accept_multiple_files=False)
st.divider()


if file is not None:
    #Dateienimport
    try:
        lf = pd.read_excel(file)
    except ValueError:
        try:
            lf = pd.read_csv(file)
        except UnicodeDecodeError: 
            file.seek(0)
            lf = pd.read_csv(file, encoding='latin-1', sep=';')
            for n in lf.columns:
                try:
                    try:
                        lf[n] = pd.to_numeric(lf[n].str.replace(",", ".", regex=False))
                    except ValueError:
                        pass
                except AttributeError:
                    pass
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
        try:
            lf = st.data_editor(lf)
        except st.errors.StreamlitAPIException:
            st.markdown("""
                Diese Datei ist noch im Multiindex-Format (wie kannst du nur), versuche eine aktuellere
                Version der CSV Datei hochzuladen oder nutze Online Converter. 
                Du wirst merken, dass hier nur eine Spalte genutzt werden wird, sodass deine
                Tabelle einspaltig sein wird. Sorry für dieses Problem, aber lowkey verrückt wer sich dazurechtfindet.           
            """)

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
