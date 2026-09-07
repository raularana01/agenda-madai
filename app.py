import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Agenda Madai", page_icon="📅", layout="wide")

# Estilos CSS
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

@st.cache_data(ttl=0)
def cargar_datos(url):
    if not url:
        return pd.DataFrame()
    try:
        df = pd.read_csv(url, dtype=str)
        df = df.fillna("")
        df.columns = df.columns.str.strip()
        
        # Mapeo automático de nombres con espacios a nombres con guion bajo
        renombres = {
            "Hora Invitacion": "Hora_Invitacion",
            "Costo Total": "Costo_Total",
            "Monto Adelanto": "Monto_Adelanto",
            "Estado Pago": "Estado_Pago",
            "Desglose Costos": "Desglose_Costos",
            "Concepto Alquiler": "Concepto_Alquiler"
        }
        df = df.rename(columns=renombres)
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

if not GOOGLE_SHEET_URL:
    st.warning("⚠️ Configura GOOGLE_SHEET_URL en los secretos de Streamlit.")
else:
    df = cargar_datos(GOOGLE_SHEET_URL)

    tab_eventos, tab_filtro, tab_nuevo = st.tabs(["Eventos", "Filtro", "Nuevo"])

    # =========================================================
    # 1. PESTAÑA: EVENTOS
    # =========================================================
    with tab_eventos:
        st.subheader("📌 Eventos Registrados")

        if not df.empty and "Fecha" in df.columns:
            df_copia = df.copy()
            df_copia["Fecha_Parsed"] = pd.to_datetime(df_copia["Fecha"], errors="coerce", dayfirst=True)
            
            mask_nat = df_copia["Fecha_Parsed"].isna()
            if mask_nat.any():
                df_copia.loc[mask_nat, "Fecha_Parsed"] = pd.to_datetime(df_copia.loc[mask_nat, "Fecha"], errors="coerce")

            df_copia["Fecha_Clean"] = df_copia["Fecha_Parsed"].dt.strftime("%Y-%m-%d")

            hoy_dt = datetime.now()
            hoy_str = hoy_dt.strftime("%Y-%m-%d")

            modo_vista = st.radio(
                "Ver eventos por categoría:",
                ["Eventos del día (Hoy)", "Próximos 3 días", "Todos los eventos agendados"],
                horizontal=True
            )

            st.markdown("---")

            if modo_vista == "Eventos del día (Hoy)":
                st.markdown(f"### 🟢 Eventos para Hoy ({hoy_str})")
                df_hoy = df_copia[df_copia["Fecha_Clean"] == hoy_str]

                if not df_hoy.empty:
                    for _, row in df_hoy.iterrows():
                        st.markdown(f"""
                        <div class="card-hoy">
                            <div class="card-header">🎉 {row.get('Evento', 'Evento')} ({row.get('Tipo', '')})</div>
                            <div class="card-sub"><b>⏰ Hora Contrato:</b> {row.get('Hora', 'N/A')} | <b>Citación:</b> {row.get('Hora_Invitacion', 'N/A')}</div>
                            <div class="card-sub"><b>👤 Cliente:</b> {row.get('Cliente', 'N/A')} | <b>📱 Tel:</b> {row.get('Telefono', 'N/A')}</div>
                            <div class="card-sub"><b>📍 Lugar:</b> {row.get('Direccion', 'N/A')}</div>
                            <div class="card-sub"><b>💰 Total:</b> S/ {row.get('Costo_Total', '0')} | <b>Estado:</b> {row.get('Estado_Pago', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"No hay eventos registrados exactamente para hoy ({hoy_str}).")

            elif modo_vista == "Próximos 3 días":
                dias_proximos = [(hoy_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, 4)]
                df_3dias = df_copia[df_copia["Fecha_Clean"].isin(dias_proximos)].sort_values("Fecha_Clean")

                st.markdown("### 🔵 Eventos de los próximos 3 días")
                if not df_3dias.empty:
                    for _, row in df_3dias.iterrows():
                        st.markdown(f"""
                        <div class="card-proximo">
                            <div class="card-header">📅 {row.get('Fecha', '')} | {row.get('Evento', 'Evento')} ({row.get('Tipo', '')})</div>
                            <div class="card-sub"><b>⏰ Hora:</b> {row.get('Hora', 'N/A')} | <b>Citación:</b> {row.get('Hora_Invitacion', 'N/A')}</div>
                            <div class="card-sub"><b>👤 Cliente:</b> {row.get('Cliente', 'N/A')} | <b>📱 Tel:</b> {row.get('Telefono', 'N/A')}</div>
                            <div class="card-sub"><b>📍 Dirección:</b> {row.get('Direccion', 'N/A')}</div>
                            <div class="card-sub"><b>💰 Total:</b> S/ {row.get('Costo_Total', '0')} | <b>Estado:</b> {row.get('Estado_Pago', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No hay eventos registrados dentro de los próximos 3 días.")

            else:
                df_futuros = df_copia.sort_values("Fecha_Clean", ascending=True)

                st.markdown("### 📅 Todos los Eventos Agendados")
                if not df_futuros.empty:
                    for _, row in df_futuros.iterrows():
                        st.markdown(f"""
                        <div class="card-proximo">
                            <div class="card-header">📅 {row.get('Fecha', '')} | {row.get('Evento', 'Evento')} ({row.get('Tipo', '')})</div>
                            <div class="card-sub"><b>⏰ Hora:</b> {row.get('Hora', 'N/A')} | <b>Citación:</b> {row.get('Hora_Invitacion', 'N/A')}</div>
                            <div class="card-sub"><b>👤 Cliente:</b> {row.get('Cliente', 'N/A')} | <b>📱 Tel:</b> {row.get('Telefono', 'N/A')}</div>
                            <div class="card-sub"><b>📍 Dirección:</b> {row.get('Direccion', 'N/A')}</div>
                            <div class="card-sub"><b>💰 Total:</b> S/ {row.get('Costo_Total', '0')} | <b>Estado:</b> {row.get('Estado_Pago', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No se encontraron registros en Google Sheets.")
        else:
            st.info("No hay datos guardados aún en la base de datos.")

    # =========================================================
    # 2. PESTAÑA: FILTRO (MODIFICADA)
    # =========================================================
    with tab_filtro:
        st.subheader("🔍 Búsqueda y Filtros Especiales")
        
        df_filtrado = df.copy()
        
        # Preparar columna de fecha parseada para filtrar por rango
        if not df_filtrado.empty and "Fecha" in df_filtrado.columns:
            df_filtrado["Fecha_DT"] = pd.to_datetime(df_filtrado["Fecha"], errors="coerce", dayfirst=True)
            mask_nat = df_filtrado["Fecha_DT"].isna()
            if mask_nat.any():
                df_filtrado.loc[mask_nat, "Fecha_DT"] = pd.to_datetime(df_filtrado.loc[mask_nat, "Fecha"], errors="coerce")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_cliente = st.text_input("👤 Cliente / Nombre del Evento:", placeholder="Buscar por cliente o evento...")
        with col_f2:
            filtro_telefono = st.text_input("📱 Número de Teléfono:", placeholder="Buscar por número...")
        with col_f3:
            rango_fechas = st.date_input("📅 Rango de Fechas:", value=(), placeholder="Selecciona inicio y fin")

        col_f4, col_f5 = st.columns(2)
        with col_f4:
            opciones_estado = ["Todos"] + list(df["Estado_Pago"].unique()) if not df.empty and "Estado_Pago" in df.columns else ["Todos"]
            filtro_estado = st.selectbox("Estado de Pago:", opciones_estado)
        with col_f5:
            opciones_tipo = ["Todos"] + list(df["Tipo"].unique()) if not df.empty and "Tipo" in df.columns else ["Todos"]
            filtro_tipo = st.selectbox("Tipo de Servicio:", opciones_tipo)

        # Aplicación de Filtros
        if filtro_cliente and not df_filtrado.empty:
            mask_cliente = (
                df_filtrado["Cliente"].astype(str).str.contains(filtro_cliente, case=False, na=False) |
                df_filtrado["Evento"].astype(str).str.contains(filtro_cliente, case=False, na=False)
            )
            df_filtrado = df_filtrado[mask_cliente]

        if filtro_telefono and not df_filtrado.empty:
            df_filtrado = df_filtrado[df_filtrado["Telefono"].astype(str).str.contains(filtro_telefono, case=False, na=False)]

        if isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2 and not df_filtrado.empty:
            f_inicio, f_fin = rango_fechas
            df_filtrado = df_filtrado[
                (df_filtrado["Fecha_DT"].dt.date >= f_inicio) & 
                (df_filtrado["Fecha_DT"].dt.date <= f_fin)
            ]

        if filtro_estado != "Todos" and not df_filtrado.empty:
            df_filtrado = df_filtrado[df_filtrado["Estado_Pago"] == filtro_estado]

        if filtro_tipo != "Todos" and not df_filtrado.empty:
            df_filtrado = df_filtrado[df_filtrado["Tipo"] == filtro_tipo]

        if "Fecha_DT" in df_filtrado.columns:
            df_filtrado = df_filtrado.drop(columns=["Fecha_DT"])

        st.write(f"**Resultados encontrados:** {len(df_filtrado)}")
        st.dataframe(df_filtrado, use_container_width=True)

    # =========================================================
    # 3. PESTAÑA: NUEVO (MODIFICADA)
    # =========================================================
    with tab_nuevo:
        st.subheader("➕ Llenar Servicio")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fecha_input = st.date_input("1. Fecha del Servicio", datetime.now())
            fecha_str = fecha_input.strftime("%Y-%m-%d")
        with col_s2:
            tipo_servicio = st.selectbox("2. Tipo de Servicio", ["Show", "Decoración", "Show + Decoración", "Alquiler"])

        st.markdown("---")

        with st.form("form_servicio", clear_on_submit=True):
            nombre_evento = ""
            hora_contrato_str = ""
            hora_invitacion_str = ""
            agregar_alquiler = "No"
            concepto_alquiler = ""
            monto_alquiler = 0

            if tipo_servicio == "Alquiler":
                col1, col2 = st.columns(2)
                with col1:
                    concepto_alquiler = st.text_input("Concepto de Alquiler", placeholder="ej. Sillas, Toldo, Luces")
                    hora_entrega_input = st.time_input("Hora de Entrega", value=datetime.strptime("15:00", "%H:%M").time())
                    hora_contrato_str = hora_entrega_input.strftime("%I:%M %p")
                    direccion = st.text_input("Dirección de Entrega")

                with col2:
                    cliente = st.text_input("Nombre del Cliente")
                    telefono = st.text_input("Teléfono del Cliente")
                    nombre_evento = f"Alquiler - {concepto_alquiler}" if concepto_alquiler else "Alquiler"
                    hora_invitacion_str = hora_contrato_str

            else:
                col1, col2 = st.columns(2)
                with col1:
                    nombre_evento = st.text_input("Nombre del Evento", placeholder="ej. Cumpleaños de Gia")
                    
                    hc_input = st.time_input("Hora Contrato / Inicio Show", value=datetime.strptime("16:00", "%H:%M").time())
                    hora_contrato_str = hc_input.strftime("%I:%M %p")

                    hi_input = st.time_input("Hora Citación / Invitación", value=datetime.strptime("15:00", "%H:%M").time())
                    hora_invitacion_str = hi_input.strftime("%I:%M %p")

                    direccion = st.text_input("Dirección del Evento")

                with col2:
                    cliente = st.text_input("Nombre del Cliente")
                    telefono = st.text_input("Teléfono del Cliente")
                    agregar_alquiler = st.radio("¿Agregar Alquiler adicional?", ["No", "Sí"], horizontal=True)

                if agregar_alquiler == "Sí":
                    st.markdown("##### 📦 Detalles del Alquiler Agregado")
                    col_alq1, col_alq2 = st.columns(2)
                    with col_alq1:
                        concepto_alquiler = st.text_input("Concepto del Alquiler Agregado", placeholder="ej. Luces, Sillas")
                    with col_alq2:
                        monto_alquiler = st.number_input("Monto del Alquiler Agregado (S/)", min_value=0, step=1, value=0)

            st.markdown("---")
            st.markdown("### Información de Pago")

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
                    st.info(f"💵 **Pago Pendiente:** S/ {monto_pendiente}")
                elif estado_pago == "Pago completo":
                    monto_adelanto = int(costo_total)
                    st.success("✅ Servicio cancelado completo.")
                else:
                    monto_adelanto = 0
                    st.warning(f"⚠️ Saldo pendiente: S/ {costo_total}")

            st.markdown("---")
            descripcion = st.text_area("📝 Detalles / Observaciones Adicionales", placeholder="Escribe aquí detalles adicionales...")

            btn_guardar = st.form_submit_button("💾 Guardar Servicio", use_container_width=True)

            if btn_guardar:
                if not GOOGLE_SCRIPT_URL:
                    st.error("⚠️ Falta configurar GOOGLE_SCRIPT_URL en los secretos.")
                else:
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
                        "Hora": hora_contrato_str,
                        "Direccion": direccion,
                        "Hora_Invitacion": hora_invitacion_str,
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
                            st.success("🎉 ¡El servicio fue guardado con éxito!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Error HTTP {res.status_code} al guardar en Google Sheets.")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
