# PUBLICACIÓN DE IDEALE EN STREAMLIT

1. Crea un repositorio nuevo en https://github.com/new, por ejemplo `ideale-vehiculos`.
2. En GitHub selecciona «uploading an existing file» o Add file > Upload files.
3. DESCOMPRIME este ZIP y carga el contenido de su carpeta raíz, conservando todas las subcarpetas. El archivo `app.py` debe quedar en la raíz de GitHub.
4. Confirma los archivos («Commit changes»).
5. En https://share.streamlit.io > Create app > Yup, I have an app, selecciona tu repositorio, `main` y `app.py`.
6. En Advanced settings selecciona Python 3.12 y haz clic en Deploy.

Nota: Streamlit Community Cloud no instala ZIP directamente. Necesita el proyecto en un repositorio de GitHub.
No es necesario reentrenar: `modelo/modelo_ideale.joblib` está incluido.
Si el arranque falla, revisa los logs de Streamlit (dependencias y compatibilidad).
