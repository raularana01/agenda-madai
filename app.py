import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de página para móvil y escritorio
st.set_page_config(page_title="Agenda Madai", page_icon="📅", layout="wide")

st.title("📅 Agenda Virtual Madai")

# Cargar la URL de Google Sheets desde los secretos
GOOGLE_SHEET_URL = st.secrets.get("GOOGLE_SHEET_URL", os.environ.get("GOOGLE_SHEET_URL", ""))

@st.cache_data(ttl=30)
def cargar_datos(url):
    if not url:
        return pd.DataFrame()
    try:
        df = pd.read_csv(url, dtype=str)
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame()

if not GOOGLE_SHEET_URL:
    st.warning("⚠️ Falta configurar la variable GOOGLE_SHEET_URL en los secretos de Streamlit.")
else:
    df = cargar_datos(GOOGLE_SHEET_URL)
    
    # Vista en pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Ver Agenda", "🔍 Buscar y Filtrar", "📱 Agregar Registros"])

    # --- PESTAÑA 1: VISTA GENERAL ---
    with tab1:
        st.subheader("Lista General de Eventos")
        if not df.empty:
            col1, col2 = st.columns(2)
            col1.metric("Total de Eventos", len(df))
            
            try:
                total_adelantos = pd.to_numeric(df["Monto_Adelanto"], errors="coerce").sum()
                col2.metric("Total Recaudado (Adelantos)", f"S/ {total_adelantos:,.2f}")
            except:
                pass
                
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay eventos registrados en la base de datos.")

    # --- PESTAÑA 2: BUSCADOR Y FILTROS ---
    with tab2:
        st.subheader("Búsqueda de Eventos")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            fecha_filtro = st.date_input("Filtrar por Fecha", value=None)
        with col_f2:
            cliente_filtro = st.text_input("Buscar por Nombre, Cliente o Evento")

        df_filtrado = df.copy()

        if fecha_filtro and "Fecha" in df_filtrado.columns:
            f_str = fecha_filtro.strftime("%Y-%m-%d")
            df_filtrado = df_filtrado[df_filtrado["Fecha"] == f_str]

        if cliente_filtro and "Cliente" in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado["Cliente"].str.contains(cliente_filtro, case=False, na=False) |
                df_filtrado["Evento"].str.contains(cliente_filtro, case=False, na=False)
            ]

        st.write(f"**Resultados encontrados:** {len(df_filtrado)}")
        st.dataframe(df_filtrado, use_container_width=True)

    # --- PESTAÑA 3: CÓMO INGRESAR O EDITAR ---
    with tab3:
        st.subheader("Registro de Nuevos Eventos")
        st.info(
            "Para un guardado instantáneo y seguro sin pérdida de información, "
            "los eventos se registran directamente en tu **Google Sheets**."
        )
        sheet_edit_url = GOOGLE_SHEET_URL.split("/pub")[0] if "/pub" in GOOGLE_SHEET_URL else GOOGLE_SHEET_URL
        st.markdown(f"👉 **[Haz clic aquí para abrir Google Sheets y agregar eventos]({sheet_edit_url})**")
