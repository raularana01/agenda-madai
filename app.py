import streamlit as st
import pandas as pd
import requests
import json
import os
import base64
from datetime import datetime, timedelta

# Configuración de la página
st.set_page_config(page_title="Agenda Madai", page_icon="📅", layout="centered")

# Función para convertir imágenes locales a Base64
def obtener_base64_de_archivo(ruta_imagen):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        extension = ruta_imagen.split('.')[-1].lower()
        mime = 'image/png' if extension == 'png' else 'image/jpeg'
        return f"data:{mime};base64,{encoded_string}"
    return None

# Cargar imágenes en Base64
imagen_fondo_b64 = obtener_base64_de_archivo("fondo.jpeg")
imagen_logo_b64 = obtener_base64_de_archivo("logo.jpeg")

# Configurar CSS para fondo con menor contraste y textos legibles
css_fondo = ""
if imagen_fondo_b64:
    css_fondo = f"""
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), url("{imagen_fondo_b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    """

st.markdown(f"""
<style>
    {css_fondo}

    /* Fondo contenedor principal para garantizar contraste */
    [data-testid="stAppViewContainer"] > .main {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-radius: 12px;
        padding: 15px !important;
        margin-top: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}

    /* Encabezado: Logo y Título "Agenda Madai" */
    .header-container {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 15px;
    }}
    
    .header-logo {{
        width: 65px;
        height: 65px;
        object-fit: contain;
        border-radius: 50%;
        border: 2px solid #FFF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}

    .header-title {{
        font-size: 34px;
        font-weight: 900;
        background: linear-gradient(45deg, #FF007F, #FFD700, #00E5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
        line-height: 1.1;
        letter-spacing: 0.5px;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.8));
    }}

    /* Estilo de textos del sistema para resaltar sobre el fondo */
    label, .stRadio label, p, .stMarkdown {{
        color: #111111 !important;
        font-weight: 600 !important;
    }}

    /* Cajas informativas e inputs */
    .stAlert {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 8px !important;
        border-left: 5px solid #2196F3 !important;
    }}

    /* Bloqueo de scroll horizontal */
    html, body, [data-testid="stAppViewContainer"], .main {{
        overflow-x: hidden !important;
    }}
    .main .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
        max-width: 100% !important;
    }}

    /* Reducir espacio vertical */
    div[data-testid="stVerticalBlock"] > div {{
        margin-bottom: -6px !important;
        padding-bottom: 0px !important;
    }}

    div[data-testid="stTextInput"] input {{
        text-align: left !important;
        padding-left: 10px !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }}

    div[data-testid="column"] {{
        min-width: 0px !important;
    }}

    /* Tarjetas de eventos con sombra y contraste alto */
    .card-hoy {{
        background-color: rgba(255, 255, 255, 0.95);
        border-left: 6px solid #2E7D32;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: #1B5E20;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }}
    .card-proximo {{
        background-color: rgba(255, 255, 255, 0.95);
        border-left: 6px solid #1565C0;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: #0D47A1;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }}
    .card-header {{
        font-size: 15px;
        font-weight: bold;
        margin-bottom: 3px;
    }}
    .card-sub {{
        font-size: 13px;
        color: #222222;
        margin-bottom: 2px;
    }}
</style>
""", unsafe_allow_html=True)

# Encabezado: Logo + Título Agenda Madai
html_logo = f'<img src="{imagen_logo_b64}" class="header-logo">' if imagen_logo_b64 else ''
st.markdown(f"""
<div class="header-container">
    {html_logo}
    <h1 class="header-title">Agenda Madai</h1>
</div>
""", unsafe_allow_html=True)

# Control del menú mediante session_state
if "menu_activo" not in st.session_state:
    st.session_state["menu_activo"] = "Eventos"

# Menú superior tipo pestañas creadas con botones
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    if st.button("📋 Eventos", use_container_width=True, type="primary" if st.session_state["menu_activo"] == "Eventos" else "secondary"):
        st.session_state["menu_activo"] = "Eventos"
        st.rerun()
with col_m2:
    if st.button("🔍 Filtro", use_container_width=True, type="primary" if st.session_state["menu_activo"] == "Filtro" else "secondary"):
        st.session_state["menu_activo"] = "Filtro"
        st.rerun()
with col_m3:
    if st.button("➕ Nuevo", use_container_width=True, type="primary" if st.session_state["menu_activo"] == "Nuevo" else "secondary"):
        st.session_state["menu_activo"] = "Nuevo"
        st.rerun()

st.write("---")

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

if not GOOGLE_SHEET_URL:
    st.warning("⚠️ Configura GOOGLE_SHEET_URL en los secretos de Streamlit.")
else:
    df = cargar_datos(GOOGLE_SHEET_URL)

    # =========================================================
    # 1. MENÚ: EVENTOS (PANTALLA DE INICIO)
    # =========================================================
    if st.session_state["menu_activo"] == "Eventos":
        if "mensaje_exito" in st.session_state:
            st.success(st.session_state.pop("mensaje_exito"))

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
    # 2. MENÚ: FILTRO
    # =========================================================
    elif st.session_state["menu_activo"] == "Filtro":
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
    # 3. MENÚ: NUEVO (FORMULARIO)
    # =========================================================
    elif st.session_state["menu_activo"] == "Nuevo":
        fecha_input = st.date_input("📅 Fecha", datetime.now())
        fecha_str = fecha_input.strftime("%Y-%m-%d")

        tipo_servicio = st.selectbox("🎭 Servicio", ["Show", "Decoración", "Show + Decoración", "Alquiler"])

        nombre_evento = st.text_input("🎉 Evento", placeholder="ej. Cumpleaños Gia")

        cliente = st.text_input("👤 Cliente", placeholder="ej. María López")

        # HORA CONTRATO
        st.caption("⏰ **Hora Contrato**")
        c1, c2 = st.columns([3.5, 1.2])
        with c1:
            h_contrato_val = st.text_input("HC", value="04:00", key="hc_val", label_visibility="collapsed")
        with c2:
            ampm_contrato = st.selectbox("AP1", ["PM", "AM"], key="hc_ap", label_visibility="collapsed")
        hora_contrato_str = f"{h_contrato_val.strip()} {ampm_contrato}"

        # HORA CITACIÓN
        st.caption("📩 **Hora Citación**")
        c3, c4 = st.columns([3.5, 1.2])
        with c3:
            h_citacion_val = st.text_input("HI", value="04:00", key="hi_val", label_visibility="collapsed")
        with c4:
            ampm_citacion = st.selectbox("AP2", ["PM", "AM"], key="hi_ap", label_visibility="collapsed")
        hora_invitacion_str = f"{h_citacion_val.strip()} {ampm_citacion}"

        direccion = st.text_input("📍 Dirección", placeholder="ej. Av. Las Flores 123")

        telefono = st.text_input("📱 Teléfono", placeholder="ej. 987654321")

        agregar_alquiler = st.radio("📦 ¿Alquiler?", ["No", "Sí"], horizontal=True)

        concepto_alquiler = ""
        monto_alquiler = 0
        if agregar_alquiler == "Sí" or tipo_servicio == "Alquiler":
            concepto_alquiler = st.text_input("Concepto Alquiler", placeholder="ej. Luces, Toldo")
            monto_alquiler = st.number_input("Monto Alquiler (S/)", min_value=0, step=1, value=0)

        costo_total = 0
        costo_show = 0
        costo_deco = 0

        if tipo_servicio == "Show + Decoración":
            costo_show = st.number_input("Show (S/)", min_value=0, step=1, value=0, key="c_show")
            costo_deco = st.number_input("Decoración (S/)", min_value=0, step=1, value=0, key="c_deco")
            costo_total = costo_show + costo_deco + monto_alquiler
        elif tipo_servicio in ["Show", "Decoración"]:
            costo_base = st.number_input(f"Costo {tipo_servicio} (S/)", min_value=0, step=1, value=0, key="c_base")
            costo_total = costo_base + monto_alquiler
        else:
            costo_total = monto_alquiler

        monto_adelanto = st.number_input("Adelanto (S/)", min_value=0, step=1, value=0, key="c_adelanto")

        monto_pendiente = max(0, int(costo_total) - int(monto_adelanto))

        st.caption("Estado de Pago")
        if monto_pendiente == 0 and costo_total > 0:
            st.success("✅ CANCELADO")
            estado_pago = "Pago completo"
        else:
            st.warning(f"💵 PENDIENTE: S/ {monto_pendiente}")
            estado_pago = "Pago parcial"

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
                        st.cache_data.clear()
                        st.session_state["menu_activo"] = "Eventos"
                        st.session_state["mensaje_exito"] = "🎉 ¡Servicio guardado con éxito!"
                        st.rerun()
                    else:
                        st.error(f"Error HTTP {res.status_code}")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
