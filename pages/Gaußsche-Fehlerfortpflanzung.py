import streamlit as st
import sympy as sp
from sympy import latex
import math

def latify(equation:str) -> str:
    return latex(sp.sympify(equation))
def round_up(k, decimals = 0):
    m = 10 ** decimals
    return math.ceil(k * m) / m

st.title("Gaußsche-Fehlerfortpflanzung")
st.subheader("Formeleingabe")
formel = st.text_input(fr"Gib deine Formel ein:")


if formel:
    Werte_Dict = {}
    Fehler_Dict = {}

    Gleichung = sp.parse_expr(formel, transformations='all', local_dict={'I': sp.Symbol('I'), 'e': sp.Symbol('E')})

    st.latex(latify(Gleichung))
    st.divider()

    try:
        lhs = str(Gleichung.lhs)
        Gleichung = Gleichung.rhs
    except AttributeError:
        lhs = None
        
    Liste = Gleichung.free_symbols

    Runden = st.checkbox("Runden")
    if Runden:
        rundung = st.number_input("Nachkommastellen", min_value=0, step=1)
    else:
        rundung = None


    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Werte")
    with col2:
        st.subheader("Fehler")

    for f in Liste:
        with col1:
            number = st.text_input(fr"Gebe deinen Wert für ${f}$ ein:")
            try:
                Werte_Dict[f] = float(sp.sympify(number.replace(",", ".")))
            except:
                pass
                
        with col2:
            number2 = st.text_input(fr"Gebe deinen Fehler für ${f}$ ein:")
            try:
                Fehler_Dict[f] = float(sp.sympify(number2.replace(",", ".")))
            except:
                pass
                

    try:
        if st.button("Lets Rock!", type="primary"):
            st.balloons()
            Gausslons = []
            for l in Liste:
                Ableitung = sp.diff(Gleichung, l)
                Gauss = (Ableitung * Fehler_Dict[l])**2
                Gausslons.append(Gauss)

            Summe = sp.sqrt(sum(Gausslons))
            Fehler = Summe.subs(Werte_Dict).evalf()
            Normalsumme = Gleichung.subs(Werte_Dict).evalf()
            LaTeX_Formel = latify(Summe)

            st.subheader("Ergebnis:")

            if lhs is None:
                if rundung is not None:
                    st.latex(fr"{round(Normalsumme, rundung)} \pm {latify(float(round_up(Fehler, rundung)))}")
                    st.code(fr"$({round(Normalsumme, rundung)} \pm {latify(float(round_up(Fehler, rundung)))})$")
                else:
                    st.latex(fr"{Normalsumme} \pm {Fehler}")
                    st.code(fr"$({Normalsumme} \pm {Fehler})$")   
                st.subheader(fr"$\LaTeX$-Fehlerformel")
                st.latex(LaTeX_Formel)
                st.code(LaTeX_Formel)
            else:
                if len(lhs) > 1:
                    if rundung is not None:
                        st.latex(fr"\{lhs} \approx {round(Normalsumme, rundung)} \pm {latify(float(round_up(Fehler, rundung)))}")
                        st.code(fr"$\{lhs} \approx ({round(Normalsumme, rundung)} \pm {latify(float(round_up(Fehler, rundung)))})$")
                    else:
                        st.latex(fr"\{lhs} = {Normalsumme} \pm {Fehler}")
                        st.code(fr"$\{lhs} = ({Normalsumme} \pm {Fehler})$")
                    st.subheader(fr"$\LaTeX$-Fehlerformel")
                    st.latex(fr"\Delta \{lhs} = {LaTeX_Formel}")
                    st.code(fr"\Delta \{lhs} = {LaTeX_Formel}")
                else:
                    if rundung is not None:
                        st.latex(fr"{lhs} \approx {round(Normalsumme, rundung)} \pm {latify(float(round_up(Fehler, rundung)))}")
                        st.code(fr"${lhs} \approx ({round(Normalsumme, rundung)} \pm {latify(float(round_up(Fehler, rundung)))})$")
                    else:
                        st.latex(fr"{lhs} = {Normalsumme} \pm {Fehler}")
                        st.code(fr"${lhs} = ({Normalsumme} \pm {Fehler})$")
                    st.subheader(fr"$\LaTeX$-Fehlerformel")
                    st.latex(fr"\Delta {lhs} = {LaTeX_Formel}")
                    st.code(fr"\Delta {lhs} = {LaTeX_Formel}")
    except KeyError:
        st.warning("Gebe Zahlen ein, keine Strings, leere Spalten oder Sonderzeichen!")
    
