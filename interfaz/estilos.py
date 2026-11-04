"""
Colores y hoja de estilos (CSS) de la aplicacion.
El tema base (fuente, fondo, barra lateral) esta en .streamlit/config.toml.
"""
import streamlit as st

# Paleta corporativa: azul marino + tonos apagados para los segmentos
AZUL = "#1f4e79"
MARINO = "#0f2742"
GRIS = "#5b6b7d"
BORDE = "#d9dfe7"
COLORES = {"Barato": "#3f7a5e", "Medio": "#a5793a", "Caro": "#8e3b46"}


def aplicar_estilos() -> None:
    st.markdown(
        f"""
        <style>
        .block-container {{padding-top: 1.6rem; max-width: 1240px;}}
        h1, h2, h3, h4 {{letter-spacing: -.01em; font-weight: 600;}}

        /* ---- Encabezado ---- */
        .encabezado {{
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: wrap; gap: 18px; background: #fff;
            border: 1px solid {BORDE}; border-top: 4px solid {MARINO};
            border-radius: 6px; padding: 18px 26px; margin-bottom: 1.1rem;
        }}
        .marca-emp {{font-size: 1.6rem; font-weight: 700; color: {MARINO};
                     letter-spacing: .14em;}}
        .marca-emp small {{display: block; font-size: .8rem; font-weight: 500;
                           letter-spacing: .02em; color: {GRIS}; margin-top: 2px;}}
        .kpis {{display: flex; flex-wrap: wrap;}}
        .kpi {{padding: 0 22px; border-left: 1px solid {BORDE};}}
        .kpi b {{display: block; font-size: 1.15rem; color: {MARINO};}}
        .kpi span {{font-size: .72rem; color: {GRIS}; text-transform: uppercase;
                    letter-spacing: .06em;}}

        /* ---- Titulos de seccion ---- */
        .seccion {{font-size: .75rem; font-weight: 600; color: {GRIS};
                    text-transform: uppercase; letter-spacing: .08em;
                    margin-bottom: .3rem;}}

        /* ---- Tarjeta del precio estimado ---- */
        .precio-card {{
            background: #fff; border: 1px solid {BORDE}; border-left: 5px solid {AZUL};
            border-radius: 6px; padding: 20px 24px;
        }}
        .precio-card .etq {{font-size: .75rem; color: {GRIS}; text-transform: uppercase;
                            letter-spacing: .08em;}}
        .precio-card .valor {{font-size: 2.4rem; font-weight: 700; color: {MARINO};
                              line-height: 1.2; margin: 4px 0;}}
        .precio-card small {{color: {GRIS};}}
        .badge {{
            display: inline-block; border-radius: 3px; padding: 2px 10px;
            font-weight: 600; font-size: .75rem; color: #fff; letter-spacing: .04em;
            text-transform: uppercase;
        }}
        .barra {{height: 6px; border-radius: 3px; margin: 16px 0 6px 0; position: relative;
                 background: linear-gradient(90deg, {COLORES['Barato']},
                                             {COLORES['Medio']}, {COLORES['Caro']});}}
        .marca-barra {{position: absolute; top: -5px; width: 3px; height: 16px;
                       background: {MARINO}; border-radius: 1px;}}
        .franja {{
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: wrap; gap: 8px; background: {MARINO}; color: #dfe6ee;
            border-radius: 6px; padding: 12px 20px; margin: 4px 0 14px 0;
            font-size: .85rem;
        }}
        .franja b {{color: #fff; font-size: 1.15rem;}}
        .vacio {{
            background: #fff; border: 1px solid {BORDE}; border-radius: 6px;
            padding: 56px 24px; text-align: center; color: {GRIS};
        }}
        .vacio h4 {{color: {MARINO}; margin-bottom: .3rem;}}

        /* ---- Barra lateral ---- */
        .rango-fila {{display: flex; justify-content: space-between; align-items: center;
                      font-size: .85rem; padding: 6px 0;
                      border-bottom: 1px solid rgba(255,255,255,.08);}}
        .rango-valor {{white-space: nowrap; font-size: .78rem;}}
        [data-testid="stSidebar"] [data-testid="stSliderThumbValue"] {{color: #fff;}}

        /* ---- Metricas y pestanas ---- */
        [data-testid="stMetric"] {{background: #fff;}}
        [data-testid="stMetricValue"] > div {{font-size: 1.45rem; font-weight: 600;
                                              color: {MARINO};}}
        [data-testid="stMetricLabel"] p {{font-size: .75rem; text-transform: uppercase;
                                          letter-spacing: .06em; color: {GRIS};}}
        .stTabs [data-baseweb="tab-list"] {{gap: 4px; border-bottom: 1px solid {BORDE};}}
        .stTabs [data-baseweb="tab"] {{padding: 10px 18px; font-weight: 500;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def titulo_seccion(texto: str) -> None:
    st.markdown(f"<div class='seccion'>{texto}</div>", unsafe_allow_html=True)
