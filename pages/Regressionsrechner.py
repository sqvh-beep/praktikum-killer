import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sympy as sp
import math
import scienceplots


def round_up(k, decimals = 0):
        multiplier = 10 ** decimals
        return math.ceil(k * multiplier) / multiplier

st.set_page_config(layout="wide")

st.title("Regressionsrechner")

uploaded_file = st.file_uploader("Lade deine CSV-Datei hoch", type=["CSV"])
st.divider()

if uploaded_file is not None:

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

    st.success("Regression ist bereit.")

    tauschen = st.checkbox("Spalten tauschen (sehr cursed, wenn man es nicht braucht)")

    if tauschen:
        x = df[df.columns[1]].values
        y = df[df.columns[0]].values
    else:
        x = df[df.columns[0]].values
        y = df[df.columns[1]].values
    
    
    try:
        y_err = df[df.columns[2]].values
    except IndexError:
        y_err = None

    if 'lets_rock_clicked' not in st.session_state:
        st.session_state['lets_rock_clicked'] = False


    col1, col2 = st.columns(2)
    with col1:
        Grad = int(st.number_input("Grad der Regression (1=linear, 2=quadratisch, etc.):", step=1))
        if Grad < 1:
            st.warning("Der Grad sollte größer als 0 sein!")
        elif Grad > len(x)-2:
            st.warning(f"Dieser Grad führt zu Overfitting und ist daher nicht möglich!")

        rd = int(st.number_input("Wie viel soll gerundet werden? (Nachkommastellen):", step=1))
        var_x = st.text_input("Variable für x", "x")
        e_x = st.text_input("Einheit für x", "x_e")
        var_y = st.text_input("Variable für y", "y")
        e_y = st.text_input("Einheit für y", "y_e")    

    if st.button("Lets Rock!", type="primary", icon="🎈"):
        st.session_state['lets_rock_clicked'] = True

    if st.session_state['lets_rock_clicked'] and Grad < len(x)-1:
        st.balloons()
        with col2:

            # Datenauswertung
            p = np.polyfit(x, y, deg=Grad, cov=True)
            c = p[0]
            c_r = np.round(c, rd)
            f = np.sqrt(np.diag(p[1]))

            # Formelbauer
            formel_latex = fr"{var_y}({var_x}) = ({c[0]} \pm {f[0]}) \cdot {var_x}^{{{Grad}}}"
            for i,n in zip(range(1,Grad+1), reversed(range(0,Grad+1))):
                if n-1 == 0:
                    formel_latex += fr"+ ({c[i]} \pm {f[i]})"
                elif n-1 == 1:
                    formel_latex += fr"+ ({c[i]} \pm {f[i]}) \cdot {var_x}"
                else:
                    formel_latex += fr"+ ({c[i]} \pm {f[i]}) \cdot {var_x}^{{{n-1}}}"

            formel_latex_rounded = fr"{var_y}({var_x}) \approx ({c_r[0]} \pm {round_up(f[0], rd)}) \cdot {var_x}^{{{Grad}}}"
            for i,n in zip(range(1,Grad+1), reversed(range(0,Grad+1))):
                if n-1 == 0:
                    formel_latex_rounded += fr"+ ({c_r[i]} \pm {round_up(f[i], rd)})"   
                elif n-1 == 1:
                    formel_latex_rounded += fr"+ ({c_r[i]} \pm {round_up(f[i], rd)}) \cdot {var_x}"
                else:
                    formel_latex_rounded += fr"+ ({c_r[i]} \pm {round_up(f[i], rd)}) \cdot {var_x}^{{{n-1}}}"
            

            # Plotter

            plt.style.use(['science', 'grid'])

            x_Achse = np.array(x)
            y_Achse = np.array(y)

            x_fit = np.linspace(min(x), max(x), 1000)    
            y_fit = np.polyval(c, x_fit)

            #Größe Plot etc.
            fig, ax = plt.subplots(figsize=(8,6))

            ax.errorbar(x_Achse, y_Achse, yerr=y_err,
                        fmt='x', color='red', ecolor='black', capsize=3,
                        label='Messwerte inkl. Fehler')
            
            ax.plot(x_fit, y_fit, color='blue', linestyle='--',
                    label=f'Fit: ${formel_latex_rounded}$')
            
            ax.set_xlabel(f"${var_x}$ in {e_x}")
            ax.set_ylabel(f"${var_y}$ in {e_y}")

            ax.set_title('Plot der Regression')

            ax.legend()
            plt.tight_layout()
            st.pyplot(fig)

        # Formelausgabe
        st.divider()

        st.subheader("Gerundete Formel:")
        st.latex(formel_latex_rounded)
        st.code(formel_latex_rounded)

        st.subheader("Ungerundete Formel:")
        st.latex(formel_latex)
        st.code(formel_latex)
    




