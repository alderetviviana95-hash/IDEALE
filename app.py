"""
IDEALE - Aplicacion web (Streamlit).

Ejecutar con:  python -m streamlit run app.py

Este archivo solo arma la pagina: encabezado, barra lateral y pestanas.
El contenido de cada pestana esta en la carpeta interfaz/:
    pestana_valoracion.py    -> estimar el precio de un vehiculo
    pestana_red_neuronal.py  -> red neuronal (Python y Weka) y experimento de nodos
    pestana_entrenamiento.py -> evidencia del entrenamiento y metricas
    pestana_datos.py         -> explorar el dataset
"""
import streamlit as st

from interfaz import (pestana_datos, pestana_entrenamiento, pestana_red_neuronal,
                      pestana_valoracion)
from interfaz.datos import (MODELO, RANGOS, cargar_catalogo, cargar_datos,
                            cargar_modelo, miles, pesos_html)
from interfaz.estilos import COLORES, aplicar_estilos

st.set_page_config(page_title="IDEALE | Valoración de vehículos", page_icon="🚘",
                   layout="wide")
aplicar_estilos()

# ------------------------------------------------------------------ carga
if not MODELO.exists():
    st.error("No se encontró el modelo. Ejecuta primero: python ejecutar_entrenamiento.py")
    st.stop()

modelo = cargar_modelo()
cat = cargar_catalogo()
df, cortes = cargar_datos()

# ------------------------------------------------------------------ encabezado
st.markdown(
    f"""
    <div class="encabezado">
      <div class="marca-emp">IDEALE
        <small>Valoración inteligente de vehículos usados</small></div>
      <div class="kpis">
        <div class="kpi"><b>{miles(len(df))}</b><span>Vehículos</span></div>
        <div class="kpi"><b>{df['marca'].nunique()}</b><span>Marcas</span></div>
        <div class="kpi"><b>{df['modelo'].nunique()}</b><span>Modelos</span></div>
        <div class="kpi"><b>{cat['mejor_modelo']}</b><span>Modelo activo</span></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ barra lateral
with st.sidebar:
    st.markdown("### Parámetros comerciales")
    margen = st.slider(
        "Margen de ganancia (%)", 1, 25, 10,
        help="La compra sugerida es el valor estimado menos este margen; "
             "la venta sugerida es el valor estimado más este margen.",
    ) / 100
    st.divider()
    st.markdown("### Segmentos de precio")
    st.markdown(
        "".join(
            f"<div class='rango-fila'><span class='badge' style='background:{COLORES[r]}'>"
            f"{r}</span><span class='rango-valor'>{pesos_html(cortes[i])} – "
            f"{pesos_html(cortes[i + 1])}</span></div>"
            for i, r in enumerate(RANGOS)
        ),
        unsafe_allow_html=True,
    )
    st.caption("Segmentos usados para entrenar la red neuronal en Weka.")
    st.divider()
    st.caption("Metodología CRISP-DM · Python · Weka")

# ------------------------------------------------------------------ pestanas
tab_valorar, tab_red, tab_entrenamiento, tab_datos = st.tabs(
    ["Valoración", "Red neuronal", "Entrenamiento", "Datos"]
)
with tab_valorar:
    pestana_valoracion.mostrar(modelo, cat, df, cortes, margen)
with tab_red:
    pestana_red_neuronal.mostrar(cat)
with tab_entrenamiento:
    pestana_entrenamiento.mostrar(cat)
with tab_datos:
    pestana_datos.mostrar(df)
