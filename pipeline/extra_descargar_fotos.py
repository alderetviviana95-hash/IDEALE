"""
IDEALE - EXTRA: descargar una foto real de cada modelo desde Wikimedia
(imagen principal del articulo de Wikipedia, licencia libre).

Guarda imagenes/<marca>_<modelo>.jpg y imagenes/creditos.csv (autor y
licencia de cada foto, para citarlas en el informe).
"""
import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from config import CATALOGO, CREDITOS, IMAGENES

API = "https://en.wikipedia.org/w/api.php"
COMMONS = "https://commons.wikimedia.org/w/api.php"
AGENTE = "IDEALE-proyecto-academico/1.0 (Python urllib)"

# Titulo del articulo cuando no coincide con "<marca> <modelo>"
TITULOS = {
    ("Mazda", "Mazda 2"): "Mazda2",
    ("Mazda", "Mazda 3"): "Mazda3",
    ("Mazda", "Mazda 6"): "Mazda6",
    ("Toyota", "Prado"): "Toyota Land Cruiser Prado",
    ("Renault", "Stepway"): "Dacia Sandero",
    ("Renault", "Sandero"): "Dacia Sandero",
    ("Renault", "Logan"): "Dacia Logan",
    ("Renault", "Duster"): "Dacia Duster",
    ("Chevrolet", "Joy"): "Chevrolet Prisma",
    ("Chevrolet", "Tracker"): "Chevrolet Trax",
    ("Chevrolet", "Captiva"): "Chevrolet Captiva",
}


def bajar(url: str) -> bytes:
    """Descarga con reintentos: Wikimedia responde 429 si se va muy rapido."""
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    for intento in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or intento == 4:
                raise
            time.sleep(10 * (intento + 1))


def pedir(url: str, params: dict) -> dict:
    return json.loads(bajar(f"{url}?{urllib.parse.urlencode(params)}"))


def imagen_principal(titulo: str):
    """(url_miniatura, nombre_archivo) de la imagen principal del articulo."""
    datos = pedir(API, {
        "action": "query", "format": "json", "redirects": 1, "titles": titulo,
        "prop": "pageimages", "piprop": "thumbnail|name", "pithumbsize": 900,
    })
    pagina = next(iter(datos["query"]["pages"].values()))
    if "thumbnail" not in pagina:
        return None, None
    return pagina["thumbnail"]["source"], pagina["pageimage"]


def credito(archivo: str) -> tuple:
    datos = pedir(COMMONS, {
        "action": "query", "format": "json", "titles": f"File:{archivo}",
        "prop": "imageinfo", "iiprop": "extmetadata",
    })
    pagina = next(iter(datos["query"]["pages"].values()))
    meta = pagina.get("imageinfo", [{}])[0].get("extmetadata", {})
    autor = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "Desconocido"))
    licencia = meta.get("LicenseShortName", {}).get("value", "Ver Wikimedia")
    return autor.strip(), licencia


def main():
    cat = json.loads(CATALOGO.read_text(encoding="utf-8"))
    # Si se vuelve a correr, conserva las fotos ya descargadas
    filas = []
    if CREDITOS.exists():
        with CREDITOS.open(encoding="utf-8") as f:
            filas = [r for r in csv.DictReader(f) if (IMAGENES / r["archivo"]).exists()]
    listos = {r["archivo"] for r in filas}

    for marca, modelos in cat["modelos_por_marca"].items():
        for modelo in modelos:
            titulo = TITULOS.get((marca, modelo), f"{marca} {modelo}")
            nombre = f"{marca}_{modelo}".lower().replace(" ", "_").replace("-", "_")
            if f"{nombre}.jpg" in listos:
                continue
            try:
                url, archivo = imagen_principal(titulo)
                if not url:
                    print(f"  SIN FOTO  {marca} {modelo} ({titulo})")
                    continue
                (IMAGENES / f"{nombre}.jpg").write_bytes(bajar(url))
                autor, licencia = credito(archivo)
                filas.append({"archivo": f"{nombre}.jpg", "marca": marca,
                              "modelo": modelo, "autor": autor, "licencia": licencia,
                              "fuente": f"https://commons.wikimedia.org/wiki/File:"
                                        f"{urllib.parse.quote(archivo)}"})
                print(f"  OK        {marca} {modelo}  <- {archivo}")
            except Exception as e:  # noqa: BLE001 - seguir con los demas
                print(f"  ERROR     {marca} {modelo}: {e}")
            time.sleep(3)

    with CREDITOS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print(f"\n{len(filas)} fotos descargadas. Creditos en: {CREDITOS}")


if __name__ == "__main__":
    main()
