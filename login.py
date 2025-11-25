# login.py
import streamlit as st
from mod_auth import login_user, signup_user

st.set_page_config(page_title="Login", page_icon="🔐")

if "user" not in st.session_state:
    st.session_state.user = None

st.title("🔐 Iniciar Sesión")

# Si ya está logueado → redirige
if st.session_state.user is not None:
    st.switch_page("app.py")

tab1, tab2 = st.tabs(["Ingresar", "Registrar (solo admin)"])

with tab1:
    email = st.text_input("Correo")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        user = login_user(email, password)
        if user:
            st.session_state.user = user
            st.success("Sesión iniciada")
            st.switch_page("app.py")

with tab2:
    st.write("⚠️ Solo tú deberías registrar usuarios")
    new_email = st.text_input("Nuevo correo")
    new_password = st.text_input("Contraseña nueva", type="password")

    if st.button("Crear cuenta"):
        signup_user(new_email, new_password)
        st.success("Usuario creado")

