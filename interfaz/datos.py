"""
Rutas, carga de archivos y funciones de formato que usan todas las pestanas.
"""
import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "modelo" / "modelo_ideale.joblib"
CATALOGO = RAIZ / "modelo" / "catalogo.json"
COMPARACION = RAIZ / "modelo" / "comparacion_modelos.csv"
CSV = RAIZ / "data" / "dataset_ideale_con_precio.csv"
IMAGENES = RAIZ / "imagenes"
EVIDENCIAS = RAIZ / "evidencias"
GRAFICAS = EVIDENCIAS / "graficas"
PREDICCIONES = EVIDENCIAS / "predicciones_prueba.csv"
VALIDACION_CRUZADA = EVIDENCIAS / "validacion_cruzada.csv"
RESULTADOS_WEKA = EVIDENCIAS / "weka" / "resultados_weka.csv"
EXPERIMENTO_NODOS = EVIDENCIAS / "experimento_nodos_mlp.csv"

RANGOS = ["Barato", "Medio", "Caro"]


# ------------------------------------------------------------------ carga
@st.cache_resource
def cargar_modelo():
    return joblib.load(MODELO)


@st.cache_data
def cargar_catalogo() -> dict:
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


@st.cache_data
def cargar_datos():
    df = pd.read_csv(CSV)
    # Mismos cortes (terciles) que el ARFF usado en Weka
    df["rango"], cortes = pd.qcut(df["precio"], q=3, labels=RANGOS, retbins=True)
    return df, cortes


@st.cache_data
def cargar_creditos() -> dict:
    """archivo -> fila de imagenes/creditos.csv (autor y licencia de la foto)."""
    ruta = IMAGENES / "creditos.csv"
    if not ruta.exists():
        return {}
    return pd.read_csv(ruta).set_index("archivo").to_dict("index")


def buscar_imagen(marca: str, modelo: str):
    """Busca imagenes/<marca>_<modelo>.(jpg|jpeg|png|webp). None si no hay."""
    nombre = f"{marca}_{modelo}".lower().replace(" ", "_").replace("-", "_")
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        ruta = IMAGENES / f"{nombre}{ext}"
        if ruta.exists():
            return str(ruta)
    return None


# ------------------------------------------------------------------ formato
def pesos(valor: float) -> str:
    return "$ {:,.0f}".format(valor).replace(",", ".")


def pesos_html(valor: float) -> str:
    # En st.markdown el "$" se interpreta como formula LaTeX
    return pesos(valor).replace("$", "&#36;")


def miles(valor: float) -> str:
    return f"{valor:,.0f}".replace(",", ".")


def rango_de(valor: float, cortes) -> str:
    if valor < cortes[1]:
        return "Barato"
    return "Medio" if valor < cortes[2] else "Caro"
