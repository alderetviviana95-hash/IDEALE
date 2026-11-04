# Cómo publicar IDEALE en internet (Streamlit Community Cloud)

Al terminar tendrás un link público (por ejemplo `https://venta-carros.streamlit.app`)
que cualquiera puede abrir sin instalar nada.

## Qué necesitas
- Una cuenta gratuita de **GitHub** (https://github.com/signup).
- Esta carpeta (`proyecto_venta_carros`). **No** se sube la carpeta `venv`; el
  archivo `.gitignore` ya la excluye.

## Paso 1. Subir el proyecto a GitHub

### Opción A (la más fácil): GitHub Desktop
1. Instalar **GitHub Desktop**: https://desktop.github.com e iniciar sesión.
2. *File → Add local repository…* y elegir la carpeta `proyecto_venta_carros`.
   Si dice que no es un repositorio, pulsar **create a repository** y *Create repository*.
3. Escribir un mensaje (por ejemplo `Proyecto IDEALE`) y pulsar **Commit to main**.
4. Pulsar **Publish repository**, ponerle nombre (por ejemplo `venta-carros`) y
   publicar. Se puede dejar **privado**: Streamlit también lo lee.

### Opción B: desde la página de GitHub (sin instalar nada)
1. En GitHub: **New repository** → nombre `venta-carros` → *Create repository*.
2. En la página que aparece, pulsar el enlace **uploading an existing file**.
3. GitHub acepta máximo **100 archivos por subida**, así que se hace en dos tandas.
   Ya están preparadas en la carpeta `IA\5_Subir_a_GitHub`:
   - **Tanda 1:** abrir `lote_1_codigo`, seleccionar todo (`Ctrl + A`) y arrastrarlo a
     la página. Esperar a que carguen los 46 archivos y pulsar **Commit changes**.
   - **Tanda 2:** en el repositorio, *Add file → Upload files*; abrir `lote_2_imagenes`,
     arrastrar la carpeta **`imagenes`** y pulsar **Commit changes**.

> Importante: `app.py` debe quedar **en la raíz del repositorio** (no dentro de otra carpeta).

## Paso 2. Publicar la app
1. Entrar a **https://share.streamlit.io** e iniciar sesión con GitHub.
2. Pulsar **Create app** → *Deploy a public app from GitHub*.
3. Elegir:
   - **Repository:** `tu-usuario/venta-carros`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Abrir **Advanced settings** y elegir **Python 3.11**.
5. Pulsar **Deploy**. La primera vez tarda unos 3 a 5 minutos en instalar las librerías.

## Paso 3. Probar
- Abrir el link, valorar un carro (por ejemplo un Toyota Corolla 2018) y revisar las
  4 pestañas.
- Copiar el link y ponerlo en el informe y en la diapositiva de la aplicación.

## Si algo falla
| Problema | Solución |
|---|---|
| `No module named ...` | Revisar que `requirements.txt` esté en la raíz del repositorio. |
| Error al cargar el modelo | Elegir **Python 3.11** en *Advanced settings* (las versiones de `requirements.txt` están fijadas para que el modelo cargue bien). |
| `FileNotFoundError` | Verificar que se subieron las carpetas `modelo/`, `data/`, `evidencias/` e `imagenes/`. |
| La app se "duerme" | Es normal en el plan gratuito tras unos días sin uso: abrir el link y pulsar *Wake up*. |

## Notas
- Los archivos de `evidencias/` (reporte y registro del entrenamiento) incluyen el
  nombre del computador donde se entrenó. Si el repositorio es **público**, conviene
  saberlo; en un repositorio **privado** no hay problema.
- Los cambios que se hagan desde la app (por ejemplo, guardar resultados de Weka) no
  son permanentes en la nube: se pierden cuando la app se reinicia.
- Para actualizar la app: cambiar los archivos, hacer *Commit* y *Push*; Streamlit
  se actualiza solo.
