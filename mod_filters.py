# filters.py
import streamlit as st

def filtros_basicos(df, prefix):
    col1, col2 = st.columns(2)

    with col1:
        sap = st.selectbox("🔧 SAP", ["Todos"] + sorted(df["SAP"].unique()), key=f"sap_{prefix}")

    col3, col4, col5 = st.columns(3)

    with col3:
        cliente = st.selectbox("🔽 Cliente", ["Todos"] + sorted(df["CLIENTE"].unique()), key=f"cliente_{prefix}")
    with col4:
        gerencia = st.selectbox("🏢 Gerencia", ["Todas"] + sorted(df["GERENCIA"].dropna().unique()), key=f"gerencia_{prefix}")
    with col5:
        año = st.selectbox("📅 Año", sorted(df["AÑO"].unique()), key=f"año_{prefix}")

    return sap, cliente, gerencia, año


def aplicar_filtros(df, sap, cliente, gerencia, año):
    if sap != "Todos":
        df = df[df["SAP"] == sap]
    if cliente != "Todos":
        df = df[df["CLIENTE"] == cliente]
    if gerencia != "Todas":
        df = df[df["GERENCIA"] == gerencia]
    return df[df["AÑO"] == año]
