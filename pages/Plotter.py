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
from scipy.optimize import curve_fit

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

ultra_plots = []
anzahl_new_plots = None

# Einstellungsspalte
with col_1:
    #title
    st.subheader("CSV Upload")
    
    csvf = st.file_uploader("Lade deine Messdaten hoch", type=["CSV"], accept_multiple_files=True)

    dataframes = []

    if csvf:
        # --------------------------------------- CSV READER S (CHATGPT)--------------------------------------------------
        namensliste = []
        for n in csvf:
            raw_data = n.read()
            
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
                st.error(f"Unbekannter Fehler beim Lesen der CSV: {n}{e}")
                st.stop()
            try:
                dataframes.append(lf)
            except:
                pass
            namensliste.append(n.name)
            # --------------------------------------- CSV READER E (CHATGPT)-------------------------------------------------


    # plot customizer
    name = st.text_input("Name des Plots")
    x_label = st.text_input("Label X")
    y_Label = st.text_input("Label Y")
    var_x = st.text_input("Gebe deine $x$-Variable an ($t$, $m$, $f$, etc.)")
    var_y = st.text_input("Gebe deine $y$-Variable an ($A$, $F$, $R$, etc.)")
    if var_y == "" or var_y == "y":
        var_y = 'y'
    if var_x == "x" or var_x == "":
        fkt = st.text_input(f"Gib eine Funktion zum Plotten ein (deine Variable ist $x$):")
        var_x = 'x'
    else:
        fkt = st.text_input(f"Gib eine Funktion zum Plotten ein (deine Variable ist ${var_x}$):")

    # csv knaller // options für messwerte

    with st.expander("Plot von Messwerten"):
        if csvf:
            for z, df in enumerate(dataframes):
                name_messung = namensliste[z]
                with st.expander(fr'Messwerte für "{name_messung}"'):
                    n_spalten = len(df.iloc[0])

                    df_shower = st.checkbox("CSV zeigen", key=z+123999999)
                    if df_shower:
                        df = st.data_editor(df) 
                    
                    anzahl_new_plots = st.number_input("Gebe an, wie viele Kurven du brauchst:", min_value=1, max_value=n_spalten, step=1, key=z+1231123)
                    
                    new_plots = []
                    regression_name = []

                    if anzahl_new_plots is not None:
                        for i in range(0,anzahl_new_plots):
                            st.divider()
                            name_plot = st.text_input("Gebe den Namen der Messung an", "Messung", key=i+z+19283178318)
                            point_or_line = st.segmented_control("Auswahl", ["Punkteplot", "Lineplot"], selection_mode="single", key=i+z+12318317009)
                            st.write("Gebe die Spalten an die geplottet werden sollen")
                            new_x_plot = st.number_input("Spaltenzahl für $x$-Values", min_value=1, max_value=n_spalten, step=1, key=i+z+1231)
                            new_y_plot = st.number_input("Spaltenzahl für $y$-Values", min_value=1, max_value=n_spalten, step=1, key =i+z+15512)
                            fehler_new = st.checkbox("Willst $y$-Fehler Plotten?", key=i+z+1203718371)
                            if fehler_new:
                                y_err_new = st.number_input("Spaltenzahl für $y$-Fehler", min_value=1, max_value=n_spalten, step=1, key=i+z+12398713)
                            else:
                                y_err_new = None
                            
                            regression = st.checkbox("Regression Plotten", key=i+z+1387221837138)
                            if regression:
                                deg = st.number_input("Gebe den Grad der Regression an", min_value=1, step=1, max_value=5, key=i+z+12381893132131)
                                rd = st.number_input("Gebe die Rundung an", min_value=0, step=1, key=i+z+13213173817318)
                                
                            else:
                                deg = None
                                rd = None
                            fitter = st.checkbox("Fit-Funktion finden", key=i+z+123987198711)
                            if fitter:
                                fit_function = st.text_input(fr"Fit-Funktion erraten (Beispiel: $a \cdot x + \sin(b \cdot x)$ mit $a,b \in \mathbb{{R}}$)", key=i+z+99999)
                            else:
                                fit_function = None
                            new_plots.append([new_x_plot, new_y_plot, y_err_new, deg, rd, name_plot, point_or_line, fit_function])

                    ultra_plots.append(new_plots)
            loglog = st.checkbox("LogLog-Scale", key=123871738138717380218073)
            histo = st.checkbox("Histogramm darstellung", key=1983218967378193728913879)

        else:
            st.warning("Lade erst eine CSV Datei hoch")
        

    # Achsendefinition2
    if csvf:
        New_Plot_Arrays = []
        all_plots_config = [] 
        
        for ultra, current_df in zip(ultra_plots, dataframes):
            for n_plot in ultra:
                new_x_achse = current_df[current_df.columns[n_plot[0]-1]].values
                new_y_achse = current_df[current_df.columns[n_plot[1]-1]].values
                if n_plot[2] is not None:
                    new_y_error = current_df[current_df.columns[n_plot[2]-1]].values
                else:
                    new_y_error = None
                
                New_Plot_Arrays.append([new_x_achse, new_y_achse, new_y_error])
                all_plots_config.append(n_plot)
    # Limits
    with st.expander("Grenzeinstellungen"):
        # x-Achse
        x_limits = st.checkbox("$x$-Grenzen?")
        if x_limits:
            under_x = st.number_input("Untere $x$-Grenze")
            upper_x = st.number_input("Obere $x$-Grenze")
        else:
            if csvf:
                comparer_min = []
                comparer_max = []
                for i in New_Plot_Arrays:
                    comparer_min.append(min(i[0]))
                    comparer_max.append(max(i[0]))
                under_x = min(comparer_min)
                upper_x = max(comparer_max)
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

    # Plot
    plt.style.use(['science', 'grid'])    
    fig, ax = plt.subplots(figsize=(8,6))
    ax.set_title(name)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_Label)
    

    #calculator
    # regression calc
    regression_n = 0

    if csvf:
        regression_formula = []
        for regressions, axis in zip(all_plots_config, New_Plot_Arrays):
            
            if regressions[3] is not None:
                deg = regressions[3]
                rd = regressions[4]

                #calc
                r_matrix = np.polyfit(axis[0], axis[1], deg=deg, cov=True)
                slope = r_matrix[0]
                slope_rd = np.round(slope, rd)
                f = np.sqrt(np.diag(r_matrix[1])) 

                #formula
                if deg == 1:
                    formel_latex_rounded = fr"{var_y}({var_x}) \approx ({latify(slope_rd[0])} \pm {latify(round_up(f[0], rd))}) \cdot {var_x}"
                else:
                    formel_latex_rounded = fr"{var_y}({var_x}) \approx ({latify(slope_rd[0])} \pm {latify(round_up(f[0], rd))}) \cdot {var_x}^{{{deg}}}"
                for i,n in zip(range(1,deg+1), reversed(range(0,deg+1))):
                    if n-1 == 0:
                        formel_latex_rounded += fr"+ ({latify(slope_rd[i])} \pm {latify(round_up(f[i], rd))})"   
                    elif n-1 == 1:
                        formel_latex_rounded += fr"+ ({latify(slope_rd[i])} \pm {latify(round_up(f[i], rd))}) \cdot {var_x}"
                    else:
                        formel_latex_rounded += fr"+ ({latify(slope_rd[i])} \pm {latify(round_up(f[i], rd))}) \cdot {var_x}^{{{n-1}}}"
                regression_formula.append(formel_latex_rounded)
                regression_n += 1

                reg_fit = np.polyval(slope, x_fit)
                ax.plot(x_fit, reg_fit, linestyle='--',
                        label=f'Lin. Reg. für {regressions[5]}: ${formel_latex_rounded}$')

    # Fit Function Calc
    if csvf:
        for fit_func, axis in zip(all_plots_config, New_Plot_Arrays):
            function_to_fit = fit_func[7]
            if function_to_fit is not None and not function_to_fit == "":

                # erstellung der fit funktion
                parsed_fit_function = sp.parse_expr(function_to_fit, transformations='all', local_dict={'e': sp.E})
                x_sym = sp.Symbol('x')
                all_symbols = parsed_fit_function.free_symbols

                # sortieren der symbole (shoutout gemini)
                params = sorted([sym for sym in all_symbols if sym.name != 'x'], key=lambda s: s.name) 
                lambdify_args = [x_sym] + params

                #eigentlicher fit
                lambded_fit = sp.lambdify(lambdify_args, parsed_fit_function, 'numpy')
                popt, pcov = curve_fit(lambded_fit, axis[0], axis[1])

                #ausgabe formel
                param_values = dict(zip(params, popt))
                fitted_expr = parsed_fit_function.subs(param_values)
                fitted_expr_rounded = fitted_expr.evalf(3)

                #plot der fit funktion
                ax.plot(axis[0], lambded_fit(axis[0], *popt), label=fr'Fit Funktion: $f(x)={latify(fitted_expr_rounded)}$')
                

    # Messwerte Plot
    if csvf:
        try:
            for plots, names in zip(New_Plot_Arrays, all_plots_config):
                if names[6] == "Punkteplot":
                    ax.errorbar(plots[0], plots[1],
                                yerr=plots[2], fmt='.',
                                ecolor='black',
                                capsize=2, label=names[5])
                    if y_limits:
                        ax.set_ylim(bottom=under_y, top=upper_y)
                else:
                    ax.plot(plots[0], plots[1], label=names[5])

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
            for plots in New_Plot_Arrays:
                ax.loglog(plots[0], plots[1], label='LogLog-Scale Plot')    
        if histo:
            pass
                

# Outputspalte
with col_2:
    ax.legend()
    if fkt or csvf:
        st.subheader("Plot")
        st.pyplot(fig)
        if not X is None and not Y is None and X==Y:
            st.warning(fr"$x$ und $y$ Spaltenzahl stimmen überein, du plottest gerade $z$ gegen $z$ ($z \in header(CSV)$)")
        if csvf:
            for i, formulas in enumerate(regression_formula):
                st.subheader(fr"$\LaTeX$-Formel für Regression {i+1}")
                st.latex(formulas)
                st.code(formulas)
