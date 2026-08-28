import streamlit as st
import pandas as pd
import sympy as sp
import math
import numpy as np
import openpyxl

st.set_page_config(layout="wide")

st.title("Transformierung der Messwerte")
st.text("Transformiere deine Spalten für deine Messwerte, indem du Rechenoperationen für die jeweilige Spalte auswählst.", text_alignment="center")

uploaded_file = st.file_uploader("Lade deine CSV- oder Excel-Datei hoch", type=["CSV", "xlsx"])
st.divider()

col1, col2, col3 = st.columns(3)

if not uploaded_file == None:
    try:
        df = pd.read_excel(uploaded_file)
        df1 = df.copy()
    except ValueError:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            df1 = df.copy()
        except UnicodeDecodeError:
            uploaded_file.seek(0) 
            df = pd.read_csv(uploaded_file, encoding='latin-1', sep=';')
            df1 = df.copy()

        for n in df1.columns:
            try:
                df1[n] = pd.to_numeric(df1[n].str.replace(",", ".", regex=False))
            except AttributeError:
                pass


    with col1:

        anzahl = st.number_input("Gebe die Spaltenzahl an, die transformiert werden soll: (Hinweis: Du kannst nicht deine Fehlerspalte transformieren (siehe Fehleraddierer))", min_value=1, max_value=len(df.iloc[0]), step=1)

        new = df1[df1.columns[anzahl-1]]

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
        st.write(df1)

    with col3:

        z = new

        st.subheader("Transformierte Liste")
        if selection == "Addition":
            z = transformation + z
        elif selection == "Multiplikation":
            z = transformation * z
        
        if not fehlerspalte == "":
            y = df1[df1.columns[fehlerspalte-1]]
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
        
        df1[spalte] = z

        if 'y' in locals():
            df1[header[fehlerspalte-1]] = y

        with col3:
            st.write(df1)

            def convert_for_download(df1):
                return df1.to_csv(index=False).encode("utf-8")

            csv = convert_for_download(df1)

            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=fr"{uploaded_file.name}_transformed.csv",
                mime="text/csv",
                icon=":material/download:",
            )
    