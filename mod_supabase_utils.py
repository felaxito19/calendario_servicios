# supabase_utils.py
import pandas as pd
from supabase import create_client

import streamlit as st

@st.cache_data(show_spinner="Cargando datos desde la base de datos…")
def fetch_table_cached(_supabase, table_name):
    return fetch_table(_supabase, table_name)


def init_supabase(url, key):
    return create_client(url, key)

def fetch_table(supabase, table, chunk_size=1000):
    all_data = []
    start = 0

    while True:
        end = start + chunk_size - 1
        resp = supabase.table(table).select("*").range(start, end).execute()
        rows = resp.data
        all_data.extend(rows)

        if len(rows) < chunk_size:
            break
        start += chunk_size

    return pd.DataFrame(all_data)
