import streamlit as st
import pandas as pd
from supabase import create_client

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

class BaseRepo:

    def __init__(self, table_name, id_field=None, prefix=None):
        self.table = table_name
        self.id_field = id_field
        self.prefix = prefix

    # =======================
    # GENERAR ID
    # =======================
    def generar_id(self):
        response = (
            supabase.table(self.table)
            .select(self.id_field)
            .order(self.id_field, desc=True)
            .limit(1)
            .execute()
        )

        if response.data:
            last = response.data[0][self.id_field]
            num = int(last.split("-")[1]) + 1
        else:
            num = 1

        return f"{self.prefix}-{num:06d}"

    # =======================
    # CREATE
    # =======================
    def crear(self, data: dict):
        return (
            supabase.table(self.table)
            .insert(data)
            .execute()
        )

    # =======================
    # READ
    # =======================
    def obtener(self, id_value: str):
        response = (
            supabase.table(self.table)
            .select("*")
            .eq(self.id_field, id_value)
            .single()
            .execute()
        )

        if not response.data:
            raise ValueError(f"{self.table}: {id_value} no encontrado")

        return response.data

    def obtener_columnas(self, *cols):
        columnas = ", ".join(cols)

        resp = (
            supabase.table(self.table)
            .select(columnas)
            .execute()
        )

        # 1 sola columna → lista normal
        if len(cols) == 1:
            col = cols[0]
            return [r[col] for r in resp.data]

        # 2+ columnas → lista de tuplas
        return [
            tuple(r[col] for col in cols)
            for r in resp.data
        ]

    # Filtrar para consultas mas especializadas...

    def filtrar(self, **kwargs):
        query = supabase.table(self.table).select("*")

        for campo, valor in kwargs.items():
            query = query.eq(campo, valor)

        resp = query.execute()
        return resp.data or []

    def filtrar_df(self, **kwargs):
        data = self.filtrar(**kwargs)
        return pd.DataFrame(data)

    def buscar_por(self, columna, valor):
        return self.filtrar_df(**{columna: valor})

    

    def filtrar_columna(self, columna, **kwargs):
        query = supabase.table(self.table).select(columna)

        for campo, valor in kwargs.items():
            query = query.eq(campo, valor)

        resp = query.execute()
        return [r[columna] for r in resp.data]
    
    # Literalmente todo el dataframe... pfff....

    def obtener_todo(self):
        resp = supabase.table(self.table).select("*").execute()
        return resp.data or []
    
    def obtener_todo_df(self):
        resp = supabase.table(self.table).select("*").execute()
        return pd.DataFrame(resp.data or [])




    # =======================
    # UPDATE
    # =======================
    def update(self, id_value: str, campo: str, valor):
        return (
            supabase.table(self.table)
            .update({campo: valor})
            .eq(self.id_field, id_value)
            .execute()
        )

    # =======================
    # DELETE
    # =======================
    def delete(self, id_value):
        supabase.table(self.table) \
                .delete() \
                .eq(self.id_field, id_value) \
                .execute()

# Repos para esta app

mano_obra_repo = BaseRepo(table_name="tidy_mo")
recursos_repo = BaseRepo(table_name="tidy_rec")

