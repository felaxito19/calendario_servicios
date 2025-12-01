# app.py
import streamlit as st
from mod_supabase_utils import init_supabase, fetch_table_cached
from mod_filters import filtros_basicos, aplicar_filtros
from mod_pivot import crear_pivot
from mod_aggrid import render_grid, estilo_tabla



st.set_page_config(page_title="Calendario", layout="wide")

# Bloquea acceso si no está logueado
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("Login.py")


st.write(f"Bienvenido **{st.session_state.user.user.email}**")

st.title("Calendario de Servicios | Área de propuestas")

from repositories import mano_obra_repo, recursos_repo
df_mo = mano_obra_repo.obtener_todo_df()
df_rec = recursos_repo.obtener_todo_df()

#un pqueño parche
df_mo["esp"] = (
    df_mo["esp"]
    .fillna("")          # convierte None/NaN a string vacío
    .astype(str)         # garantiza que todo sea string
    .str.strip()         # quita espacios alrededor
    .replace("", "SIN ESPECIALIDAD")   # si queda vacío → reemplaza
)




from colors import METSO_COLORS



orden_meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

abrev_meses = {
    "Enero": "ENE",
    "Febrero": "FEB",
    "Marzo": "MAR",
    "Abril": "ABR",
    "Mayo": "MAY",
    "Junio": "JUN",
    "Julio": "JUL",
    "Agosto": "AGO",
    "Septiembre": "SEP",
    "Octubre": "OCT",
    "Noviembre": "NOV",
    "Diciembre": "DIC"
}

tab1, tab2 = st.tabs(["Contratos", "Servicios Spot"])

# ---------------------------------------------------------------------------------------------------
# FUNCIÓN PARA MI DASHBOARD
import unicodedata
import streamlit as st

def normalize(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.strip().upper()

def render_cards_servicio(df_mes_mo, df_mes_rec, estilo_tabla, pretty_mo, pretty_rec):
    col1, col2, col3 = st.columns(3)

    # =========================================================
    # COL 1 — MANO DE OBRA
    # =========================================================
    with col1:
        st.markdown("#### Mano de Obra")

        tipos = df_mes_mo["Tipo"].dropna().unique()

        for t in tipos:
            df_t = df_mes_mo[df_mes_mo["Tipo"] == t]

            if df_t.empty:
                continue

            total_t = df_t["Cantidad"].sum()

            st.markdown(f"""
            <div style="
                border: 1px solid #E3E3E3;
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 18px;
            ">
                <h5 style="margin: 0 0 8px 0;">
                    👷 {t} — Total: {total_t}
                </h5>
            """, unsafe_allow_html=True)

            


            df_pivot = (
                df_t
                .pivot_table(
                    index=["Especialidad", "Puesto"],
                    values="Cantidad",
                    aggfunc="sum"
                )
                .reset_index()
                .rename(columns=pretty_mo)
            )

            st.dataframe(estilo_tabla(df_pivot), hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================
    # COL 2 — Alojamiento & Transporte
    # =========================================================
    with col2:
        st.markdown("#### Alojamiento & Transporte")

        recursos_validos = ["ALIMENTACION", "ALOJAMIENTO", "TRANSPORTE"]

        df_f = df_mes_rec[
            df_mes_rec["Recurso"].apply(
                lambda x: any(rv in normalize(x) for rv in recursos_validos)
            )
        ]

        recursos = sorted(df_f["Recurso"].unique(), key=lambda r: normalize(r))

        emoji = {
            "ALIMENTACION": "🍽️",
            "ALOJAMIENTO": "🛏️",
            "TRANSPORTE": "🚚"
        }

        for r in recursos:
            r_norm = normalize(r)

            st.markdown(f"""
            <div style="
                border: 1px solid #E3E3E3;
                padding: 16px;
                border-radius: 12px;
                margin-bottom: 18px;">
                <h5 style="margin: 0 0 0 0;">
                    {emoji.get(r_norm, "📦")} {r}
                </h5>
            """, unsafe_allow_html=True)

            df_r = df_f[df_f["Recurso"] == r]

            df_pivot = (
                df_r
                .pivot_table(
                    index=["Descripción"],
                    values=["Cantidad", "Días"],
                    aggfunc="sum"
                )
                .reset_index()
                .rename(columns=pretty_rec)
            )

            st.dataframe(estilo_tabla(df_pivot), hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================
    # COL 3 — RECURSOS VARIOS
    # =========================================================
    with col3:
        st.markdown("#### Recursos Varios")

        recursos_validos = ["ALIMENTACION", "ALOJAMIENTO", "TRANSPORTE"]

        df_rest = df_mes_rec[
            df_mes_rec["Recurso"].apply(
                lambda x: not any(rv in normalize(x) for rv in recursos_validos)
            )
        ]

        if df_rest.empty:
            st.write("No hay recursos adicionales.")
        else:
            recursos_varios = sorted(df_rest["Recurso"].unique(), key=lambda r: normalize(r))

            for r in recursos_varios:
                st.markdown(f"""
                <div style="
                    border: 1px solid #E3E3E3;
                    padding: 16px;
                    border-radius: 12px;
                    margin-bottom: 18px;">
                    <h5 style="margin: 0 0 0 0;">
                        📦 {r}
                    </h5>
                """, unsafe_allow_html=True)

                df_r = df_rest[df_rest["Recurso"] == r]

                df_pivot = (
                    df_r
                    .pivot_table(
                        index=["Descripción"],
                        values=["Cantidad"],
                        aggfunc="sum"
                    )
                    .reset_index()
                    .rename(columns=pretty_rec)
                )

                st.dataframe(estilo_tabla(df_pivot), hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------------------------------

with tab1:

    st.header("Servicios relacionados a contratos")

    # 1) Filtrar df_mo y df_rec a solo CONTRATOS
    df_contrato_mo  = df_mo[df_mo["fuente"] == "CONTRATO"].copy()
    df_contrato_rec = df_rec[df_rec["fuente"] == "CONTRATO"].copy()

    # 2) Aplicar tus filtros (+ pivot)
    sap, cliente, gerencia, año = filtros_basicos(df_contrato_mo, "contrato")
    df_filtrado = aplicar_filtros(df_contrato_mo, sap, cliente, gerencia, año)
    pivot = crear_pivot(df_filtrado, orden_meses)

    # 3) Render de la tabla pivot

    pretty_mo = {
    "tipo": "Tipo",
    "esp": "Especialidad",
    "puesto": "Puesto",
    "cantidad": "Cantidad",
    }

    pretty_rec = {
        "tipo_recurso": "Recurso",
        "descripcion": "Descripción",
        "cantidad": "Cantidad",
        "dias": "Días"
    }
                                    
    df_contrato_mo = df_contrato_mo.rename(columns=pretty_mo)
    df_contrato_rec = df_contrato_rec.rename(columns=pretty_rec)


    grid_1 = render_grid(pivot, orden_meses, abrev_meses, METSO_COLORS["G2"])


    selected = grid_1["selected_rows"]

    st.write("Hint: selecciona una fila para ver detalles del contrato.")

    if selected is not None and len(selected) > 0:
        # Si es lista → dict
        if isinstance(selected, list):
            fila = selected[0]
        else:
            fila = selected.iloc[0]

        st.markdown("---")
        st.markdown("### Detalle del Servicio")




        sap_sel    = fila["sap"]
        meses_act  = {m: int(fila[m]) for m in orden_meses if fila.get(m) > 0}

        if sap_sel == "" or sap_sel is None:
            st.info("Detalle global.")
        else:
            # Pre-filtrar una sola vez
            df_sap_mo  = df_contrato_mo[df_contrato_mo["sap"] == sap_sel]
            df_sap_rec = df_contrato_rec[df_contrato_rec["sap"] == sap_sel]

            for mes in meses_act:
                st.subheader(f"📌 {mes}")

                df_mes_mo  = df_sap_mo[df_sap_mo["mes_nombre"] == mes]
                df_mes_rec = df_sap_rec[df_sap_rec["mes_nombre"] == mes]

                # ⚡️ Aquí llamas a la función que arma TODAS las cards
                render_cards_servicio(
                    df_mes_mo,
                    df_mes_rec,
                    estilo_tabla,
                    pretty_mo,
                    pretty_rec
                )

                    


with tab2:

    st.header("Servicios spot adjudicados")

    # 1) Filtrar df_mo y df_rec a solo CONTRATOS
    df_spot_mo  = df_mo[df_mo["fuente"] == "SPOT"].copy()
    df_spot_rec = df_rec[df_rec["fuente"] == "SPOT"].copy()

    # Y en este caso particular solo a adj

    df_spot_mo = df_spot_mo[df_spot_mo["estatus"] == "Adjudicado"]
    df_spot_rec = df_spot_rec[df_spot_rec["estatus"] == "Adjudicado"]

    # 2) Aplicar tus filtros (+ pivot)
    sap, cliente, gerencia, año = filtros_basicos(df_spot_mo, "spot")
    df_filtrado = aplicar_filtros(df_spot_mo, sap, cliente, gerencia, año)
    pivot = crear_pivot(df_filtrado, orden_meses)

    # 3) Render de la tabla pivot

    pretty_mo = {
    "tipo": "Tipo",
    "esp": "Especialidad",
    "puesto": "Puesto",
    "cantidad": "Cantidad",
    }

    pretty_rec = {
        "tipo_recurso": "Recurso",
        "descripcion": "Descripción",
        "cantidad": "Cantidad",
        "dias": "Días"
    }
                                    
    df_spot_mo = df_spot_mo.rename(columns=pretty_mo)
    df_spot_rec = df_spot_rec.rename(columns=pretty_rec)


    grid_1 = render_grid(pivot, orden_meses, abrev_meses, METSO_COLORS["G2"])

    selected = grid_1["selected_rows"]

    st.write("Hint: selecciona una fila para ver detalles del contrato.")

    if selected is not None and len(selected) > 0:
        # Si es lista → dict
        if isinstance(selected, list):
            fila = selected[0]
        else:
            fila = selected.iloc[0]

        st.markdown("---")
        st.markdown("### Detalle del Servicio")


        sap_sel    = fila["sap"]
        meses_act  = {m: int(fila[m]) for m in orden_meses if fila.get(m) > 0}

        if sap_sel == "" or sap_sel is None:
            st.info("Detalle global.")
        else:
            # Pre-filtrar una sola vez
            df_sap_mo  = df_spot_mo[df_spot_mo["sap"] == sap_sel]
            df_sap_rec = df_spot_rec[df_spot_rec["sap"] == sap_sel]

            for mes in meses_act:
                st.subheader(f"📌 {mes}")

                df_mes_mo  = df_sap_mo[df_sap_mo["mes_nombre"] == mes]
                df_mes_rec = df_sap_rec[df_sap_rec["mes_nombre"] == mes]

                # ⚡️ Aquí llamas a la función que arma TODAS las cards
                render_cards_servicio(
                    df_mes_mo,
                    df_mes_rec,
                    estilo_tabla,
                    pretty_mo,
                    pretty_rec

                )




