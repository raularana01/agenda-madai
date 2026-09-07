import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta

# Configuración de página
st.set_page_config(page_title="Agenda Madai", page_icon="📅", layout="wide")

# Estilos CSS para tarjetas
st.markdown("""
<style>
    .card-hoy {
        background-color: #E8F5E9;
        border-left: 6px solid #2E7D32;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        color: #1B5E20;
    }
    .card-proximo {
        background-color: #E3F2FD;
        border-left: 6px solid #1565C0;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        color: #0D47A1;
    }
    .card-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .card-sub {
        font-size: 14px;
        color: #424242;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 Agenda Virtual Madai")

# Cargar variables secretas
GOOGLE_SHEET_URL = st.secrets.get("GOOGLE_SHEET_URL", os.environ.get("GOOGLE_SHEET_URL", ""))
GOOGLE_SCRIPT_URL = st.secrets.get("GOOGLE_SCRIPT_URL", os.environ.get("GOOGLE_SCRIPT_URL", ""))

@st.cache_data(ttl=15)
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
    st.warning("⚠️ Configura GOOGLE_SHEET_URL en los secretos de Streamlit.")
else:
    df = cargar_datos(GOOGLE_SHEET_URL)

    # Menú principal
    tab_inicio, tab_agenda, tab_filtros, tab_agregar = st.tabs([
        "🏠 Inicio (Eventos)", 
        "📋 Todos los Eventos", 
        "🔍 Filtros Avanzados", 
        "➕ Agregar Servicio"
    ])

    # =========================================================
    # 1. PESTAÑA INICIO: TARJETAS LLAMATIVAS
    # =========================================================
    with tab_inicio:
        st.subheader("📌 Resumen de Eventos")
        
        hoy_dt = datetime.now()
        hoy_str = hoy_dt.strftime("%Y-%m-%d")
        proximos_3_dias = [(hoy_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 4)]

        if not df.empty and "Fecha" in df.columns:
            df_hoy = df[df["Fecha"] == hoy_str]
            df_proximos = df[df["Fecha"].isin(proximos_3_dias)]

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown(f"### 🟢 Eventos de Hoy ({hoy_str})")
                if not df_hoy.empty:
                    for _, row in df_hoy.iterrows():
                        st.markdown(f"""
                        <div class="card-hoy">
                            <div class="card-header">🎉 {row.get('Evento', '')} - {row.get('Hora', '')}</div>
                            <div class="card-sub"><b>Cliente:</b> {row.get('Cliente', '')} | <b>Teléfono:</b> {row.get('Telefono', '')}</div>
                            <div class="card-sub"><b>Tipo:</b> {row.get('Tipo', '')} | <b>Lugar:</b> {row.get('Direccion', '')}</div>
                            <div class="card-sub"><b>Estado Pago:</b> {row.get('Estado_Pago', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No hay eventos programados para el día de hoy.")

            with col_b:
                st.markdown("### 🔵 Próximos 3 Días")
                if not df_proximos.empty:
                    for _, row in df_proximos.iterrows():
                        st.markdown(f"""
                        <div class="card-proximo">
                            <div class="card-header">📅 {row.get('Fecha', '')} | {row.get('Evento', '')} ({row.get('Hora', '')})</div>
                            <div class="card-sub"><b>Cliente:</b> {row.get('Cliente', '')} | <b>Tipo:</b> {row.get('Tipo', '')}</div>
                            <div class="card-sub"><b>Dirección:</b> {row.get('Direccion', '')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No hay eventos programados para los próximos 3 días.")
        else:
            st.info("No hay datos disponibles en la agenda.")

    # =========================================================
    # 2. PESTAÑA AGENDA GENERAL
    # =========================================================
    with tab_agenda:
        st.subheader("📋 Lista Completa de Registros")
        if not df.empty:
            st.dataframe(df, use_container_width=True)

    # =========================================================
    # 3. PESTAÑA FILTROS PERSONALIZADOS
    # =========================================================
    with tab_filtros:
        st.subheader("🔍 Filtros Personalizados")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            filtro_texto = st.text_input("Buscar texto libre (Cliente, Evento, Dirección, etc.):")
        with c2:
            opciones_estado = ["Todos"] + list(df["Estado_Pago"].unique()) if not df.empty and "Estado_Pago" in df.columns else ["Todos"]
            filtro_estado = st.selectbox("Estado de Pago:", opciones_estado)
        with c3:
            opciones_tipo = ["Todos"] + list(df["Tipo"].unique()) if not df.empty and "Tipo" in df.columns else ["Todos"]
            filtro_tipo = st.selectbox("Tipo de Servicio:", opciones_tipo)

        df_filtrado = df.copy()

        if filtro_texto and not df_filtrado.empty:
            mask = df_filtrado.apply(lambda row: row.astype(str).str.contains(filtro_texto, case=False).any(), axis=1)
            df_filtrado = df_filtrado[mask]

        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Estado_Pago"] == filtro_estado]

        if filtro_tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Tipo"] == filtro_tipo]

        st.write(f"**Coincidencias encontradas:** {len(df_filtrado)}")
        st.dataframe(df_filtrado, use_container_width=True)

    # =========================================================
    # 4. FORMULARIO NATIVO DE REGISTRO DIRECTO A BASE DE DATOS
    # =========================================================
    with tab_agregar:
        st.subheader("➕ Registrar Nuevo Evento")
        
        with st.form("form_nuevo_evento", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fecha = st.date_input("Fecha del Evento")
                tipo = st.selectbox("Tipo de Servicio", ["Show + Decoración", "Show", "Decoración + Alquiler", "Alquiler", "Otro"])
                evento = st.text_input("Nombre del Evento (ej. Cumpleaños Gia)")
                hora = st.text_input("Hora del Evento (ej. 04:00 PM)")
                direccion = st.text_input("Dirección")

            with col2:
                hora_invitacion = st.text_input("Hora Citación / Montaje")
                cliente = st.text_input("Nombre del Cliente")
                telefono = st.text_input("Teléfono de Contacto")
                costo_total = st.number_input("Costo Total (S/)", min_value=0.0, step=10.0)
                monto_adelanto = st.number_input("Monto Adelanto (S/)", min_value=0.0, step=10.0)

            with col3:
                estado_pago = st.selectbox("Estado de Pago", ["Adelanto parcial", "Pago completo", "Pendiente"])
                descripcion = st.text_area("Descripción / Notas")
                desglose = st.text_input("Desglose de Costos")
                concepto_alquiler = st.text_input("Concepto de Alquiler")

            btn_guardar = st.form_submit_button("💾 Guardar en la Base de Datos", use_container_width=True)

            if btn_guardar:
                if not GOOGLE_SCRIPT_URL:
                    st.error("⚠️ No has configurado GOOGLE_SCRIPT_URL en los secretos de Streamlit.")
                else:
                    payload = {
                        "Fecha": fecha.strftime("%Y-%m-%d"),
                        "Tipo": tipo,
                        "Evento": evento,
                        "Hora": hora,
                        "Direccion": direccion,
                        "Hora_Invitacion": hora_invitacion,
                        "Cliente": cliente,
                        "Telefono": telefono,
                        "Costo_Total": str(costo_total),
                        "Monto_Adelanto": str(monto_adelanto),
                        "Estado_Pago": estado_pago,
                        "Descripcion": descripcion,
                        "Desglose_Costos": desglose,
                        "Concepto_Alquiler": concepto_alquiler
                    }
                    
                    try:
                        res = requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload))
                        if res.status_code == 200:
                            st.success(f"🎉 ¡El evento '{evento}' se guardó directamente en la base de datos!")
                            st.cache_data.clear()
                        else:
                            st.error(f"Error al guardar los datos (Código: {res.status_code})")
                    except Exception as e:
                        st.error(f"Error en la conexión con la base de datos: {e}")
