"""
IDEALE - PASO 2: preparar datos, entrenar, comparar y guardar el mejor modelo.

Sigue CRISP-DM:  Preparacion -> Modelado -> Evaluacion (MAE, RMSE, R2)

Entrada : data/dataset_ideale_con_precio.csv
Salida  : modelo/      modelo_ideale.joblib, catalogo.json, comparacion_modelos.csv
          evidencias/  reporte_entrenamiento.md, predicciones_prueba.csv,
                       validacion_cruzada.csv, graficas/*.png
"""
import hashlib
import json
import platform
import time
from datetime import datetime

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import (ANIO_ACTUAL, CATALOGO, COMPARACION, CSV, EVIDENCIAS,
                    EXPERIMENTO_NODOS, GRAFICAS, MODELO, MODELO_DIR, PREDICCIONES,
                    REPORTE, SEED, VALIDACION_CRUZADA)

CATEGORICAS = ["marca", "modelo", "combustible", "transmision", "estado"]
NUMERICAS = ["antiguedad", "kilometraje"]


# =================================================================== 1. DATOS
def preparar_datos() -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(CSV)
    info = {"registros_cargados": len(df),
            # Huella del archivo: prueba exactamente que datos se usaron
            "sha256_dataset": hashlib.sha256(CSV.read_bytes()).hexdigest()[:16]}
    print(f"Registros cargados: {len(df)}")

    # --- Limpieza ---
    df = df.drop_duplicates().dropna()
    df = df[(df["kilometraje"] >= 0) & (df["precio"] > 0)]
    info["registros_limpios"] = len(df)
    print(f"Registros tras limpieza: {len(df)} "
          f"(eliminados: {info['registros_cargados'] - len(df)})")

    # --- Variable derivada: antiguedad del vehiculo ---
    df["antiguedad"] = ANIO_ACTUAL - df["anio"]
    return df, info


# ================================================================= 2. MODELOS
def pipe(regresor):
    """Preparacion de datos + regresor, entrenado sobre log(precio)."""
    prep = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
            ("num", StandardScaler(), NUMERICAS),
        ]
    )
    # Se entrena sobre log(precio): los precios son muy asimetricos
    # y asi el error es proporcional (no favorece solo a los carros caros).
    return TransformedTargetRegressor(
        regressor=Pipeline([("prep", prep), ("reg", regresor)]),
        func=np.log1p,
        inverse_func=np.expm1,
    )


def red_neuronal(nodos: tuple):
    """Perceptron multicapa (MLP). `nodos` = nodos por capa oculta, ej. (10,) o (10, 5)."""
    mlp = MLPRegressor(
        hidden_layer_sizes=nodos, activation="relu", solver="adam",
        alpha=1e-3,                 # regularizacion: evita memorizar los datos
        learning_rate_init=1e-3,
        max_iter=3000,
        early_stopping=True,        # se detiene cuando deja de mejorar
        validation_fraction=0.15, n_iter_no_change=50,
        random_state=SEED,
    )
    # La red aprende mejor si el objetivo (log del precio) tambien esta estandarizado
    return TransformedTargetRegressor(regressor=mlp, transformer=StandardScaler())


def construir_modelos(nodos_mlp: tuple) -> dict:
    return {
        "Regresion lineal": pipe(LinearRegression()),
        "Random Forest": pipe(
            RandomForestRegressor(n_estimators=300, random_state=SEED, n_jobs=-1)
        ),
        "Gradient Boosting": pipe(
            GradientBoostingRegressor(n_estimators=400, max_depth=3,
                                      learning_rate=0.05, random_state=SEED)
        ),
        "Red neuronal (MLP)": pipe(red_neuronal(nodos_mlp)),
    }


# ======================================================= 3. EXPERIMENTO NODOS
CONFIG_NODOS = [(3,), (5,), (10,), (20,), (50,), (10, 5), (20, 10)]


def experimento_nodos(X_tr, X_te, y_tr, y_te, kfold) -> tuple[pd.DataFrame, tuple]:
    """Prueba la red neuronal con distinta cantidad de nodos en la capa oculta.

    La mejor configuracion se elige con la validacion cruzada (solo datos de
    entrenamiento), para no "hacer trampa" mirando los datos de prueba.
    """
    filas = []
    for nodos in CONFIG_NODOS:
        modelo = pipe(red_neuronal(nodos))
        cv = cross_val_score(modelo, X_tr, y_tr, cv=kfold, scoring="r2")
        inicio = time.perf_counter()
        modelo.fit(X_tr, y_tr)
        segundos = time.perf_counter() - inicio
        pred = modelo.predict(X_te)
        filas.append({
            "Nodos": ",".join(map(str, nodos)),
            "Capas ocultas": len(nodos),
            "R2 CV (media)": cv.mean(),
            "R2 prueba": r2_score(y_te, pred),
            "MAE prueba (COP)": mean_absolute_error(y_te, pred),
            "Epocas": modelo.regressor_.named_steps["reg"].regressor_.n_iter_,
            "Tiempo (s)": segundos,
        })
        f = filas[-1]
        print(f"  MLP {f['Nodos']:>6} nodos  R2 CV={f['R2 CV (media)']:.4f}  "
              f"R2 prueba={f['R2 prueba']:.4f}  MAE={f['MAE prueba (COP)']:>12,.0f}  "
              f"({f['Epocas']} epocas, {segundos:.1f}s)")

    tabla = pd.DataFrame(filas)
    mejor = CONFIG_NODOS[int(tabla["R2 CV (media)"].idxmax())]
    print(f"  >>> Mejor red neuronal: {','.join(map(str, mejor))} nodos\n")
    return tabla, mejor


# ============================================================== 4. EVALUACION
def entrenar_y_evaluar(X_tr, X_te, y_tr, y_te, kfold, nodos_mlp):
    resultados, cv_filas, entrenados = [], [], {}

    for nombre, modelo in construir_modelos(nodos_mlp).items():
        # Validacion cruzada (5 particiones) sobre el conjunto de entrenamiento
        cv = cross_val_score(modelo, X_tr, y_tr, cv=kfold, scoring="r2")
        cv_filas += [{"Modelo": nombre, "Particion": i + 1, "R2": r2}
                     for i, r2 in enumerate(cv)]

        inicio = time.perf_counter()
        modelo.fit(X_tr, y_tr)
        segundos = time.perf_counter() - inicio
        pred = modelo.predict(X_te)

        fila = {
            "Modelo": nombre,
            "MAE (COP)": mean_absolute_error(y_te, pred),
            "RMSE (COP)": np.sqrt(mean_squared_error(y_te, pred)),
            "R2": r2_score(y_te, pred),
            "R2 CV (media)": cv.mean(),
            "R2 CV (desv.)": cv.std(),
            "Tiempo (s)": segundos,
        }
        resultados.append(fila)
        entrenados[nombre] = (modelo, pred)
        print(f"{nombre:18s} MAE={fila['MAE (COP)']:>12,.0f}  "
              f"RMSE={fila['RMSE (COP)']:>12,.0f}  R2={fila['R2']:.4f}  "
              f"CV={cv.mean():.4f}±{cv.std():.4f}  ({segundos:.2f}s)")

    tabla = pd.DataFrame(resultados).sort_values("R2", ascending=False)
    return tabla, pd.DataFrame(cv_filas), entrenados


# =============================================================== 5. GRAFICAS
def grafica_nodos(exp: pd.DataFrame, mejor: tuple):
    """R2 (validacion cruzada) y MAE de la red neuronal segun los nodos."""
    etiqueta = [n if "," not in n else n.replace(",", "+") + "\n2 capas" for n in exp["Nodos"]]
    colores = ["#0f2742" if n == ",".join(map(str, mejor)) else "#a9bccf"
               for n in exp["Nodos"]]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, col, titulo, fmt in [
        (a1, "R2 CV (media)", "R2 en validacion cruzada (mas alto = mejor)", "{:.3f}"),
        (a2, "MAE prueba (COP)", "Error promedio en prueba (millones COP)", "{:.1f}"),
    ]:
        valores = exp[col] / (1e6 if "MAE" in col else 1)
        barras = ax.bar(etiqueta, valores, color=colores, width=0.6)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, v, fmt.format(v), ha="center",
                    va="bottom", fontsize=9, fontweight="bold", color="#0f2742")
        ax.set_title(titulo, fontsize=10)
        ax.set_xlabel("Nodos en la capa oculta")
        ax.tick_params(axis="x", labelsize=8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
    a1.set_ylim(max(0, exp["R2 CV (media)"].min() - 0.05), 1.0)
    a2.set_ylim(0, exp["MAE prueba (COP)"].max() / 1e6 * 1.2)
    fig.suptitle("Red neuronal (MLP) en Python: efecto del numero de nodos", fontsize=11)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "mlp_nodos.png", dpi=150)
    plt.close(fig)


def guardar_graficas(tabla, y_te, mejor_pred, mejor_nombre):
    # Precio real vs predicho
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_te / 1e6, mejor_pred / 1e6, alpha=0.6, s=18, color="#1f4e79")
    lim = [0, max(y_te.max(), mejor_pred.max()) / 1e6 * 1.05]
    ax.plot(lim, lim, "--", color="#8e3b46", label="Prediccion perfecta")
    ax.set_xlabel("Precio real (millones COP)")
    ax.set_ylabel("Precio predicho (millones COP)")
    ax.set_title(f"Real vs predicho - {mejor_nombre}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAFICAS / "real_vs_predicho.png", dpi=150)
    plt.close(fig)

    # Comparacion de R2
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.barh(tabla["Modelo"], tabla["R2"], color="#1f4e79")
    ax.set_xlim(min(0.5, tabla["R2"].min() - 0.05), 1.0)
    ax.set_xlabel("R2 (mas alto = mejor)")
    ax.set_title("Comparacion de modelos")
    fig.tight_layout()
    fig.savefig(GRAFICAS / "comparacion_r2.png", dpi=150)
    plt.close(fig)

    # Distribucion del error en el conjunto de prueba
    errores = (mejor_pred - y_te) / 1e6
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.hist(errores, bins=30, color="#1f4e79", edgecolor="white")
    ax.axvline(0, color="#8e3b46", linestyle="--")
    ax.set_xlabel("Error de prediccion (millones COP)")
    ax.set_ylabel("Vehiculos")
    ax.set_title(f"Distribucion del error - {mejor_nombre}")
    fig.tight_layout()
    fig.savefig(GRAFICAS / "distribucion_error.png", dpi=150)
    plt.close(fig)


# ================================================================ 6. REPORTE
def escribir_reporte(fecha, info, n_tr, n_te, tabla, mejor_nombre, exp, nodos_mlp):
    def md(t: pd.DataFrame) -> str:
        filas = ["| " + " | ".join(t.columns) + " |",
                 "|" + "---|" * len(t.columns)]
        filas += ["| " + " | ".join(str(v) for v in r) + " |" for r in t.values]
        return "\n".join(filas)

    vista = tabla.copy()
    for c in ["MAE (COP)", "RMSE (COP)"]:
        vista[c] = vista[c].map(lambda v: f"$ {v:,.0f}".replace(",", "."))
    for c in ["R2", "R2 CV (media)", "R2 CV (desv.)"]:
        vista[c] = vista[c].map(lambda v: f"{v:.4f}")
    vista["Tiempo (s)"] = vista["Tiempo (s)"].map(lambda v: f"{v:.2f}")

    vista_exp = exp.copy()
    vista_exp["MAE prueba (COP)"] = vista_exp["MAE prueba (COP)"].map(
        lambda v: f"$ {v:,.0f}".replace(",", "."))
    for c in ["R2 CV (media)", "R2 prueba"]:
        vista_exp[c] = vista_exp[c].map(lambda v: f"{v:.4f}")
    vista_exp["Tiempo (s)"] = vista_exp["Tiempo (s)"].map(lambda v: f"{v:.1f}")

    REPORTE.write_text(f"""# Reporte de entrenamiento - IDEALE

- **Fecha de ejecucion:** {fecha}
- **Equipo:** {platform.node()} · Python {platform.python_version()} · scikit-learn {sklearn.__version__}

## 1. Datos
- Archivo: `data/{CSV.name}` (huella SHA-256: `{info['sha256_dataset']}`)
- Registros cargados: {info['registros_cargados']}
- Registros tras limpieza: {info['registros_limpios']}
- Variables de entrada: {', '.join(CATEGORICAS + NUMERICAS)}
- Variable objetivo: precio (COP)

## 2. Division de los datos
- Entrenamiento: {n_tr} vehiculos (80 %)
- Prueba: {n_te} vehiculos (20 %), nunca vistos durante el entrenamiento
- Semilla aleatoria: {SEED} (los resultados se pueden repetir)
- Validacion cruzada: 5 particiones sobre el conjunto de entrenamiento

## 3. Experimento: nodos de la red neuronal (MLP)
Se probo la red con distinta cantidad de nodos en la capa oculta. La mejor
configuracion se eligio por el R2 de la validacion cruzada (solo datos de
entrenamiento).

{md(vista_exp)}

**Red neuronal elegida: {','.join(map(str, nodos_mlp))} nodos**

## 4. Comparacion de modelos
{md(vista)}

**Modelo seleccionado (mayor R2): {mejor_nombre}**
Se reentreno con todos los datos y se guardo en `modelo/{MODELO.name}`.

## 5. Archivos de evidencia
- `predicciones_prueba.csv`: precio real vs predicho de los {n_te} vehiculos de prueba
- `validacion_cruzada.csv`: R2 de cada particion de la validacion cruzada
- `experimento_nodos_mlp.csv`: resultados de la red neuronal con cada cantidad de nodos
- `graficas/comparacion_r2.png`, `graficas/real_vs_predicho.png`, `graficas/distribucion_error.png`, `graficas/mlp_nodos.png`
- `log_entrenamiento.txt`: salida completa de la consola (si se uso `ejecutar_entrenamiento.py`)

> Nota: los precios del dataset son sinteticos (ver `pipeline/paso1_generar_precios.py`).
""", encoding="utf-8")


# ================================================================== PRINCIPAL
def main():
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for carpeta in (MODELO_DIR, EVIDENCIAS, GRAFICAS):
        carpeta.mkdir(parents=True, exist_ok=True)

    df, info = preparar_datos()
    X = df[CATEGORICAS + NUMERICAS]
    y = df["precio"]

    # 80 % entrenamiento / 20 % prueba
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.20, random_state=SEED
    )
    print(f"Entrenamiento: {len(X_tr)} | Prueba: {len(X_te)}\n")
    kfold = KFold(n_splits=5, shuffle=True, random_state=SEED)

    # --- Experimento: cuantos nodos necesita la red neuronal ---
    print("Experimento de nodos - Red neuronal (MLP):")
    exp, nodos_mlp = experimento_nodos(X_tr, X_te, y_tr, y_te, kfold)
    exp.to_csv(EXPERIMENTO_NODOS, index=False)
    grafica_nodos(exp, nodos_mlp)

    print("Comparacion de modelos:")
    tabla, cv, entrenados = entrenar_y_evaluar(X_tr, X_te, y_tr, y_te, kfold, nodos_mlp)
    tabla[["Modelo", "MAE (COP)", "RMSE (COP)", "R2"]].to_csv(COMPARACION, index=False)
    cv.to_csv(VALIDACION_CRUZADA, index=False)

    # --- Seleccion del mejor modelo (mayor R2) ---
    mejor_nombre = tabla.iloc[0]["Modelo"]
    mejor_modelo, mejor_pred = entrenados[mejor_nombre]
    print(f"\n>>> Mejor modelo: {mejor_nombre}")

    # --- Evidencia: predicciones sobre los carros de prueba ---
    pred = df.loc[X_te.index, ["marca", "modelo", "anio", "kilometraje", "estado"]]
    pred = pred.assign(precio_real=y_te.values, precio_predicho=mejor_pred.round(-3),
                       error=(mejor_pred - y_te.values).round(-3))
    pred["error_%"] = (pred["error"] / pred["precio_real"] * 100).round(1)
    pred.to_csv(PREDICCIONES, index=False)

    guardar_graficas(tabla, y_te, mejor_pred, mejor_nombre)

    # Se reentrena con TODOS los datos para la aplicacion final
    mejor_modelo.fit(X, y)
    joblib.dump(mejor_modelo, MODELO)

    # --- Catalogo para la app (marcas -> modelos, rangos, etc.) ---
    catalogo = {
        "modelos_por_marca": {
            m: sorted(g["modelo"].unique().tolist())
            for m, g in df.groupby("marca")
        },
        "combustibles": sorted(df["combustible"].unique().tolist()),
        "transmisiones": sorted(df["transmision"].unique().tolist()),
        "estados": ["Nuevo 0 km", "Buen estado", "Segunda mano",
                    "Medio estado", "Mal estado"],
        "anio_min": int(df["anio"].min()),
        "anio_max": int(df["anio"].max()),
        "km_max": int(df["kilometraje"].max()),
        "mejor_modelo": mejor_nombre,
        "anio_actual": ANIO_ACTUAL,
        "fecha_entrenamiento": fecha,
        "nodos_red_neuronal": ",".join(map(str, nodos_mlp)),
    }
    CATALOGO.write_text(json.dumps(catalogo, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    escribir_reporte(fecha, info, len(X_tr), len(X_te), tabla, mejor_nombre, exp, nodos_mlp)
    print(f"\nModelo guardado en:    {MODELO}")
    print(f"Evidencias guardadas en: {EVIDENCIAS}")


if __name__ == "__main__":
    main()
