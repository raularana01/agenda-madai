import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Agenda Madai", page_icon="📅", layout="centered")

# Estilos CSS optimizados para móviles sin scroll lateral
st.markdown("""
<style>
    .main .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 100% !important;
    }
    
    .card-hoy {
        background-color: #E8F5E9;
        border-left: 6px solid #2E7D32;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 12px;
        color: #1B5E20;
    }
    .card-proximo {
        background-color: #E3F2FD;
        border-left: 6px solid #1565C0;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 12px;
        color: #0D47A1;
    }
    .card-header {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .card-sub {
        font-size: 13px;
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

# Generación automática de lista con formato completo hh:mm AM/PM en un solo cuadro
HORAS_OPCIONES = []
for h in range(8, 24):  # Desde 8:00 AM hasta 11:30 PM
    ampm = "AM" if h < 12 else "PM"
    h12 = h if h <= 12 else h - 12
    if h12 == 0:
        h12 = 12
    HORAS_OPCIONES.append(f"{h12:02d}:00 {ampm}")
    HORAS_OPCIONES.append(f"{h12:02d}:30 {ampm}")

# Función que genera solo UN cuadro de selección desplegable
def selector_hora_unica(label, key, default_index=16):
    return st.selectbox(
        label, 
        options=HORAS_OPCIONES, 
        index=default_index, 
        key=key
    )

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
        
        filtro_cliente = st.text_input("👤 Cliente / Nombre del Evento:", placeholder="Buscar por cliente o evento...")
        filtro_telefono = st.text_input("📱 Número de Teléfono:", placeholder="Buscar por número...")
        rango_fechas = st.date_input("📅 Rango de Fechas:", value=())

        tiene_filtro_fechas = isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2
        filtro_activo = bool(filtro_cliente.strip() or filtro_telefono.strip() or tiene_filtro_fechas)

        if not filtro_activo:
            st.info("👉 Ingresa un nombre, número de teléfono o selecciona un rango de fechas.")
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
    # 3. PESTAÑA: NUEVO (UN SOLO CUADRO DE HORA COMPACTO)
    # =========================================================
    with tab_nuevo:
        # Fila 1: Fecha y Tipo de Servicio
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            fecha_input = st.date_input("📅 Fecha del Servicio", datetime.now())
            fecha_str = fecha_input.strftime("%Y-%m-%d")
        with col_f2:
            tipo_servicio = st.selectbox("🎭 Servicio", ["Show", "Decoración", "Show + Decoración", "Alquiler"])

        st.markdown("---")

        # Fila 2: Nombre de Evento y Cliente
        nombre_evento = st.text_input("🎉 Nombre del Evento", placeholder="ej. Cumpleaños de Gia")
        cliente = st.text_input("👤 Nombre del Cliente", placeholder="ej. María López")

        st.markdown("---")

        # Fila 3: Horas lado a lado en un solo cuadro selector cada una
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            hora_contrato_str = selector_hora_unica("⏰ Hora Contrato", "h_contrato_single", default_index=16)
        with col_h2:
            hora_invitacion_str = selector_hora_unica("📩 Hora Citación", "h_citacion_single", default_index=16)

        st.markdown("---")

        # Fila 4: Dirección
        direccion = st.text_input("📍 Dirección del Evento", placeholder="ej. Av. Las Flores 123")

        st.markdown("---")

        # Fila 5: Teléfono y Alquiler
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            telefono = st.text_input("📱 Teléfono", placeholder="ej. 987654321")
        with col_t2:
            agregar_alquiler = st.radio("📦 ¿Alquiler?", ["No", "Sí"], horizontal=True)

        concepto_alquiler = ""
        monto_alquiler = 0
        if agregar_alquiler == "Sí" or tipo_servicio == "Alquiler":
            st.markdown("##### 📦 Detalles del Alquiler")
            col_alq1, col_alq2 = st.columns(2)
            with col_alq1:
                concepto_alquiler = st.text_input("Concepto", placeholder="ej. Luces, Toldo")
            with col_alq2:
                monto_alquiler = st.number_input("Monto (S/)", min_value=0, step=1, value=0)

        st.markdown("---")
        st.markdown("### 💰 Montos y Pagos")

        costo_total = 0
        costo_show = 0
        costo_deco = 0

        if tipo_servicio == "Show + Decoración":
            st.info("💡 **Show + Decoración:** Ingresa montos independientes:")
            col_sd1, col_sd2 = st.columns(2)
            with col_sd1:
                costo_show = st.number_input("Show (S/)", min_value=0, step=1, value=0, key="c_show")
            with col_sd2:
                costo_deco = st.number_input("Decoración (S/)", min_value=0, step=1, value=0, key="c_deco")

            costo_total = costo_show + costo_deco + monto_alquiler
            st.markdown(f"**Total:** S/ {costo_total}")

        elif tipo_servicio in ["Show", "Decoración"]:
            costo_base = st.number_input(f"Costo Servicio ({tipo_servicio}) (S/)", min_value=0, step=1, value=0, key="c_base")
            costo_total = costo_base + monto_alquiler
        else:
            costo_total = monto_alquiler

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            monto_adelanto = st.number_input("Adelanto (S/)", min_value=0, step=1, value=0, key="c_adelanto")

        monto_pendiente = max(0, int(costo_total) - int(monto_adelanto))

        with col_p2:
            st.write("")
            if monto_pendiente == 0 and costo_total > 0:
                st.success("✅ **CANCELADO**")
                estado_pago = "Pago completo"
            else:
                st.warning(f"💵 **PENDIENTE:** S/ {monto_pendiente}")
                estado_pago = "Pago parcial"

        st.markdown("---")
        descripcion = st.text_area("📝 Observaciones", placeholder="Detalles adicionales...")

        if st.button("💾 Guardar Servicio", use_container_width=True, type="primary"):
            if not GOOGLE_SCRIPT_URL:
                st.error("⚠️ Falta configurar GOOGLE_SCRIPT_URL.")
            else:
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
                        st.success("🎉 ¡Servicio guardado con éxito!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Error HTTP {res.status_code}")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
