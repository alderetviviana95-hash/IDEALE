# Reporte de entrenamiento - IDEALE

- **Fecha de ejecucion:** 2026-11-03 17:33:53
- **Equipo:** CristianBaquero · Python 3.11.9 · scikit-learn 1.9.1

## 1. Datos
- Archivo: `data/dataset_ideale_con_precio.csv` (huella SHA-256: `3fd1171913b02e73`)
- Registros cargados: 1000
- Registros tras limpieza: 1000
- Variables de entrada: marca, modelo, combustible, transmision, estado, antiguedad, kilometraje
- Variable objetivo: precio (COP)

## 2. Division de los datos
- Entrenamiento: 800 vehiculos (80 %)
- Prueba: 200 vehiculos (20 %), nunca vistos durante el entrenamiento
- Semilla aleatoria: 42 (los resultados se pueden repetir)
- Validacion cruzada: 5 particiones sobre el conjunto de entrenamiento

## 3. Experimento: nodos de la red neuronal (MLP)
Se probo la red con distinta cantidad de nodos en la capa oculta. La mejor
configuracion se eligio por el R2 de la validacion cruzada (solo datos de
entrenamiento).

| Nodos | Capas ocultas | R2 CV (media) | R2 prueba | MAE prueba (COP) | Epocas | Tiempo (s) |
|---|---|---|---|---|---|---|
| 3 | 1 | 0.9746 | 0.9736 | $ 4.490.730 | 635 | 1.0 |
| 5 | 1 | 0.9754 | 0.9782 | $ 4.388.562 | 553 | 1.1 |
| 10 | 1 | 0.9787 | 0.9698 | $ 5.036.763 | 267 | 0.6 |
| 20 | 1 | 0.9818 | 0.9791 | $ 4.393.109 | 387 | 1.9 |
| 50 | 1 | 0.9794 | 0.9833 | $ 4.189.422 | 307 | 1.9 |
| 10,5 | 2 | 0.9798 | 0.9832 | $ 4.210.654 | 376 | 2.2 |
| 20,10 | 2 | 0.9762 | 0.9794 | $ 4.081.873 | 275 | 1.8 |

**Red neuronal elegida: 20 nodos**

## 4. Comparacion de modelos
| Modelo | MAE (COP) | RMSE (COP) | R2 | R2 CV (media) | R2 CV (desv.) | Tiempo (s) |
|---|---|---|---|---|---|---|
| Red neuronal (MLP) | $ 4.393.109 | $ 7.551.002 | 0.9791 | 0.9818 | 0.0044 | 3.53 |
| Regresion lineal | $ 5.030.268 | $ 7.977.826 | 0.9767 | 0.9764 | 0.0033 | 0.03 |
| Gradient Boosting | $ 9.439.103 | $ 15.461.474 | 0.9124 | 0.9090 | 0.0328 | 0.65 |
| Random Forest | $ 12.767.220 | $ 21.864.970 | 0.8247 | 0.8127 | 0.0581 | 0.45 |

**Modelo seleccionado (mayor R2): Red neuronal (MLP)**
Se reentreno con todos los datos y se guardo en `modelo/modelo_ideale.joblib`.

## 5. Archivos de evidencia
- `predicciones_prueba.csv`: precio real vs predicho de los 200 vehiculos de prueba
- `validacion_cruzada.csv`: R2 de cada particion de la validacion cruzada
- `experimento_nodos_mlp.csv`: resultados de la red neuronal con cada cantidad de nodos
- `graficas/comparacion_r2.png`, `graficas/real_vs_predicho.png`, `graficas/distribucion_error.png`, `graficas/mlp_nodos.png`
- `log_entrenamiento.txt`: salida completa de la consola (si se uso `ejecutar_entrenamiento.py`)

> Nota: los precios del dataset son sinteticos (ver `pipeline/paso1_generar_precios.py`).
