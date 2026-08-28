import streamlit as st
import sympy as sp
from sympy import latex
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
import pandas as pd
import math
import io
import csv

# Funktionen
def latify(equation:str) -> str:
    return latex(sp.sympify(equation))
def round_up(k, decimals = 0):
    multiplier = 10 ** decimals
    return math.ceil(k * multiplier) / multiplier 

# Titel etc
st.title("Plotter für Messwerte")
st.set_page_config(layout="wide")

# Spaltendefinition (Spalte1=einstellungen, Spalte2=plot)
col_1, col_2 = st.columns(2)

#Platzvariablen
X = None
Y = None

var_x = 'x'
var_y = "y"

# Einstellungsspalte
with col_1:
    #title
    st.subheader("CSV Upload")

    
    csvf = st.file_uploader("Lade deine Messdaten hoch", type=["CSV"])

    if csvf:
        # --------------------------------------- CSV READER S (CHATGPT)--------------------------------------------------
        raw_data = csvf.read()
        
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



    # plot customizer
    name = st.text_input("Name des Plots")
    x_label = st.text_input("Label X")
    y_Label = st.text_input("Label Y")
    var_x = st.text_input("Gebe deine $x$-Variable an ($t$, $m$, $f$, etc.)")
    var_y = st.text_input("Gebe deine $y$-Variable an ($A$, $F$, $R$, etc.)")
    if var_x == "x" or var_x == "":
        fkt = st.text_input(f"Gib eine Funktion zum Plotten ein (deine Variable ist $x$):")
        var_x = 'x'
    else:
        fkt = st.text_input(f"Gib eine Funktion zum Plotten ein (deine Variable ist ${var_x}$):")
    

    # csv knaller // options für messwerte
    with st.expander("Plot von Messwerten"):
        if csvf:
            n_spalten = len(df.iloc[0])
            st.write(df)
            st.write("Gebe die Spalten an die geplottet werden sollen")

            #Achsendefinition
            X = st.number_input("Spaltenzahl für $x$-Values", min_value=1, max_value=n_spalten, step=1)
            Y = st.number_input("Spaltenzahl für $y$-Values", min_value=1, max_value=n_spalten, step=1)
            st.divider()
            fehler = st.checkbox("Willst $y$-Fehler Plotten?")
            if fehler:
                y_err = st.number_input("Spaltenzahl für $y$-Fehler", min_value=1, max_value=n_spalten, step=1)
                st.divider()
            else:
                y_error = None

            # more options
            regression = st.checkbox("Regression Plotten")
            if regression:
                deg = st.number_input("Gebe den Grad der Regression an", min_value=1, step=1, max_value=5)
                rd = st.number_input("Gebe die Rundung an", min_value=0, step=1)
                st.divider()
            loglog = st.checkbox("LogLog-Scale")
            histo = st.checkbox("Histogramm darstellung")

            #calc
        else:
            st.warning("Lade erst eine CSV Datei hoch")
        

    # Achsendefinition2
    if csvf:
        x_Achse = df[df.columns[X-1]].values
        y_Achse = df[df.columns[Y-1]].values
        if fehler:
            y_error = df[df.columns[y_err-1]].values

        
    # Limits
    with st.expander("Grenzeinstellungen"):
        # x-Achse
        x_limits = st.checkbox("$x$-Grenzen?")
        if x_limits:
            under_x = st.number_input("Untere $x$-Grenze")
            upper_x = st.number_input("Obere $x$-Grenze")
        else:
            if csvf:
                under_x = x_Achse[0]
                upper_x = x_Achse[-1]
            else:
                under_x = 0
                upper_x = 10
        x_fit = np.linspace(under_x, upper_x, 1000)

        # Y limits
        y_limits = st.checkbox("$y$-Grenzen?")
        if y_limits:
            under_y = st.number_input("Untere $y$-Grenze")
            upper_y = st.number_input("Obere $y$-Grenze")
        else:
            upper_y = None
            under_y = None

    #calculator
    # regression calc
    if csvf and regression and deg is not None:
        r_matrix = np.polyfit(x_Achse, y_Achse, deg=deg, cov=True)
        slope = r_matrix[0]
        slope_rd = np.round(slope, rd)
        f = np.sqrt(np.diag(r_matrix[1])) 

        #formula
        if deg == 1:
            formel_latex_rounded = fr"{var_y}({var_x}) \approx ({slope_rd[0]} \pm {round_up(f[0], rd)}) \cdot {var_x}"
        else:
            formel_latex_rounded = fr"{var_y}({var_x}) \approx ({slope_rd[0]} \pm {round_up(f[0], rd)}) \cdot {var_x}^{{{deg}}}"
        for i,n in zip(range(1,deg+1), reversed(range(0,deg+1))):
            if n-1 == 0:
                formel_latex_rounded += fr"+ ({slope_rd[i]} \pm {round_up(f[i], rd)})"   
            elif n-1 == 1:
                formel_latex_rounded += fr"+ ({slope_rd[i]} \pm {round_up(f[i], rd)}) \cdot {var_x}"
            else:
                formel_latex_rounded += fr"+ ({slope_rd[i]} \pm {round_up(f[i], rd)}) \cdot {var_x}^{{{n-1}}}"
    

    # Plot
    plt.style.use(['science', 'grid'])    
    fig, ax = plt.subplots(figsize=(8,6))
    ax.set_title(name)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_Label)

    # Messwerte Plot
    if csvf:
        try:
            ax.errorbar(x_Achse, y_Achse, 
                        yerr=y_error, fmt='x', 
                        color='red', ecolor='black', 
                        capsize=3, label='Messwerte inkl. Fehler')
        except ValueError:
            st.warning("Dies ist unmöglich die Fehlerspalte, da negative Werte gefunden wurden!")

    # Funktionenplot
    if fkt:
        funke = sp.parse_expr(fkt, transformations='all')
        f_numpy = sp.lambdify(sp.symbols(var_x), funke, 'numpy')
        y_xis = f_numpy(x_fit)
        plt.plot(x_fit, y_xis, label=fr'${latify(funke)}$')

    # fit plot
    if csvf:
        if loglog:
            ax.loglog(x_Achse, y_Achse, label='LogLog-Scale Plot der Messwerte')    
        if histo:
            pass
        if regression:
            if deg is not None:
                reg_fit = np.polyval(slope, x_fit)
                ax.plot(x_fit, reg_fit, color='blue', linestyle='--',
                        label=f'Fit: ${formel_latex_rounded}$')

# Outputspalte
with col_2:
    ax.legend()
    if fkt or csvf:
        st.subheader("Plot")
        st.pyplot(fig)
        if not X is None and not Y is None and X==Y:
            st.warning(fr"$x$ und $y$ Spaltenzahl stimmen überein, du plottest gerade $z$ gegen $z$ ($z \in header(CSV)$)")
        if csvf and regression:
                if deg is not None:
                    st.subheader(fr"$\LaTeX$-Formel")
                    st.latex(formel_latex_rounded)
                    st.code(formel_latex_rounded)
