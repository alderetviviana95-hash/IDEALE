"""
IDEALE - Ejecuta TODO el entrenamiento en orden y guarda la evidencia.

    python ejecutar_entrenamiento.py

Corre los pasos de la carpeta pipeline/ y copia toda la salida de la consola
(con fecha y hora) en evidencias/log_entrenamiento.txt.
"""
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PIPELINE = RAIZ / "pipeline"
LOG = RAIZ / "evidencias" / "log_entrenamiento.txt"

PASOS = [
    ("PASO 1 - Generar precios del dataset", "paso1_generar_precios.py"),
    ("PASO 2 - Entrenar y evaluar los modelos", "paso2_entrenar_modelo.py"),
    ("PASO 3 - Preparar archivos para Weka", "paso3_preparar_weka.py"),
]


def main():
    LOG.parent.mkdir(parents=True, exist_ok=True)
    inicio_total = time.perf_counter()

    with LOG.open("w", encoding="utf-8") as log:
        def escribir(texto=""):
            print(texto)
            log.write(texto + "\n")

        escribir("=" * 70)
        escribir("IDEALE - REGISTRO DE ENTRENAMIENTO")
        escribir(f"Inicio : {datetime.now():%Y-%m-%d %H:%M:%S}")
        escribir(f"Equipo : {platform.node()} | Python {platform.python_version()}")
        escribir("=" * 70)

        for titulo, script in PASOS:
            escribir(f"\n>>> {titulo}  ({datetime.now():%H:%M:%S})")
            escribir("-" * 70)
            inicio = time.perf_counter()
            res = subprocess.run(
                [sys.executable, str(PIPELINE / script)], cwd=PIPELINE,
                capture_output=True, text=True, encoding="utf-8",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            for linea in (res.stdout + res.stderr).rstrip().splitlines():
                escribir(linea)
            escribir(f"--- {script}: {'OK' if res.returncode == 0 else 'ERROR'} "
                     f"({time.perf_counter() - inicio:.1f} s)")
            if res.returncode != 0:
                escribir("\nEl entrenamiento se detuvo por un error.")
                sys.exit(res.returncode)

        escribir("\n" + "=" * 70)
        escribir(f"Fin    : {datetime.now():%Y-%m-%d %H:%M:%S} "
                 f"(total {time.perf_counter() - inicio_total:.1f} s)")
        escribir(f"Evidencias en: {LOG.parent}")
        escribir("=" * 70)


if __name__ == "__main__":
    main()
