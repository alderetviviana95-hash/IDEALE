"""
IDEALE - Configuracion compartida por todos los pasos del pipeline.

Todas las rutas del proyecto estan aqui, asi cada script solo importa
lo que necesita:  from config import CSV, MODELO, ...
"""
from pathlib import Path

SEED = 42           # semilla para que los resultados se puedan repetir
ANIO_ACTUAL = 2026

RAIZ = Path(__file__).resolve().parent.parent

# --- Datos ---
DATA = RAIZ / "data"
ARFF_ORIGINAL = DATA / "original" / "dataset_ideale_weka_1000.arff"
CSV = DATA / "dataset_ideale_con_precio.csv"

# --- Archivos para Weka ---
WEKA = DATA / "weka"
ARFF_PRECIO = WEKA / "dataset_ideale_con_precio.arff"
ARFF_RANGO = WEKA / "dataset_ideale_precio_rango.arff"
ARFF_RANGO_SIN_MODELO = WEKA / "dataset_ideale_precio_rango_sin_modelo.arff"

# --- Modelo entrenado (lo usa la app) ---
MODELO_DIR = RAIZ / "modelo"
MODELO = MODELO_DIR / "modelo_ideale.joblib"
CATALOGO = MODELO_DIR / "catalogo.json"
COMPARACION = MODELO_DIR / "comparacion_modelos.csv"

# --- Evidencias del entrenamiento (para mostrar a la profesora) ---
EVIDENCIAS = RAIZ / "evidencias"
GRAFICAS = EVIDENCIAS / "graficas"
REPORTE = EVIDENCIAS / "reporte_entrenamiento.md"
LOG = EVIDENCIAS / "log_entrenamiento.txt"
PREDICCIONES = EVIDENCIAS / "predicciones_prueba.csv"
VALIDACION_CRUZADA = EVIDENCIAS / "validacion_cruzada.csv"
EXPERIMENTO_NODOS = EVIDENCIAS / "experimento_nodos_mlp.csv"
RESULTADOS_WEKA = EVIDENCIAS / "weka" / "resultados_weka.csv"

# --- Fotos de los vehiculos ---
IMAGENES = RAIZ / "imagenes"
CREDITOS = IMAGENES / "creditos.csv"
