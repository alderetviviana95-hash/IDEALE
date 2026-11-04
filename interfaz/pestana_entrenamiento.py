"""
Pestana "Entrenamiento": evidencia de que el modelo se entreno.
Muestra la fecha, las metricas, la validacion cruzada, las graficas y las
predicciones sobre los vehiculos de prueba (archivos de evidencias/).
"""
import pandas as pd
import streamlit as st

from interfaz.datos import (COMPARACION, GRAFICAS, PREDICCIONES, VALIDACION_CRUZADA,
                            pesos)
from interfaz.estilos import titulo_seccion


def mostrar(cat: dict) -> None:
    st.markdown("#### Entrenamiento del modelo (Python · CRISP-DM)")
    fecha = cat.get("fecha_entrenamiento", "sin registro")
    st.caption(f"Último entrenamiento: **{fecha}** · Reporte completo en "
               "`evidencias/reporte_entrenamiento.md`")

    tabla = pd.read_csv(COMPARACION)
    mejor = tabla.sort_values("R2", ascending=False).iloc[0]
    m1, m2, m3 = st.columns(3)
    m1.metric("Mejor modelo", mejor["Modelo"], border=True)
    m2.metric("R² (prueba)", f"{mejor['R2']:.3f}", border=True)
    m3.metric("Error promedio (MAE)", pesos(mejor["MAE (COP)"]), border=True)

    titulo_seccion("Comparación de modelos · 200 vehículos de prueba")
    st.dataframe(
        tabla.style.format({"MAE (COP)": pesos, "RMSE (COP)": pesos, "R2": "{:.4f}"}),
        hide_index=True, width="stretch",
    )

    if VALIDACION_CRUZADA.exists():
        titulo_seccion("Validación cruzada · R² en cada una de las 5 particiones")
        cv = pd.read_csv(VALIDACION_CRUZADA).pivot(index="Particion", columns="Modelo",
                                                    values="R2")
        st.dataframe(cv.style.format("{:.4f}"), width="stretch")

    g1, g2, g3 = st.columns(3)
    for col, archivo, titulo in [
        (g1, "comparacion_r2.png", "Comparación de modelos"),
        (g2, "real_vs_predicho.png", "Precio real vs predicho"),
        (g3, "distribucion_error.png", "Distribución del error"),
    ]:
        if (GRAFICAS / archivo).exists():
            col.image(str(GRAFICAS / archivo), caption=titulo)

    if PREDICCIONES.exists():
        pred = pd.read_csv(PREDICCIONES)
        titulo_seccion(f"Predicciones sobre los {len(pred)} vehículos de prueba "
                       "(nunca vistos en el entrenamiento)")
        st.dataframe(
            pred.style.format({"precio_real": pesos, "precio_predicho": pesos,
                               "error": pesos, "error_%": "{:.1f}%"}),
            hide_index=True, width="stretch", height=280,
        )
        st.download_button("Descargar predicciones (CSV)", PREDICCIONES.read_bytes(),
                           file_name=PREDICCIONES.name, mime="text/csv")
