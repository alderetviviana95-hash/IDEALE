"""
IDEALE - PASO 1: generar la columna `precio` (SINTETICA) para el dataset.

Entrada : data/original/dataset_ideale_weka_1000.arff  (sin precio)
Salida  : data/dataset_ideale_con_precio.csv
          data/weka/dataset_ideale_con_precio.arff

El ARFF original no trae precio, asi que lo simulamos con una formula basada
en como se comporta el mercado colombiano de usados:

  precio = precio_nuevo_del_modelo
           x depreciacion por antiguedad (exponencial)
           x ajuste por kilometraje (respecto al km "esperado" para su edad)
           x ajuste por estado
           x ajuste por transmision / combustible
           x ruido aleatorio (~6 %)

IMPORTANTE para el informe: estos precios son SIMULADOS (valores aproximados
en pesos colombianos, escala 2025-2026), no precios reales de mercado.
"""
import numpy as np
import pandas as pd
from scipy.io import arff

from config import ANIO_ACTUAL, SEED
from config import ARFF_ORIGINAL as ARFF_IN
from config import ARFF_PRECIO as ARFF_OUT
from config import CSV as CSV_OUT

# Precio aproximado de un vehiculo NUEVO de cada modelo (millones de COP).
PRECIO_NUEVO = {
    "Accent": 75, "Accord": 160, "Amarok": 210, "BT-50": 170, "CR-V": 190,
    "CX-30": 150, "CX-5": 170, "Captiva": 125, "Cerato": 100, "City": 85,
    "Civic": 130, "Corolla": 120, "Creta": 105, "Duster": 95, "EcoSport": 90,
    "Elantra": 110, "Escape": 150, "Explorer": 270, "Fiesta": 70, "Fit": 75,
    "Focus": 95, "Fortuner": 260, "Frontier": 190, "Gol": 55, "HR-V": 140,
    "Hilux": 220, "Jetta": 120, "Joy": 52, "Kicks": 100, "Koleos": 150,
    "Kwid": 45, "Logan": 62, "March": 55, "Mazda 2": 75, "Mazda 3": 115,
    "Mazda 6": 160, "Onix": 70, "Picanto": 52, "Polo": 85, "Prado": 400,
    "RAV4": 190, "Ranger": 200, "Rio": 75, "Sail": 55, "Sandero": 62,
    "Santa Fe": 220, "Seltos": 110, "Sentra": 95, "Sorento": 230, "Spark": 48,
    "Sportage": 140, "Stepway": 75, "Tiguan": 170, "Tracker": 100,
    "Tucson": 140, "Versa": 68, "X-Trail": 165, "Yaris": 70, "i10": 50,
}

# Camionetas y pickups conservan mejor su valor.
RESISTENTES = {"Prado", "Hilux", "Fortuner", "Ranger", "Amarok", "Frontier",
               "BT-50", "RAV4", "CR-V", "Explorer", "Santa Fe", "Sorento"}
PICKUPS_SUV_DIESEL = RESISTENTES | {"Koleos", "Captiva"}

FACTOR_ESTADO = {
    "Nuevo 0 km": 1.00,
    "Buen estado": 1.00,
    "Segunda mano": 0.95,
    "Medio estado": 0.88,
    "Mal estado": 0.72,
}


def cargar_arff() -> pd.DataFrame:
    data, _ = arff.loadarff(ARFF_IN)
    df = pd.DataFrame(data)
    for col in df.select_dtypes(include="object"):
        df[col] = df[col].str.decode("utf-8")
    return df


def calcular_precio(fila, rng) -> float:
    base = PRECIO_NUEVO[fila["modelo"]] * 1_000_000
    edad = max(ANIO_ACTUAL - int(fila["anio"]), 0)

    # 1) Depreciacion por edad (se pierde ~9-12 % por ano, con piso de 18 %).
    tasa = 0.91 if fila["modelo"] in RESISTENTES else 0.885
    f_edad = max(tasa ** edad, 0.18)

    # 2) Kilometraje: se compara con ~15.000 km por ano de uso.
    km_esperado = 15_000 * edad
    f_km = float(np.clip(np.exp(-2.2e-6 * (fila["kilometraje"] - km_esperado)),
                         0.68, 1.15))

    # 3) Estado del vehiculo.
    f_estado = FACTOR_ESTADO[fila["estado"]]

    # 4) Transmision y combustible.
    f_trans = 1.04 if fila["transmision"] == "Automatico" else 1.0
    f_comb = 1.0
    if fila["combustible"] == "Diesel":
        f_comb = 1.05 if fila["modelo"] in PICKUPS_SUV_DIESEL else 0.97

    # 5) Ruido de mercado (lognormal, ~6 %).
    ruido = rng.lognormal(mean=0.0, sigma=0.06)

    precio = base * f_edad * f_km * f_estado * f_trans * f_comb * ruido
    precio = max(precio, 5_000_000)  # ningun carro vale menos de 5 M
    return round(precio / 100_000) * 100_000  # redondeo a 100.000


def guardar_arff(df: pd.DataFrame) -> None:
    """Escribe un ARFF con la columna precio para poder abrirlo en Weka."""
    def nominal(col):
        vals = ",".join(f"'{v}'" for v in sorted(df[col].unique()))
        return "{" + vals + "}"

    lineas = ["@relation ideale_carros_con_precio", ""]
    for col in ["marca", "modelo"]:
        lineas.append(f"@attribute {col} {nominal(col)}")
    lineas.append("@attribute anio numeric")
    for col in ["combustible", "transmision"]:
        lineas.append(f"@attribute {col} {nominal(col)}")
    lineas.append("@attribute kilometraje numeric")
    lineas.append(f"@attribute estado {nominal('estado')}")
    lineas.append("@attribute precio numeric")
    lineas += ["", "@data"]
    for _, r in df.iterrows():
        lineas.append(
            f"'{r.marca}','{r.modelo}',{int(r.anio)},'{r.combustible}',"
            f"'{r.transmision}',{int(r.kilometraje)},'{r.estado}',{int(r.precio)}"
        )
    ARFF_OUT.write_text("\n".join(lineas), encoding="utf-8")


def main():
    rng = np.random.default_rng(SEED)
    df = cargar_arff()
    df["anio"] = df["anio"].astype(int)
    df["kilometraje"] = df["kilometraje"].astype(int)
    df["precio"] = df.apply(lambda f: calcular_precio(f, rng), axis=1).astype(int)

    df.to_csv(CSV_OUT, index=False)
    guardar_arff(df)

    print(f"Registros: {len(df)}")
    print(f"CSV  -> {CSV_OUT}")
    print(f"ARFF -> {ARFF_OUT}")
    print("\nResumen del precio (COP):")
    print(df["precio"].describe().apply(lambda x: f"{x:,.0f}"))
    print("\nEjemplos:")
    print(df.sample(8, random_state=1).to_string(index=False))


if __name__ == "__main__":
    main()
