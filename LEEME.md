# IDEALE - Valoración inteligente de vehículos usados

Sistema que estima el precio de un carro usado con Inteligencia Artificial
(metodología CRISP-DM), con una red neuronal adicional entrenada en Weka.

## Estructura del proyecto

```
proyecto_venta_carros/
├── app.py                      ← Aplicación web (Streamlit)
├── ejecutar_entrenamiento.py   ← Corre TODO el entrenamiento y guarda las evidencias
├── informe_ideale.ipynb        ← Cuaderno Jupyter: datos, graficas, modelos y comprobacion de cifras
├── requirements.txt            ← Librerías necesarias
│
├── pipeline/                   ← Pasos del entrenamiento (en orden)
│   ├── config.py               ·  rutas y parámetros compartidos
│   ├── paso1_generar_precios.py·  crea la columna precio (sintética)
│   ├── paso2_entrenar_modelo.py·  limpia, prueba nodos de la red neuronal, entrena 4 modelos y guarda el mejor
│   ├── paso3_preparar_weka.py  ·  crea los .arff Barato/Medio/Caro para la red neuronal
│   ├── extra_descargar_fotos.py·  fotos reales de Wikimedia (opcional)
│   └── extra_crear_dibujos.py  ·  dibujos de relleno (opcional)
│
├── interfaz/                   ← Código de la app, una pestaña por archivo
│   ├── estilos.py · datos.py
│   ├── pestana_valoracion.py · pestana_red_neuronal.py
│   └── pestana_entrenamiento.py · pestana_datos.py
│
├── data/
│   ├── original/               ·  dataset original (sin precio)
│   ├── dataset_ideale_con_precio.csv
│   └── weka/                   ·  archivos .arff para abrir en Weka
│
├── modelo/                     ← Modelo entrenado que usa la app
├── evidencias/                 ← PRUEBAS DEL ENTRENAMIENTO
│   ├── reporte_entrenamiento.md·  fecha, datos, métricas y modelo elegido
│   ├── log_entrenamiento.txt   ·  salida completa de la consola con fecha y hora
│   ├── predicciones_prueba.csv ·  real vs predicho de los 200 carros de prueba
│   ├── validacion_cruzada.csv  ·  R² de cada una de las 5 particiones
│   ├── experimento_nodos_mlp.csv·  red neuronal con 3, 5, 10, 20, 50, 10+5 y 20+10 nodos
│   ├── graficas/               ·  comparación, real vs predicho, distribución del error
│   └── weka/                   ·  capturas y resultados de la red neuronal en Weka
└── imagenes/                   ← Fotos de los vehículos + créditos
```

## Abrir la app por primera vez (Windows)

Requisito: Python 3.11 o superior (https://www.python.org/downloads/,
marcar "Add Python to PATH" al instalar).

1. Abrir la carpeta `proyecto_venta_carros` en Visual Studio Code (Archivo > Abrir carpeta).
2. En la terminal (Ctrl+ñ), uno por uno:

       python -m venv venv
       .\venv\Scripts\python.exe -m pip install -r requirements.txt
       .\venv\Scripts\python.exe -m streamlit run app.py

El modelo ya viene entrenado, no hace falta volver a entrenarlo.

## Volver a entrenar (y generar evidencias nuevas)

    .\venv\Scripts\python.exe ejecutar_entrenamiento.py

Corre los pasos 1, 2 y 3 en orden y actualiza la carpeta `evidencias/`.

## Weka

- `data/weka/dataset_ideale_con_precio.arff`: precio numérico (Regresión).
- `data/weka/dataset_ideale_precio_rango_sin_modelo.arff`: precio Barato/Medio/Caro,
  usado para la Red Neuronal (MLP) en Clasificación.
