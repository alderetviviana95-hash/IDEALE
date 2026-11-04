"""
Pestana "Valoracion": el usuario ingresa los datos del vehiculo y el
modelo entrenado estima su precio, la compra y la venta sugerida.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from interfaz.datos import (buscar_imagen, cargar_creditos, miles, pesos, pesos_html,
                            rango_de)
from interfaz.estilos import COLORES, titulo_seccion


def formulario(cat: dict) -> tuple[dict, bool]:
    """Datos del vehiculo. Devuelve (datos, se_pulso_estimar)."""
    with st.container(border=True):
        titulo_seccion("Datos del vehículo")
        c1, c2 = st.columns(2)
        marca = c1.selectbox("Marca", sorted(cat["modelos_por_marca"]))
        # El selector de modelo depende de la marca elegida
        referencia = c2.selectbox("Modelo", cat["modelos_por_marca"][marca])

        img = buscar_imagen(marca, referencia)
        if img:
            st.image(img, width="stretch")
            cred = cargar_creditos().get(Path(img).name)
            if cred:
                st.caption(f"{marca} {referencia} · Foto: {cred['autor']} "
                           f"({cred['licencia']}) · [Wikimedia Commons]({cred['fuente']})")

        anio = st.slider("Año", cat["anio_min"], cat["anio_actual"], 2020)
        km = st.number_input("Kilometraje (km)", 0, 600_000, 60_000, step=1_000)
        c1, c2 = st.columns(2)
        combustible = c1.radio("Combustible", cat["combustibles"], horizontal=True)
        transmision = c2.radio("Transmisión", cat["transmisiones"], horizontal=True)
        estado = st.select_slider("Estado", cat["estados"], value="Buen estado")
        estimar = st.button("Estimar precio", type="primary", width="stretch")

    datos = {"marca": marca, "modelo": referencia, "anio": anio, "kilometraje": km,
             "combustible": combustible, "transmision": transmision, "estado": estado}
    return datos, estimar


def validar(d: dict, anio_actual: int) -> tuple[list, list]:
    """Revisa que los datos sean coherentes. Devuelve (errores, avisos)."""
    antiguedad = anio_actual - d["anio"]
    errores, avisos = [], []
    if d["estado"] == "Nuevo 0 km" and (d["kilometraje"] > 100 or antiguedad > 1):
        errores.append("Un vehículo 'Nuevo 0 km' debe tener ~0 km y ser "
                       "del año actual o el anterior.")
    if antiguedad > 0 and d["kilometraje"] > 60_000 * antiguedad:
        avisos.append("El kilometraje es muy alto para la edad del vehículo; revisa el dato.")
    if antiguedad >= 3 and d["kilometraje"] < 1_000:
        avisos.append("Un vehículo de varios años con casi 0 km es poco común; "
                      "revisa el dato.")
    return errores, avisos


def predecir(modelo, d: dict, anio_actual: int) -> float:
    """Usa el mejor modelo entrenado (ver modelo/catalogo.json) para estimar el precio."""
    X = pd.DataFrame([{
        "marca": d["marca"], "modelo": d["modelo"],
        "combustible": d["combustible"], "transmision": d["transmision"],
        "estado": d["estado"], "antiguedad": anio_actual - d["anio"],
        "kilometraje": d["kilometraje"],
    }])
    return float(modelo.predict(X)[0])


def resultado(d: dict, valor: float, margen: float, df: pd.DataFrame, cortes) -> None:
    compra, venta = valor * (1 - margen), valor * (1 + margen)
    rango = rango_de(valor, cortes)
    percentil = (df["precio"] < valor).mean()
    pos = min(max(percentil, 0.01), 0.99) * 100

    st.markdown(
        f"""
        <div class="precio-card">
          <div class="etq">Valor comercial estimado · {d['marca']} {d['modelo']} {d['anio']}</div>
          <div class="valor">{pesos_html(valor)}</div>
          <span class="badge" style="background:{COLORES[rango]}">Segmento {rango}</span>
          <div class="barra"><div class="marca-barra" style="left:{pos:.0f}%"></div></div>
          <small>Ubicado por encima del {percentil:.0%} de los vehículos registrados</small>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    m1, m2 = st.columns(2)
    m1.metric("Compra sugerida", pesos(compra), border=True)
    m2.metric("Venta sugerida", pesos(venta), border=True)
    st.markdown(
        f"<div class='franja'><span>Ganancia esperada por operación</span>"
        f"<b>{pesos_html(venta - compra)}</b>"
        f"<span>Margen bruto {margen * 2:.0%}</span></div>",
        unsafe_allow_html=True,
    )

    similares = df[(df["marca"] == d["marca"]) & (df["modelo"] == d["modelo"])]
    if not similares.empty:
        titulo_seccion(f"Referencias en la base de datos · {d['marca']} {d['modelo']} "
                       f"({len(similares)})")
        similares = similares.assign(dif=(similares["anio"] - d["anio"]).abs())
        st.dataframe(
            similares.sort_values("dif").head(5)
            [["anio", "kilometraje", "estado", "transmision", "precio"]]
            .rename(columns={"anio": "Año", "kilometraje": "Kilometraje",
                             "estado": "Estado", "transmision": "Transmisión",
                             "precio": "Precio"})
            .style.format({"Precio": pesos, "Kilometraje": miles}),
            hide_index=True, width="stretch",
        )
    st.caption("Estimación de apoyo a la decisión; los precios base del entrenamiento "
               "son sintéticos.")


def mostrar(modelo, cat: dict, df: pd.DataFrame, cortes, margen: float) -> None:
    col_in, col_out = st.columns([1, 1.15], gap="large")
    with col_in:
        datos, estimar = formulario(cat)

    with col_out:
        if not estimar:
            st.markdown(
                "<div class='vacio'><h4>Sin estimación</h4>"
                "Ingrese los datos del vehículo y seleccione <b>Estimar precio</b>.</div>",
                unsafe_allow_html=True,
            )
            return

        errores, avisos = validar(datos, cat["anio_actual"])
        for e in errores:
            st.error(e)
        if errores:
            return
        for a in avisos:
            st.warning(a)
        valor = predecir(modelo, datos, cat["anio_actual"])
        resultado(datos, valor, margen, df, cortes)
