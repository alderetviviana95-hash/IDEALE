"""
IDEALE - EXTRA: crea una imagen de relleno para cada marca/modelo.

Genera  imagenes/<marca>_<modelo>.png  (ej: toyota_corolla.png).
Luego puedes reemplazar cualquiera por una foto real con el MISMO nombre
(.jpg, .jpeg, .png o .webp). Si ya existe una imagen, este script NO la toca.
"""
import json
import hashlib

from PIL import Image, ImageDraw, ImageFont

from config import CATALOGO as RUTA_CATALOGO
from config import IMAGENES as CARPETA

CARPETA.mkdir(exist_ok=True)
CATALOGO = json.loads(RUTA_CATALOGO.read_text(encoding="utf-8"))

ANCHO, ALTO = 800, 450


def nombre_archivo(marca: str, modelo: str) -> str:
    return f"{marca}_{modelo}".lower().replace(" ", "_").replace("-", "_")


def fuente(tam: int):
    for nombre in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def color_marca(marca: str):
    h = int(hashlib.md5(marca.encode()).hexdigest(), 16)
    return ((h >> 16) % 150 + 50, (h >> 8) % 150 + 50, h % 150 + 50)


def dibujar(marca: str, modelo: str) -> Image.Image:
    c = color_marca(marca)
    img = Image.new("RGB", (ANCHO, ALTO), (236, 240, 245))
    d = ImageDraw.Draw(img)

    # suelo
    d.rectangle([0, 330, ANCHO, ALTO], fill=(210, 215, 222))

    # carroceria
    d.rounded_rectangle([140, 220, 660, 320], radius=35, fill=c)
    # cabina
    d.polygon([(250, 220), (310, 150), (500, 150), (570, 220)], fill=c)
    # ventanas
    claro = (220, 235, 248)
    d.polygon([(275, 218), (322, 163), (390, 163), (390, 218)], fill=claro)
    d.polygon([(405, 218), (405, 163), (492, 163), (545, 218)], fill=claro)
    # luces
    d.rounded_rectangle([630, 240, 660, 262], radius=8, fill=(255, 235, 150))
    d.rounded_rectangle([140, 240, 165, 262], radius=8, fill=(230, 80, 80))
    # ruedas
    for x in (240, 560):
        d.ellipse([x - 48, 275, x + 48, 371], fill=(40, 40, 45))
        d.ellipse([x - 24, 299, x + 24, 347], fill=(185, 190, 198))

    # texto
    d.text((ANCHO // 2, 45), marca.upper(), font=fuente(34),
           fill=(70, 80, 95), anchor="mm")
    d.text((ANCHO // 2, 95), modelo, font=fuente(48),
           fill=(25, 35, 50), anchor="mm")
    d.text((ANCHO // 2, 425), "Imagen de referencia", font=fuente(18),
           fill=(120, 130, 145), anchor="mm")
    return img


def main():
    creadas = existentes = 0
    for marca, modelos in CATALOGO["modelos_por_marca"].items():
        for modelo in modelos:
            base = nombre_archivo(marca, modelo)
            if any((CARPETA / f"{base}{ext}").exists()
                   for ext in (".jpg", ".jpeg", ".png", ".webp")):
                existentes += 1
                continue
            dibujar(marca, modelo).save(CARPETA / f"{base}.png")
            creadas += 1
    print(f"Imagenes creadas: {creadas} | ya existian: {existentes}")
    print(f"Carpeta: {CARPETA}")


if __name__ == "__main__":
    main()
