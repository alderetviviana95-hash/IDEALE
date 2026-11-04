"""
Pestana "Red neuronal (Weka)": diagrama de la red, configuracion usada en
Weka y tabla del experimento con distinta cantidad de nodos.
"""
import altair as alt
import pandas as pd
import streamlit as st

from interfaz.datos import EXPERIMENTO_NODOS, GRAFICAS, RANGOS, RESULTADOS_WEKA, pesos
from interfaz.estilos import AZUL, COLORES, MARINO, titulo_seccion

ENTRADAS_RED = ["marca", "anio", "combustible", "transmision", "kilometraje", "estado"]


def diagrama_red(ocultos: int) -> str:
    """Codigo DOT (Graphviz) de la red: entradas -> capa oculta -> salidas."""
    dot = ["digraph red {", 'bgcolor="transparent";',
           "rankdir=LR; splines=line; nodesep=0.12; ranksep=1.6;",
           'node [shape=circle, style=filled, fontname="Helvetica", fontsize=10, '
           'width=0.5, fixedsize=true, color="#ffffff", fontcolor="#1c2733"];',
           'edge [color="#c3ccd7", arrowsize=0.3, penwidth=0.5];']
    dot.append('subgraph cluster_e {label="Entrada"; color="none"; fontname="Helvetica"; '
               'fontcolor="#5b6b7d";')
    dot += [f'e{i} [label="{n}", fillcolor="#e9edf2", shape=box, '
            f'style="rounded,filled", width=1.2];' for i, n in enumerate(ENTRADAS_RED)]
    dot.append("}")
    dot.append(f'subgraph cluster_o {{label="Capa oculta ({ocultos} nodos)"; '
               'color="none"; fontname="Helvetica"; fontcolor="#5b6b7d";')
    dot += [f'h{j} [label="", fillcolor="{AZUL}"];' for j in range(ocultos)]
    dot.append("}")
    dot.append('subgraph cluster_s {label="Salida"; color="none"; fontname="Helvetica"; '
               'fontcolor="#5b6b7d";')
    dot += [f's{k} [label="{r}", fillcolor="{COLORES[r]}", fontcolor="white", '
            f'shape=box, style="rounded,filled", width=0.9];' for k, r in enumerate(RANGOS)]
    dot.append("}")
    dot += [f"e{i} -> h{j};" for i in range(len(ENTRADAS_RED)) for j in range(ocultos)]
    dot += [f"h{j} -> s{k};" for j in range(ocultos) for k in range(len(RANGOS))]
    dot.append("}")
    return "\n".join(dot)


def cargar_resultados() -> pd.DataFrame:
    if RESULTADOS_WEKA.exists():
        return pd.read_csv(RESULTADOS_WEKA, dtype={"hiddenLayers": str})
    # La prueba con 20 nodos no se incluye: supero el limite de 100 s de Weka Web
    return pd.DataFrame({"hiddenLayers": ["3", "5", "10", "10,5"],
                         "Exactitud (%)": [None] * 4})


def grafica_nodos(validos: pd.DataFrame) -> alt.Chart:
    """Barras de exactitud por configuracion; la mejor resaltada y con su valor."""
    datos = validos.assign(
        Configuracion=validos["hiddenLayers"].map(
            lambda h: f"{h} nodos" if "," not in h else f"{h} (2 capas)"),
        Mejor=validos["Exactitud (%)"] == validos["Exactitud (%)"].max(),
    )
    orden = datos["Configuracion"].tolist()

    base = alt.Chart(datos).encode(
        x=alt.X("Configuracion:N", sort=orden, title="Nodos en la capa oculta",
                axis=alt.Axis(labelAngle=0, labelFontSize=12, titlePadding=10)),
        y=alt.Y("Exactitud (%):Q", scale=alt.Scale(domain=[0, 100]),
                title="Exactitud (%)", axis=alt.Axis(tickCount=5, titlePadding=10)),
    )
    barras = base.mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3, size=46).encode(
        color=alt.condition("datum.Mejor", alt.value(MARINO), alt.value("#a9bccf")),
        tooltip=["Configuracion", alt.Tooltip("Exactitud (%):Q", format=".2f")],
    )
    etiquetas = base.mark_text(dy=-9, fontSize=13, fontWeight="bold", color=MARINO).encode(
        text=alt.Text("Exactitud (%):Q", format=".2f"))
    return ((barras + etiquetas)
            .properties(height=300, padding={"left": 10, "top": 10, "right": 10, "bottom": 5})
            .configure_view(strokeWidth=0))


def seccion_python(cat: dict) -> None:
    """Red neuronal de regresion entrenada en Python (paso2_entrenar_modelo.py)."""
    if not EXPERIMENTO_NODOS.exists():
        return
    exp = pd.read_csv(EXPERIMENTO_NODOS, dtype={"Nodos": str})
    elegida = cat.get("nodos_red_neuronal", "")
    fila = exp[exp["Nodos"] == elegida].iloc[0] if elegida in set(exp["Nodos"]) else exp.iloc[0]

    st.markdown("#### Red neuronal en Python · predice el precio exacto")
    st.write(
        "Se entrenó un **perceptrón multicapa (MLPRegressor)** con todas las variables, "
        "incluida *modelo*, para estimar el precio en pesos. Se probaron distintas "
        "cantidades de nodos y se eligió la mejor con validación cruzada."
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("Configuración elegida", f"{fila['Nodos']} nodos", border=True)
    m2.metric("R² (prueba)", f"{fila['R2 prueba']:.3f}", border=True)
    m3.metric("Error promedio (MAE)", pesos(fila["MAE prueba (COP)"]), border=True)

    grafica = GRAFICAS / "mlp_nodos.png"
    if grafica.exists():
        st.image(str(grafica), width="stretch")
    st.dataframe(
        exp.style.format({"R2 CV (media)": "{:.4f}", "R2 prueba": "{:.4f}",
                          "MAE prueba (COP)": pesos, "Tiempo (s)": "{:.1f}"}),
        hide_index=True, width="stretch",
    )
    st.caption("La configuración se elige por el R² de la validación cruzada (solo datos de "
               "entrenamiento), no por el resultado en prueba, para no sesgar la evaluación.")
    st.divider()


def mostrar(cat: dict) -> None:
    seccion_python(cat)
    st.markdown("#### Red neuronal en Weka · clasifica por segmento de precio")
    st.write(
        "Además de los modelos en Python, se entrenó una **red neuronal (MLP)** en "
        "Weka para **clasificar** cada vehículo en un segmento de precio. Como la red "
        "solo está disponible en Clasificación, el precio se convirtió en tres "
        "categorías con la misma cantidad de vehículos cada una."
    )

    c1, c2 = st.columns([1.6, 1], gap="large")
    with c1:
        with st.container(border=True):
            titulo_seccion("Arquitectura de la red")
            ocultos = st.slider("Nodos en la capa oculta (hiddenLayers)", 1, 20, 5)
            st.graphviz_chart(diagrama_red(ocultos), width="stretch")
            st.caption("Cada nodo de la capa oculta aprende un patrón (por ejemplo, "
                       "'más kilómetros = más barato'). Más nodos = más capacidad, "
                       "pero también más tiempo y riesgo de memorizar los datos.")
    with c2:
        with st.container(border=True):
            titulo_seccion("Configuración en Weka")
            st.dataframe(
                pd.DataFrame({
                    "Parámetro": ["Archivo", "Tarea", "Algoritmo", "Objetivo",
                                  "trainingTime", "Evaluación"],
                    "Valor": ["precio_rango_sin_modelo.arff", "Clasificación",
                              "MultilayerPerceptron", "precio (segmento)", "200",
                              "Validación cruzada"],
                }),
                hide_index=True, width="stretch",
            )
            st.caption("Se quitó la columna 'modelo' (59 valores) porque la tarea "
                       "superaba el límite de 100 s de Weka Web.")

    st.markdown("#### Experimento: número de nodos")
    st.caption("Registre la exactitud obtenida en Weka para cada prueba y guarde. "
               "Las capturas de pantalla van en la carpeta evidencias/weka/.")
    e1, e2 = st.columns([1, 1.3], gap="large")
    with e1:
        tabla = st.data_editor(
            cargar_resultados(), num_rows="dynamic", hide_index=True, width="stretch",
            column_config={
                "hiddenLayers": st.column_config.TextColumn("hiddenLayers"),
                "Exactitud (%)": st.column_config.NumberColumn(
                    "Exactitud (%)", min_value=0, max_value=100, format="%.2f"),
            },
        )
        if st.button("Guardar resultados"):
            RESULTADOS_WEKA.parent.mkdir(parents=True, exist_ok=True)
            tabla.to_csv(RESULTADOS_WEKA, index=False)
            st.success("Resultados guardados en evidencias/weka/resultados_weka.csv")
    with e2:
        validos = tabla.dropna(subset=["Exactitud (%)"])
        if validos.empty:
            st.info("Al registrar resultados se mostrará aquí la gráfica comparativa.")
        else:
            mejor = validos.loc[validos["Exactitud (%)"].idxmax()]
            st.success(f"Mejor configuración: **{mejor['hiddenLayers']} nodos** "
                       f"con **{mejor['Exactitud (%)']:.2f}%** de exactitud")
            st.altair_chart(grafica_nodos(validos), width="stretch")
    st.caption("La prueba con 20 nodos no se incluye porque el entrenamiento superó el "
               "límite de 100 segundos de Weka Web y no entregó resultado.")

    completos = RESULTADOS_WEKA.parent / "resultados_weka_completos.csv"
    matriz = GRAFICAS / "weka_matriz_confusion.png"
    if completos.exists():
        st.markdown("#### Métricas completas en Weka")
        m1, m2 = st.columns([1.5, 1], gap="large")
        with m1:
            titulo_seccion("Exactitud, precisión, sensibilidad y F-Measure")
            metricas = pd.read_csv(completos, dtype={"hiddenLayers": str}).iloc[:, :5]
            st.dataframe(metricas.style.format("{:.2f}", subset=metricas.columns[1:]),
                         hide_index=True, width="stretch")
            st.caption("Las filas de cada matriz de confusión suman 1.000 vehículos: cada "
                       "vehículo se evaluó una vez mediante validación cruzada.")
        with m2:
            if matriz.exists():
                st.image(str(matriz), caption="Matriz de confusión de la mejor configuración")
