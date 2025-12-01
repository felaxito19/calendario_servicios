# grid.py

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

def render_grid(df, orden_meses, abrev_meses, bg_color):
    gb = GridOptionsBuilder.from_dataframe(df)


    gb.configure_column("sap",width=1,hide=True, suppressColumnsToolPanel=True )

    gb.configure_column("cliente", pinned="left", width=180, filter=True)

    gb.configure_column(
        "descripcion_del_servicio",
        header_name="actividad",
        pinned="left",
        width=450
    )

    cell_style_js = JsCode(f"""
        function(params) {{
            if (params.value > 0) {{
                return {{
                    color: 'white',
                    backgroundColor: '{bg_color}',
                    fontWeight: '600',
                    textAlign: 'center'
                }}
            }}
            return {{
                textAlign: 'center',
                color: 'transparent'
            }}
        }}
    """)


    for mes in orden_meses.keys():
        if mes in df.columns:
            gb.configure_column(
                mes,
                header_name=abrev_meses[mes],
                width=70,
                filter=False,
                cellStyle=cell_style_js
            )

    gb.configure_selection(
        selection_mode="single",   # ✅ una fila
        use_checkbox=False         # ✅ clic directo sin checkbox
    )

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        theme="alpine",
        height=550,
        
    )

    return grid

def estilo_tabla(df):
    return (
        df.style
        .set_properties(**{
            "text-align": "left",
            "padding": "6px 10px",
            "font-size": "14px"
        })
        .hide(axis="index")
        .set_table_styles([
            {"selector": "th", "props": [
                ("background-color", "#f6f6f6"),
                ("font-weight", "600"),
                ("padding", "8px 10px"),
                ("border-bottom", "1px solid #ddd")
            ]},
            {"selector": "td", "props": [
                ("border-bottom", "1px solid #eee")
            ]},
        ])
    )

# grid.py   - v2

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode

def render_grid(df, orden_meses, abrev_meses, bg_color):

    gb = GridOptionsBuilder.from_dataframe(df)

    # Ocultar columnas internas
    gb.configure_column("sap", width=1, hide=True)
    gb.configure_column("estatus", width=1, hide=True)

    # Left pinned
    gb.configure_column("cliente", pinned="left", width=180)
    gb.configure_column(
        "descripcion_del_servicio",
        header_name="actividad",
        pinned="left",
        width=450
    )

    # 🎨 color dinámico por estatus
    color_js = JsCode("""
        function(params) {
            let e = params.data.estatus;
            if (!e) return {};

            let colors = {
                "Enviado": "#00AEEF",
                "Cancelado": "#FF5555",
                "Esperando Cliente": "#F39C12",
                "Adjudicado": "#27AE60",
                "Programado": "#8E44AD"
            };

            return {
                backgroundColor: colors[e] || "transparent",
                color: colors[e] ? "white" : "black",
                fontWeight: "600",
                textAlign: "center"
            }
        }
    """)

    # Color para los meses
    cell_style_meses = JsCode(f"""
        function(params) {{
            if (params.value > 0) {{
                return {{
                    color: 'white',
                    backgroundColor: '{bg_color}',
                    fontWeight: '600',
                    textAlign: 'center'
                }}
            }}
            return {{
                textAlign: 'center',
                color: 'transparent'
            }}
        }}
    """)

    # === Columnas ===
    for mes in orden_meses.keys():
        if mes in df.columns:
            gb.configure_column(
                mes,
                header_name=abrev_meses[mes],
                width=70,
                filter=False,
                cellStyle=cell_style_meses
            )

    # === Estilo basado en ESTATUS (fila completa) ===
    gb.configure_grid_options(
        getRowStyle=color_js
    )

    # Selección
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=False
    )

    grid = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        theme="alpine",
        height=550,
    )

    return grid
