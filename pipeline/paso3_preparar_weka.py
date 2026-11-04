"""
IDEALE - PASO 3: preparar los archivos para la Red Neuronal en Weka.

Convierte el precio en rangos (Barato / Medio / Caro) porque en Weka Web
la Red Neuronal (MLP) solo esta disponible en Clasificacion.
Cada rango tiene aproximadamente la misma cantidad de carros (terciles).

Entrada : data/weka/dataset_ideale_con_precio.arff
Salida  : data/weka/dataset_ideale_precio_rango.arff
          data/weka/dataset_ideale_precio_rango_sin_modelo.arff  (el que se usa en Weka)
"""
import pandas as pd

from config import ARFF_PRECIO as ORIGEN
from config import ARFF_RANGO as DESTINO
from config import ARFF_RANGO_SIN_MODELO as DESTINO_SIN_MODELO

RANGOS = ["Barato", "Medio", "Caro"]


def main():
    lineas = ORIGEN.read_text(encoding="utf-8").splitlines()
    inicio = next(i for i, l in enumerate(lineas) if l.strip().lower() == "@data")
    encabezado, datos = lineas[:inicio], [l for l in lineas[inicio + 1:] if l.strip()]

    precios = pd.Series([float(l.rsplit(",", 1)[1]) for l in datos])
    rango, cortes = pd.qcut(precios, q=3, labels=RANGOS, retbins=True)

    salida = []
    for l in encabezado:
        if l.lower().startswith("@relation"):
            l = "@relation ideale_carros_precio_rango"
        elif l.lower().startswith("@attribute precio"):
            l = "@attribute precio {" + ",".join(f"'{r}'" for r in RANGOS) + "}"
        salida.append(l)
    salida.append("@data")
    salida += [f"{l.rsplit(',', 1)[0]},'{r}'" for l, r in zip(datos, rango)]

    DESTINO.write_text("\n".join(salida) + "\n", encoding="utf-8")

    # Version liviana sin la columna "modelo" (59 valores) para que la
    # red neuronal entrene dentro del limite de tiempo de Weka Web
    sin_modelo = []
    for l in salida:
        if l.lower().startswith("@attribute modelo"):
            continue
        if l.startswith("'"):
            partes = l.split(",")
            l = ",".join(partes[:1] + partes[2:])
        sin_modelo.append(l)
    DESTINO_SIN_MODELO.write_text("\n".join(sin_modelo) + "\n", encoding="utf-8")

    print(f"Archivo creado: {DESTINO}")
    print(f"Archivo creado: {DESTINO_SIN_MODELO}")
    for i, r in enumerate(RANGOS):
        n = (rango == r).sum()
        print(f"  {r:7s} ${cortes[i]:>14,.0f} - ${cortes[i + 1]:>14,.0f}  ({n} carros)")


if __name__ == "__main__":
    main()
