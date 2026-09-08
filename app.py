import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Agenda Madai", page_icon="📅", layout="wide")

# Estilos CSS y forzado de diseño en filas
st.markdown("""
<style>
    /* Forzar diseño horizontal en columnas de formulario */
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 1rem !important;
    }
    
    [data-testid="stForm"] [data-testid="stHorizontalBlock"] > div {
        flex: 1 1 0px !important;
        min-width: 0 !important;
    }

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

# Función para construir selector de hora dinámico AM/PM
def selector_hora_ampm(label, key_prefix, default_hora=4, default_min=0, default_ampm="PM"):
    st.markdown(f"**{label}**")
    col_h, col_m, col_p = st.columns([2, 2, 2])
    with col_h:
        hora = st.number_input("Hora", min_value=1, max_value=12, value=default_hora, key=f"{key_prefix}_h")
    with col_m:
        minuto = st.number_input("Min", min_value=0, max_value=59, value=default_min, step=5, key=f"{key_prefix}_m")
    with col_p:
        ampm = st.selectbox("AM/PM", ["AM", "PM"], index=1 if default_ampm == "PM" else 0, key=f"{key_prefix}_p")
    return f"{hora:02d}:{minuto:02d} {ampm}"

if not GOOGLE_SHEET_URL:
    st.warning("⚠️ Configura GOOGLE_SHEET_URL en los secretos de Streamlit.")
else:
    df = cargar_datos(GOOGLE_SHEET_URL)

    tab_eventos, tab_filtro, tab_nuevo = st.tabs(["Eventos", "Filtro", "Nuevo"])

    # =========================================================
    # 1. PESTAÑA: EVENTOS
    # =========================================================
    with tab_eventos:
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
                    st.info(f"No hay eventos registrados para hoy ({hoy_str}).")

            elif modo_vista == "Próximos 3 días":
                dias_proximos = [(hoy_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(0, 4)]
                df_3dias = df_copia[df_copia["Fecha_Clean"].isin(dias_proximos)].sort_values("Fecha_Clean")

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
    # 2. PESTAÑA: FILTRO
    # =========================================================
    with tab_filtro:
        st.subheader("🔍 Búsqueda y Filtros")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_cliente = st.text_input("👤 Cliente / Nombre del Evento:", placeholder="Buscar por cliente o evento...")
        with col_f2:
            filtro_telefono = st.text_input("📱 Número de Teléfono:", placeholder="Buscar por número...")
        with col_f3:
            rango_fechas = st.date_input("📅 Rango de Fechas:", value=())

        tiene_filtro_fechas = isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2
        filtro_activo = bool(filtro_cliente.strip() or filtro_telefono.strip() or tiene_filtro_fechas)

        if not filtro_activo:
            st.info("👉 Ingresa un nombre, número de teléfono o selecciona un rango de fechas para ver los resultados.")
        else:
            df_filtrado = df.copy()

            if not df_filtrado.empty and "Fecha" in df_filtrado.columns:
                df_filtrado["Fecha_DT"] = pd.to_datetime(df_filtrado["Fecha"], errors="coerce", dayfirst=True)
                mask_nat = df_filtrado["Fecha_DT"].isna()
                if mask_nat.any():
                    df_filtrado.loc[mask_nat, "Fecha_DT"] = pd.to_datetime(df_filtrado.loc[mask_nat, "Fecha"], errors="coerce")

            if filtro_cliente.strip() and not df_filtrado.empty:
                mask_cliente = (
                    df_filtrado["Cliente"].astype(str).str.contains(filtro_cliente, case=False, na=False) |
                    df_filtrado["Evento"].astype(str).str.contains(filtro_cliente, case=False, na=False)
                )
                df_filtrado = df_filtrado[mask_cliente]

            if filtro_telefono.strip() and not df_filtrado.empty:
                df_filtrado = df_filtrado[df_filtrado["Telefono"].astype(str).str.contains(filtro_telefono, case=False, na=False)]

            if tiene_filtro_fechas and not df_filtrado.empty:
                f_inicio, f_fin = rango_fechas
                df_filtrado = df_filtrado[
                    (df_filtrado["Fecha_DT"].dt.date >= f_inicio) & 
                    (df_filtrado["Fecha_DT"].dt.date <= f_fin)
                ]

            if "Fecha_DT" in df_filtrado.columns:
                df_filtrado = df_filtrado.drop(columns=["Fecha_DT"])

            st.write(f"**Resultados encontrados:** {len(df_filtrado)}")
            st.dataframe(df_filtrado, use_container_width=True)

    # =========================================================
    # 3. PESTAÑA: NUEVO
    # =========================================================
    with tab_nuevo:
        with st.form("form_servicio", clear_on_submit=True):
            # 1. Fecha y Tipo de Servicio JUNTOS
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                fecha_input = st.date_input("📅 Fecha del Servicio", datetime.now())
                fecha_str = fecha_input.strftime("%Y-%m-%d")
            with col_f2:
                tipo_servicio = st.selectbox("🎭 Tipo de Servicio", ["Show", "Decoración", "Show + Decoración", "Alquiler"])

            st.markdown("---")

            # 2. Nombre del Evento y Cliente UNO ABAJO DEL OTRO
            nombre_evento = st.text_input("🎉 Nombre del Evento", placeholder="ej. Cumpleaños de Gia")
            cliente = st.text_input("👤 Nombre del Cliente", placeholder="ej. María López")

            st.markdown("---")

            # 3. Horas con selector dinámico AM / PM
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                hora_contrato_str = selector_hora_ampm("⏰ Hora Contrato / Inicio", "hc", default_hora=4, default_ampm="PM")
            with col_h2:
                hora_invitacion_str = selector_hora_ampm("📩 Hora Citación / Invitación", "hi", default_hora=3, default_ampm="PM")

            st.markdown("---")

            # 4. Dirección en UNA SOLA LÍNEA
            direccion = st.text_input("📍 Dirección del Evento", placeholder="ej. Av. Las Flores 123, San Isidro")

            st.markdown("---")

            # 5. Teléfono y ¿Agregar Alquiler? JUNTOS
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                telefono = st.text_input("📱 Teléfono del Cliente", placeholder="ej. 987654321")
            with col_t2:
                agregar_alquiler = st.radio("📦 ¿Agregar Alquiler?", ["No", "Sí"], horizontal=True)

            concepto_alquiler = ""
            monto_alquiler = 0
            if agregar_alquiler == "Sí" or tipo_servicio == "Alquiler":
                st.markdown("##### 📦 Detalles del Alquiler")
                col_alq1, col_alq2 = st.columns(2)
                with col_alq1:
                    concepto_alquiler = st.text_input("Concepto del Alquiler", placeholder="ej. Luces, Sillas, Toldo")
                with col_alq2:
                    monto_alquiler = st.number_input("Monto del Alquiler (S/)", min_value=0, step=1, value=0)

            st.markdown("---")
            st.markdown("### 💰 Montos y Pagos")

            costo_total = 0
            costo_show = 0
            costo_deco = 0

            # 6. Lógica de Precios según Tipo de Servicio
            if tipo_servicio == "Show + Decoración":
                st.info("💡 **Show + Decoración:** Ingresa los precios independientes para cada servicio:")
                col_sd1, col_sd2 = st.columns(2)
                with col_sd1:
                    costo_show = st.number_input("Costo del Show (S/)", min_value=0, step=1, value=0)
                with col_sd2:
                    costo_deco = st.number_input("Costo de la Decoración (S/)", min_value=0, step=1, value=0)

                costo_total = costo_show + costo_deco + monto_alquiler
                st.markdown(f"**Desglose:** Show (S/ {costo_show}) + Decoración (S/ {costo_deco})" + (f" + Alquiler (S/ {monto_alquiler})" if monto_alquiler > 0 else ""))
                st.subheader(f"Costo Total Calculado: S/ {costo_total}")

            elif tipo_servicio in ["Show", "Decoración"]:
                costo_base = st.number_input(f"Costo Total del Servicio ({tipo_servicio}) (S/)", min_value=0, step=1, value=0)
                costo_total = costo_base + monto_alquiler
            else:  # Alquiler solo
                costo_total = monto_alquiler

            # 7. Adelanto y Cálculo de Pendiente (Sin radio de estado)
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                monto_adelanto = st.number_input("Monto de Adelanto (S/)", min_value=0, max_value=int(costo_total) if costo_total > 0 else 99999, step=1, value=0)
            
            monto_pendiente = max(0, int(costo_total) - int(monto_adelanto))

            with col_p2:
                if monto_pendiente == 0 and costo_total > 0:
                    st.success("### ✅ CANCELADO")
                    estado_pago = "Pago completo"
                else:
                    st.warning(f"💵 **MONTO PENDIENTE:** S/ {monto_pendiente}")
                    estado_pago = "Pago parcial"

            st.markdown("---")
            descripcion = st.text_area("📝 Detalles / Observaciones Adicionales", placeholder="Escribe aquí detalles adicionales...")

            btn_guardar = st.form_submit_button("💾 Guardar Servicio", use_container_width=True)

            if btn_guardar:
                if not GOOGLE_SCRIPT_URL:
                    st.error("⚠️ Falta configurar GOOGLE_SCRIPT_URL en los secretos.")
                else:
                    # Desglose personalizado
                    desglose_partes = []
                    if tipo_servicio == "Show + Decoración":
                        desglose_partes.append(f"Show: S/ {costo_show}")
                        desglose_partes.append(f"Decoración: S/ {costo_deco}")
                    elif tipo_servicio != "Alquiler":
                        desglose_partes.append(f"{tipo_servicio}: S/ {costo_total - monto_alquiler}")
                    
                    if concepto_alquiler:
                        desglose_partes.append(f"Alquiler ({concepto_alquiler}): S/ {monto_alquiler}")
                    
                    if monto_pendiente > 0:
                        desglose_partes.append(f"Pendiente: S/ {monto_pendiente}")

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
