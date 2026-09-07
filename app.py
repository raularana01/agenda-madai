import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta

# Configuración de página
st.set_page_config(page_title="Agenda Madai", page_icon="📅", layout="wide")

# Estilos CSS para tarjetas llamativas de eventos
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
        color: #333333;
        margin-bottom: 3px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 Agenda Virtual Madai")

# Cargar variables de secretos
GOOGLE_SHEET_URL = st.secrets.get("GOOGLE_SHEET_URL", os.environ.get("GOOGLE_SHEET_URL", ""))
GOOGLE_SCRIPT_URL = st.secrets.get("GOOGLE_SCRIPT_URL", os.environ.get("GOOGLE_SCRIPT_URL", ""))

@st.cache_data(ttl=15)
def cargar_datos(url):
    if not url:
        return pd.DataFrame()
    try:
        df = pd.read_csv(url, dtype=str)
        df = df.fillna("")
        # Limpieza básica de espacios en columnas
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame()

if not GOOGLE_SHEET_URL:
    st.warning("⚠️ Configura GOOGLE_SHEET_URL en los secretos de Streamlit.")
else:
    df = cargar_datos(GOOGLE_SHEET_URL)

    # Navegación reducida a 3 pestañas
    tab_inicio, tab_filtros, tab_agregar = st.tabs([
        "🏠 Inicio (Eventos)", 
        "🔍 Filtros Personalizados", 
        "➕ Llenar Servicio"
    ])

    # =========================================================
    # 1. PESTAÑA INICIO: TARJETAS DE HOY Y PRÓXIMOS 3 DÍAS
    # =========================================================
    with tab_inicio:
        st.subheader("📌 Resumen de Eventos")
        
        hoy_dt = datetime.now()
        hoy_str = hoy_dt.strftime("%Y-%m-%d")
        proximos_3_dias = [(hoy_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 4)]

        if not df.empty and "Fecha" in df.columns:
            # Normalizar fechas para comparación uniforme YYYY-MM-DD
            df_copia = df.copy()
            df_copia["Fecha_Clean"] = pd.to_datetime(df_copia["Fecha"], errors="coerce").dt.strftime("%Y-%m-%d")

            df_hoy = df_copia[df_copia["Fecha_Clean"] == hoy_str]
            df_proximos = df_copia[df_copia["Fecha_Clean"].isin(proximos_3_dias)]

            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown(f"### 🟢 Eventos de Hoy ({hoy_str})")
                if not df_hoy.empty:
                    for _, row in df_hoy.iterrows():
                        st.markdown(f"""
                        <div class="card-hoy">
                            <div class="card-header">🎉 {row.get('Evento', 'Evento')} ({row.get('Tipo', '')})</div>
                            <div class="card-sub"><b>⏰ Hora Contrato:</b> {row.get('Hora', 'N/A')} | <b> Citación:</b> {row.get('Hora_Invitacion', 'N/A')}</div>
                            <div class="card-sub"><b>👤 Cliente:</b> {row.get('Cliente', 'N/A')} | <b>📱 Tel:</b> {row.get('Telefono', 'N/A')}</div>
                            <div class="card-sub"><b>📍 Lugar:</b> {row.get('Direccion', 'N/A')}</div>
                            <div class="card-sub"><b>💰 Total:</b> S/ {row.get('Costo_Total', '0')} | <b>Estado:</b> {row.get('Estado_Pago', 'N/A')}</div>
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
                            <div class="card-header">📅 {row.get('Fecha', '')} | {row.get('Evento', 'Evento')}</div>
                            <div class="card-sub"><b>Tipo:</b> {row.get('Tipo', '')} | <b>Hora:</b> {row.get('Hora', '')}</div>
                            <div class="card-sub"><b>Cliente:</b> {row.get('Cliente', 'N/A')} | <b>Tel:</b> {row.get('Telefono', 'N/A')}</div>
                            <div class="card-sub"><b>Dirección:</b> {row.get('Direccion', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No hay eventos programados para los próximos 3 días.")
        else:
            st.info("No hay registros en la base de datos.")

    # =========================================================
    # 2. PESTAÑA FILTROS PERSONALIZADOS
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
    # 3. PESTAÑA LLENAR SERVICIO (FORMULARIO DINÁMICO)
    # =========================================================
    with tab_agregar:
        st.subheader("➕ Llenar Servicio")
        
        # 1. Fecha primero
        fecha_input = st.date_input("1. Fecha del Servicio", datetime.now())
        fecha_str = fecha_input.strftime("%Y-%m-%d")

        # 2. Tipo de Servicio
        tipo_servicio = st.selectbox("2. Tipo de Servicio", ["Show", "Decoración", "Show + Decoración", "Alquiler"])

        st.markdown("---")

        with st.form("form_servicio", clear_on_submit=True):
            
            nombre_evento = ""
            hora_contrato = ""
            hora_invitacion = ""
            agregar_alquiler = "No"
            concepto_alquiler = ""
            monto_alquiler = 0

            # SI ES ALQUILER ÚNICAMENTE
            if tipo_servicio == "Alquiler":
                col1, col2 = st.columns(2)
                with col1:
                    concepto_alquiler = st.text_input("Concepto de Alquiler (¿Qué se alquila?)", placeholder="ej. Sillas, Luces, Toldo")
                    hora_contrato = st.text_input("Hora a Llevar / Entrega", placeholder="ej. 10:00 AM")
                    direccion = st.text_input("Dirección de Entrega")
                with col2:
                    cliente = st.text_input("Nombre del Cliente")
                    telefono = st.text_input("Teléfono del Cliente")
                    nombre_evento = f"Alquiler - {concepto_alquiler}" if concepto_alquiler else "Alquiler"
                    hora_invitacion = hora_contrato

            # SI ES SHOW, DECORACIÓN O SHOW + DECORACIÓN
            else:
                col1, col2 = st.columns(2)
                with col1:
                    nombre_evento = st.text_input("Nombre del Evento", placeholder="ej. Cumpleaños de Gia")
                    hora_contrato = st.text_input("Hora del Contrato / Inicio Show", placeholder="ej. 04:00 PM")
                    hora_invitacion = st.text_input("Hora de Invitación / Citación", placeholder="ej. 03:30 PM")
                    direccion = st.text_input("Dirección del Evento")

                with col2:
                    cliente = st.text_input("Nombre del Cliente")
                    telefono = st.text_input("Teléfono del Cliente")
                    agregar_alquiler = st.radio("¿Agregar Alquiler adicional?", ["No", "Sí"], horizontal=True)

                if agregar_alquiler == "Sí":
                    st.markdown("##### 📦 Detalles del Alquiler Adicional")
                    col_alq1, col_alq2 = st.columns(2)
                    with col_alq1:
                        concepto_alquiler = st.text_input("Concepto del Alquiler Agregado", placeholder="ej. Luces, Sillas, Accesorios")
                    with col_alq2:
                        monto_alquiler = st.number_input("Monto del Alquiler Agregado (S/)", min_value=0, step=1, value=0)

            st.markdown("---")
            st.markdown("### 💰 Información de Pago (en Soles S/)")

            col_p1, col_p2, col_p3 = st.columns(3)
            
            with col_p1:
                costo_total = st.number_input("Costo Total del Servicio (S/)", min_value=0, step=1, value=0)

            with col_p2:
                estado_pago = st.selectbox("Estado de Pago", ["Adelanto parcial", "Pago completo", "Pendiente"])

            monto_adelanto = 0
            monto_pendiente = 0

            with col_p3:
                if estado_pago == "Adelanto parcial":
                    monto_adelanto = st.number_input("Monto de Adelanto (S/)", min_value=0, max_value=int(costo_total) if costo_total > 0 else 99999, step=1, value=0)
                    monto_pendiente = max(0, int(costo_total) - int(monto_adelanto))
                    st.info(f"💵 **Pago Pendiente por cobrar:** S/ {monto_pendiente}")
                elif estado_pago == "Pago completo":
                    monto_adelanto = int(costo_total)
                    st.success("✅ Servicio cancelado en su totalidad.")
                else: # Pendiente
                    monto_adelanto = 0
                    st.warning(f"⚠️ Saldo pendiente total: S/ {costo_total}")

            st.markdown("---")
            descripcion = st.text_area("📝 Detalles / Observaciones Adicionales", placeholder="Escribe aquí notas adicionales del contrato...")

            btn_guardar = st.form_submit_button("💾 Guardar Servicio", use_container_width=True)

            if btn_guardar:
                if not GOOGLE_SCRIPT_URL:
                    st.error("⚠️ Falta configurar GOOGLE_SCRIPT_URL en los secretos de Streamlit.")
                else:
                    # Construcción de desglose
                    desglose_partes = []
                    if tipo_servicio != "Alquiler":
                        desglose_partes.append(f"{tipo_servicio}: S/ {costo_total - monto_alquiler}")
                    if concepto_alquiler:
                        desglose_partes.append(f"Alquiler: S/ {monto_alquiler} ({concepto_alquiler})")
                    
                    desglose_str = " | ".join(desglose_partes) if desglose_partes else f"S/ {costo_total}"

                    payload = {
                        "Fecha": fecha_str,
                        "Tipo": tipo_servicio if agregar_alquiler == "No" or tipo_servicio == "Alquiler" else f"{tipo_servicio} + Alquiler",
                        "Evento": nombre_evento if nombre_evento else "Evento",
                        "Hora": hora_contrato,
                        "Direccion": direccion,
                        "Hora_Invitacion": hora_invitacion,
                        "Cliente": cliente,
                        "Telefono": telefono,
                        "Costo_Total": str(int(costo_total)),
                        "Monto_Adelanto": str(int(monto_adelanto)),
                        "Estado_Pago": estado_pago,
                        "Descripcion": descripcion if descripcion else "Sin descripción",
                        "Desglose_Costos": desglose_str,
                        "Concepto_Alquiler": concepto_alquiler if concepto_alquiler else "N/A"
                    }

                    try:
                        res = requests.post(GOOGLE_SCRIPT_URL, data=json.dumps(payload))
                        if res.status_code == 200:
                            st.success(f"🎉 ¡El servicio de {tipo_servicio} fue guardado con éxito!")
                            st.cache_data.clear()
                        else:
                            st.error(f"Error al enviar datos a Google Sheets. Código HTTP: {res.status_code}")
                    except Exception as e:
                        st.error(f"Ocurrió un error en la conexión: {e}")
