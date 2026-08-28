import streamlit as st
import pandas as pd
import numpy as np
import math

st.header("Standard-Fehlerrechner")

file = st.file_uploader("Lade eine CSV Datei hoch", type=["CSV"])
st.divider()

if file:

    df = pd.read_csv(file)
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