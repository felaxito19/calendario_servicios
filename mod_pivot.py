# pivot.py
def crear_pivot(df, orden_meses):
    pivot = df.pivot_table(
        index=["sap","cliente", "descripcion_del_servicio"],
        columns=["mes_nombre"],
        values="cantidad",
        aggfunc="sum",
        fill_value=0
    )
    
    pivot = pivot.reindex(columns=orden_meses.keys(), fill_value=0)
    pivot = pivot.reset_index()
    
    return pivot
