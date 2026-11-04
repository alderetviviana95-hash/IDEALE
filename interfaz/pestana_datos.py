"""
Pestana "Datos": exploracion del dataset de vehiculos.
"""
import pandas as pd
import streamlit as st

from interfaz.datos import RANGOS, miles, pesos
from interfaz.estilos import AZUL, MARINO, titulo_seccion


def mostrar(df: pd.DataFrame) -> None:
    st.markdown("#### Base de datos de vehículos")
    marcas = st.multiselect("Filtrar por marca", sorted(df["marca"].unique()),
                            placeholder="Todas las marcas")
    vista = df[df["marca"].isin(marcas)] if marcas else df

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Vehículos", miles(len(vista)), border=True)
    d2.metric("Precio promedio", pesos(vista["precio"].mean()), border=True)
    d3.metric("Año promedio", f"{vista['anio'].mean():.0f}", border=True)
    d4.metric("Km promedio", miles(vista["kilometraje"].mean()), border=True)

    g1, g2 = st.columns(2, gap="large")
    with g1:
        titulo_seccion("Precio promedio por marca (millones COP)")
        st.bar_chart(
            (vista.groupby("marca")["precio"].mean() / 1e6).sort_values(),
            horizontal=True, color=AZUL, height=320,
        )
    with g2:
        titulo_seccion("Vehículos por segmento de precio")
        conteo = vista["rango"].value_counts().reindex(RANGOS).rename("Vehículos")
        st.bar_chart(conteo, color=MARINO, height=320)

    st.dataframe(
        vista.drop(columns="rango").style.format({"precio": pesos, "kilometraje": miles}),
        hide_index=True, width="stretch", height=320,
    )
