import streamlit as st
from mod_filters import filtros_basicos, aplicar_filtros
from mod_pivot import crear_pivot
from mod_aggrid import render_grid, estilo_tabla
from colors import METSO_COLORS

# ==============================================================================
# CONFIG & LOGIN
# ==============================================================================
st.set_page_config(page_title="Calendario", layout="wide")

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("Login.py")

st.write(f"Bienvenido **{st.session_state.user.user.email}**")
st.title("Calendario de Servicios | Área de propuestas")


# ==============================================================================
# REPOSITORIOS
# ==============================================================================

from repositories import mano_obra_repo
df_mo = mano_obra_repo.obtener_todo_df()

# ==============================================================================
# CONSTANTES PARA PIVOTS Y MESES
# ==============================================================================
orden_meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

abrev_meses = {
    "Enero": "ENE", "Febrero": "FEB", "Marzo": "MAR", "Abril": "ABR",
    "Mayo": "MAY", "Junio": "JUN", "Julio": "JUL", "Agosto": "AGO",
    "Septiembre": "SEP", "Octubre": "OCT", "Noviembre": "NOV", "Diciembre": "DIC"
}


# ==============================================================================
# RENDER DE CARDS
# ==============================================================================
import unicodedata

def normalize(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.strip().upper()



import pandas as pd
def render_cards_servicio(df_mes_mo):

    df_mes_mo = pd.DataFrame(df_mes_mo)

    if "Tipo" not in df_mes_mo.columns:
        st.warning("No hay datos de Mano de Obra.")
        return

    st.markdown("#### Mano de Obra")

    tipos = list(df_mes_mo["Tipo"].dropna().unique())
    cols = st.columns(2)
    idx = 0

    for t in tipos:
        df_t = df_mes_mo[df_mes_mo["Tipo"] == t]
        if df_t.empty:
            continue

        total_t = int(df_t["Cantidad"].sum())

        df_pivot = (
            df_t
            .pivot_table(
                index=["Especialidad", "Puesto"],
                values="Cantidad",
                aggfunc="sum",
            )
            .reset_index()
        )

        with cols[idx]:
            st.markdown(f"""
            <div style="
                border: 1px solid #E3E3E3;
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 18px;
            ">
                <h5 style="margin: 0;">
                    👷 {t} — Total: {total_t}
                </h5>
            """, unsafe_allow_html=True)

            st.dataframe(
                df_pivot,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

        idx = 1 - idx





# ==============================================================================
# SPOT
# ==============================================================================
st.header("Servicios spot presupuestados")

df_spot_mo = df_mo.copy()
df_spot_mo  = df_mo[df_mo["fuente"] == "SPOT"] # Primero sacamos todos los SPOTS (En este caso ese es nuestro único filtro)

sap, cliente, gerencia, año = filtros_basicos(df_spot_mo, "spot")
df_filtrado = aplicar_filtros(df_spot_mo, sap, cliente, gerencia, año)
pivot = crear_pivot(df_filtrado, orden_meses)

df_spot_mo.rename(columns={
    "tipo": "Tipo",
    "esp": "Especialidad",
    "puesto": "Puesto",
    "cantidad": "Cantidad",
}, inplace=True)


grid = render_grid(pivot, orden_meses, abrev_meses, METSO_COLORS["G2"])

selected = grid["selected_rows"]

st.info("Selecciona una fila para ver el detalle de un servicio específico o presiona el botón de resumen global.")
ver_global = st.button("🔍 Ver detalle global")

if ver_global:
    # ==============================
    #  RESUMEN TOTAL (por botón)
    # ==============================
    st.divider()
    st.subheader("Resumen mensual global")

    for mes in orden_meses:
        df_mes_mo = df_spot_mo[df_spot_mo["mes_nombre"] == mes]

        if df_mes_mo.empty:
            continue

        st.subheader(f"📌 {mes}")
        render_cards_servicio(df_mes_mo)

elif isinstance(selected, pd.DataFrame) and not selected.empty:
    
    # ==============================
    #  SELECCIONADO → DETALLE
    # ==============================
    fila = selected.iloc[0]
    st.divider()

    st.subheader(f"DETALLE: {fila['descripcion_del_servicio']}")

    sap_sel    = fila["sap"]
    meses_act  = {m: int(fila[m]) for m in orden_meses if fila.get(m) > 0}

    if not sap_sel:
        st.info("Detalle global.")
    else:
        df_sap_mo  = df_spot_mo[df_spot_mo["sap"] == sap_sel]

        for mes in meses_act:
            st.subheader(f"📌 {mes}")
            df_mes_mo  = df_sap_mo[df_sap_mo["mes_nombre"] == mes]
            render_cards_servicio(df_mes_mo)

else:
    # ==============================
    #  SIN SELECCION NI BOTÓN
    # ==============================
    pass
