"""
IDEALE - EXTRA: graficas de la red neuronal entrenada en Weka.

Entrada : evidencias/weka/resultados_weka_completos.csv  (metricas copiadas de Weka)
Salida  : evidencias/graficas/weka_exactitud_nodos.png
          evidencias/graficas/weka_matriz_confusion.png   (mejor configuracion)
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import EVIDENCIAS, GRAFICAS

RANGOS = ["Barato", "Medio", "Caro"]
MARINO, CLARO = "#0f2742", "#a9bccf"


def etiqueta(h: str) -> str:
    return f"{h} nodos" if "," not in h else f"{h}\n(2 capas)"


def main():
    df = pd.read_csv(EVIDENCIAS / "weka" / "resultados_weka_completos.csv",
                     dtype={"hiddenLayers": str})
    mejor = df["Accuracy (%)"].idxmax()

    # --- Exactitud por configuracion ---
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    colores = [MARINO if i == mejor else CLARO for i in df.index]
    barras = ax.bar([etiqueta(h) for h in df["hiddenLayers"]], df["Accuracy (%)"],
                    color=colores, width=0.6)
    for b, v in zip(barras, df["Accuracy (%)"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.5, f"{v:.2f} %", ha="center",
                fontsize=10, fontweight="bold", color=MARINO)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Exactitud (%)")
    ax.set_xlabel("Nodos en la capa oculta (hiddenLayers)")
    ax.set_title("Red neuronal (MLP) en Weka: exactitud según los nodos")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(GRAFICAS / "weka_exactitud_nodos.png", dpi=150)
    plt.close(fig)

    # --- Matriz de confusion de la mejor configuracion ---
    fila = df.loc[mejor]
    m = np.array([[fila[f"{r}->{p}"] for p in RANGOS] for r in RANGOS], dtype=int)
    fig, ax = plt.subplots(figsize=(4.6, 3.9))
    ax.imshow(m, cmap="Blues")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, m[i, j], ha="center", va="center", fontsize=13,
                    fontweight="bold", color="white" if m[i, j] > m.max() / 2 else MARINO)
    ax.set_xticks(range(3), RANGOS)
    ax.set_yticks(range(3), RANGOS)
    ax.set_xlabel("Segmento predicho")
    ax.set_ylabel("Segmento real")
    ax.set_title(f"Matriz de confusión - {fila['hiddenLayers']} nodos")
    fig.tight_layout()
    fig.savefig(GRAFICAS / "weka_matriz_confusion.png", dpi=150)
    plt.close(fig)

    # --- Recall por segmento (para el analisis) ---
    for _, f in df.iterrows():
        aciertos = [f[f"{r}->{r}"] / sum(f[f"{r}->{p}"] for p in RANGOS) * 100 for r in RANGOS]
        print(f"{f['hiddenLayers']:>5} nodos | " + " | ".join(
            f"{r}: {a:.1f} %" for r, a in zip(RANGOS, aciertos)))
    print(f"Mejor: {df.loc[mejor, 'hiddenLayers']} nodos ({df.loc[mejor, 'Accuracy (%)']:.2f} %)")


if __name__ == "__main__":
    main()
