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

# CSS: Fondo y estilos visuales con colores diferenciados por marca
css_fondo = ""
if imagen_fondo_b64:
    css_fondo = f"""
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.65), rgba(0, 0, 0, 0.65)), url("{imagen_fondo_b64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    """

st.markdown(f"""
<style>
    {css_fondo}

    /* Tarjeta contenedora principal */
    [data-testid="stAppViewContainer"] > .main {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 14px;
        padding: 14px !important;
        margin-top: 10px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }}

    /* Encabezado */
    .header-container {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }}
    
    .header-logo {{
        width: 62px;
        height: 62px;
        object-fit: contain;
        border-radius: 50%;
        border: 2px solid #FFFFFF;
        box-shadow: 0 3px 10px rgba(0,0,0,0.5);
    }}

    .header-title {{
        font-size: 34px;
        font-weight: 900;
        background: linear-gradient(45deg, #FF007F, #FF8C00, #00E5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
        line-height: 1.1;
        letter-spacing: 0.5px;
        filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.9));
    }}

    /* Legibilidad de textos */
    label, p, span, div, .stMarkdown, .stRadio label, .stCheckbox label {{
        color: #000000 !important;
        font-weight: 800 !important;
        text-shadow: 0px 0px 3px rgba(255, 255, 255, 0.9), 0px 0px 1px #FFFFFF;
    }}

    /* Inputs */
    div[data-testid="stTextInput"] input, 
    div[data-testid="stNumberInput"] input, 
    div[data-testid="stSelectbox"] select, 
    div[data-testid="stTextArea"] textarea {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #DDDDDD !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}

    /* Bloqueo de scroll horizontal */
    html, body, [data-testid="stAppViewContainer"], .main {{
        overflow-x: hidden !important;
    }}
    .main .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }}

    div[data-testid="stVerticalBlock"] > div {{
        margin-bottom: -6px !important;
        padding-bottom: 0px !important;
    }}

    div[data-testid="column"] {{
        min-width: 0px !important;
    }}

    /* ESTILOS DE TARJETAS POR MARCA */
    .card-madai {{
        background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%) !important;
        border-left: 8px solid #00838F;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 131, 143, 0.2);
    }}
    
    .badge-madai {{
        background-color: #00838F;
        color: #FFFFFF !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        text-shadow: none !important;
    }}

    .card-risuena {{
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%) !important;
        border-left: 8px solid #7B1FA2;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(123, 31, 162, 0.2);
    }}

    .badge-risuena {{
        background-color: #7B1FA2;
        color: #FFFFFF !important;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        text-shadow: none !important;
    }}

    .card-header {{
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 6px;
        color: #000000;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .card-sub {{
        font-size: 13px;
        color: #111111;
        margin-bottom: 3px;
    }}

    /* Estilo de Ficha Completa del Evento */
    .ficha-completa {{
        background-color: #FFFFFF !important;
        border: 2px dashed #00838F;
        border-radius: 10px;
        padding: 12px;
        margin-top: 8px;
        margin-bottom: 12px;
    }}
</style>
""", unsafe_allow_html=True)

# Encabezado
html_logo = f'<img src="{imagen_logo_b64}" class="header-logo">' if imagen_logo_b64 else ''
st.markdown(f"""
<div class="header-container">
    {html_logo}
    <h1 class="header-title">Agenda Madai</h1>
</div>
""", unsafe_allow_html=True)

if "menu_activo" not in st.session_state:
    st.session_state["menu_activo"] = "Eventos"

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

GOOGLE_SHEET_URL = st.secrets.get("GOOGLE_SHEET_URL", os.environ.get("GOOGLE_SHEET_URL", ""))
GOOGLE_SCRIPT_URL = st.secrets.get("GOOGLE_SCRIPT_URL", os.environ.get("GOOGLE_SCRIPT_URL", ""))

@st.cache_data(ttl=0)
def cargar_datos(url):
    if not url:
        return pd.DataFrame()
    try:
        df = pd.read_csv(url, dtype=str)
        df = df.fillna("")
        df.columns = [str(c).strip() for c in df.columns]

        columnas_reales = [
            "Marca", "Fecha", "Tipo", "Evento", "Hora", 
            "Direccion", "Hora_Invitacion", "Cliente", "Telefono", 
            "Costo_Total", "Monto_Adelanto", 
            "Descripcion", "Desglose_Costos", "Concepto_Alquiler"
        ]

        if len(df.columns) >= len(columnas_reales):
            dict_renombres = {}
            for i, col in enumerate(columnas_reales):
                if i < len(df.columns):
                    dict_renombres[df.columns[i]] = col
            df = df.rename(columns=dict_renombres)

        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

def obtener_valor(row, col_name):
    val = row.get(col_name, "")
    if isinstance(val, pd.Series):
        val = val.iloc[0] if not val.empty else ""
    return str(val).strip()

def renderizar_tarjeta(row, index_evento, muestra_fecha=False):
    marca = obtener_valor(row, "Marca") or "Madai"
    
    # Asignar clase CSS según la marca
    if marca.lower() == "risueña":
        clase_tarjeta = "card-risuena"
        clase_badge = "badge-risuena"
    else:
        clase_tarjeta = "card-madai"
        clase_badge = "badge-madai"

    v_fecha = obtener_valor(row, "Fecha")
    v_evento = obtener_valor(row, "Evento") or "Evento"
    v_tipo = obtener_valor(row, "Tipo")
    h_contrato = obtener_valor(row, "Hora") or "N/A"
    h_citacion = obtener_valor(row, "Hora_Invitacion") or "N/A"
    v_cliente = obtener_valor(row, "Cliente") or "N/A"
    v_telefono = obtener_valor(row, "Telefono") or "N/A"
    v_lugar = obtener_valor(row, "Direccion") or "N/A"
    
    try:
        v_total_num = float(obtener_valor(row, "Costo_Total") or 0)
        v_adelanto_num = float(obtener_valor(row, "Monto_Adelanto") or 0)
        v_pendiente_num = max(0, int(v_total_num - v_adelanto_num))
    except ValueError:
        v_total_num = 0
        v_pendiente_num = 0

    texto_fecha = f"📅 {v_fecha} | " if muestra_fecha else ""

    # Tarjeta Principal
    st.markdown(f"""
    <div class="{clase_tarjeta}">
        <div class="card-header">
            <span>{texto_fecha}🎉 {v_evento} ({v_tipo})</span>
            <span class="{clase_badge}">🏷️ {marca.upper()}</span>
        </div>
        <div class="card-sub">⏰ <b>Hora Contrato:</b> {h_contrato} | <b>Citación:</b> {h_citacion}</div>
        <div class="card-sub">👤 <b>Cliente:</b> {v_cliente} | 📱 <b>Tel:</b> {v_telefono}</div>
        <div class="card-sub">📍 <b>Lugar:</b> {v_lugar}</div>
        <div class="card-sub">💰 <b>Total:</b> S/ {int(v_total_num)} | <b>Pendiente:</b> S/ {v_pendiente_num}</div>
    </div>
    """, unsafe_allow_html=True)

    # Key único por evento para session_state
    event_key = f"evt_{index_evento}_{v_fecha}_{v_cliente}"

    # Estado para la visibilidad de la ficha completa
    if f"ver_ficha_{event_key}" not in st.session_state:
        st.session_state[f"ver_ficha_{event_key}"] = False

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("📋 Ver Ficha Completa", key=f"btn_ver_ficha_{event_key}", use_container_width=True):
            st.session_state[f"ver_ficha_{event_key}"] = not st.session_state[f"ver_ficha_{event_key}"]
            st.rerun()

    # DESPLEGABLE DE GESTIÓN (Asignar personal)
    with st.expander("⚙️ Asignar Personal y Editar Detalles"):
        if f"num_dalinas_{event_key}" not in st.session_state:
            st.session_state[f"num_dalinas_{event_key}"] = 1

        num_dalinas = st.session_state[f"num_dalinas_{event_key}"]
        st.markdown(f"**💃 Dalinas asignadas ({num_dalinas}/7):**")

        for i in range(num_dalinas):
            st.text_input(f"Nombre de Dalina {i+1}", key=f"dalina_{i}_{event_key}", placeholder=f"ej. Dalina {i+1}")

        c_add, c_rem = st.columns(2)
        with c_add:
            if num_dalinas < 7:
                if st.button("➕ Agregar Dalina", key=f"btn_add_dalina_{event_key}", use_container_width=True):
                    st.session_state[f"num_dalinas_{event_key}"] += 1
                    st.rerun()
        with c_rem:
            if num_dalinas > 1:
                if st.button("➖ Quitar Dalina", key=f"btn_rem_dalina_{event_key}", use_container_width=True):
                    st.session_state[f"num_dalinas_{event_key}"] -= 1
                    st.rerun()

        st.write("---")

        opciones_animador = ["Ninguno(a)", "Madai", "Martha", "Eusy", "Antonio", "Jair", "Britny", "Gina"]
        st.selectbox("🎤 Animador(a):", opciones_animador, key=f"animador_{event_key}")

        col_dj, col_staff = st.columns(2)
        with col_dj:
            st.text_input("🎧 DJ:", key=f"dj_{event_key}", placeholder="Nombre del DJ")
        with col_staff:
            st.text_input("🛠️ Staff / Apoyo:", key=f"staff_{event_key}", placeholder="Nombre del staff")

        st.text_input("⏳ Duración:", key=f"duracion_{event_key}", placeholder="ej. 2 Horas / 30 min")
        st.text_area("📝 Detalles adicionales:", key=f"detalles_{event_key}", placeholder="Notas extra...")

        if st.button("💾 Guardar Personal", key=f"btn_save_details_{event_key}", use_container_width=True, type="primary"):
            st.success("✅ Datos del evento actualizados.")

    # MOSTRAR LA FICHA COMPLETA SI EL BOTÓN FUE PRESIONADO
    if st.session_state[f"ver_ficha_{event_key}"]:
        # Recopilar Dalinas
        dalinas_list = []
        n_dal = st.session_state.get(f"num_dalinas_{event_key}", 1)
        for i in range(n_dal):
            val_dal = st.session_state.get(f"dalina_{i}_{event_key}", "").strip()
            if val_dal:
                dalinas_list.append(val_dal)
        
        str_dalinas = ", ".join(dalinas_list) if dalinas_list else "Ninguna asignada"
        anim_val = st.session_state.get(f"animador_{event_key}", "Ninguno(a)")
        dj_val = st.session_state.get(f"dj_{event_key}", "").strip() or "No asignado"
        staff_val = st.session_state.get(f"staff_{event_key}", "").strip() or "No asignado"
        dur_val = st.session_state.get(f"duracion_{event_key}", "").strip() or "No especificada"
        det_val = st.session_state.get(f"detalles_{event_key}", "").strip() or "Sin detalles"

        st.markdown(f"""
        <div class="ficha-completa">
            <h4 style="margin-top:0; color:#00838F; text-align:center;">📜 FICHA COMPLETA DEL EVENTO</h4>
            <hr style="margin: 6px 0;">
            <p><b>🏷️ Marca:</b> {marca.upper()} | <b>🎉 Evento:</b> {v_evento} ({v_tipo})</p>
            <p><b>📅 Fecha:</b> {v_fecha} | <b>⏰ Contrato:</b> {h_contrato} | <b>Citación:</b> {h_citacion}</p>
            <p><b>👤 Cliente:</b> {v_cliente} | <b>📱 Teléfono:</b> {v_telefono}</p>
            <p><b>📍 Ubicación:</b> {v_lugar}</p>
            <p><b>💰 Total:</b> S/ {int(v_total_num)} | <b>Monto Pendiente:</b> S/ {v_pendiente_num}</p>
            <hr style="margin: 6px 0;">
            <h5 style="margin: 4px 0; color:#7B1FA2;">👥 PERSONAL ASIGNADO:</h5>
            <p><b>💃 Dalina(s):</b> {str_dalinas}</p>
            <p><b>🎤 Animador(a):</b> {anim_val}</p>
            <p><b>🎧 DJ:</b> {dj_val} | <b>🛠️ Staff:</b> {staff_val}</p>
            <p><b>⏳ Duración del Show:</b> {dur_val}</p>
            <p><b>📝 Notas/Detalles:</b> {det_val}</p>
        </div>
        """, unsafe_allow_html=True)

if not GOOGLE_SHEET_URL:
    st.warning("⚠️ Configura GOOGLE_SHEET_URL en los secretos de Streamlit.")
else:
    df = cargar_datos(GOOGLE_SHEET_URL)

    # =========================================================
    # 1. MENÚ: EVENTOS
    # =========================================================
    if st.session_state["menu_activo"] == "Eventos":
        if "mensaje_exito" in st.session_state:
            st.success(st.session_state.pop("mensaje_exito"))

        c_top1, c_top2 = st.columns([3, 1])
        with c_top2:
            if st.button("🔄 Actualizar", key="btn_refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

        if not df.empty and "Fecha" in df.columns:
            df_copia = df.copy()
            df_copia["Fecha_Str"] = df_copia["Fecha"].astype(str).str.strip()

            try:
                from zoneinfo import ZoneInfo
                hoy_date = datetime.now(ZoneInfo("America/Lima")).date()
            except Exception:
                hoy_date = (datetime.utcnow() - timedelta(hours=5)).date()

            modo_vista = st.radio(
                "Ver eventos por categoría:",
                ["Eventos del día (Hoy)", "Próximos 3 días", "Todos los eventos agendados"],
                horizontal=True
            )

            df_copia["Fecha_Date"] = pd.to_datetime(df_copia["Fecha_Str"], format="%Y-%m-%d", errors="coerce").dt.date

            if modo_vista == "Eventos del día (Hoy)":
                df_hoy = df_copia[df_copia["Fecha_Date"] == hoy_date]

                if not df_hoy.empty:
                    for idx, row in df_hoy.iterrows():
                        renderizar_tarjeta(row, index_evento=idx, muestra_fecha=False)
                else:
                    st.info(f"No hay eventos registrados para hoy ({hoy_date.strftime('%Y-%m-%d')}).")

            elif modo_vista == "Próximos 3 días":
                limite_3dias = hoy_date + timedelta(days=3)
                mask_3dias = (df_copia["Fecha_Date"] >= hoy_date) & (df_copia["Fecha_Date"] <= limite_3dias)
                df_3dias = df_copia[mask_3dias].sort_values("Fecha_Date")

                if not df_3dias.empty:
                    for idx, row in df_3dias.iterrows():
                        renderizar_tarjeta(row, index_evento=idx, muestra_fecha=True)
                else:
                    st.info("No hay eventos registrados dentro de los próximos 3 días.")

            else:
                df_todos = df_copia.sort_values("Fecha_Date", ascending=True, na_position="last")

                if not df_todos.empty:
                    for idx, row in df_todos.iterrows():
                        renderizar_tarjeta(row, index_evento=idx, muestra_fecha=True)
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
                df_filtrado["Fecha_DT"] = pd.to_datetime(df_filtrado["Fecha"], errors="coerce")

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
        marca_seleccionada = st.radio("🏷️ Selecciona la Marca", ["Madai", "Risueña"], horizontal=True)

        fecha_input = st.date_input("📅 Fecha", datetime.now())
        fecha_str = fecha_input.strftime("%Y-%m-%d")

        tipo_servicio = st.selectbox("🎭 Servicio", ["Show", "Decoración", "Show + Decoración", "Alquiler"])

        nombre_evento = st.text_input("🎉 Evento", placeholder="ej. Cumpleaños Gia")

        cliente = st.text_input("👤 Cliente", placeholder="ej. María López")

        # HORA CONTRATO
        st.caption("⏰ **Hora Contrato**")
        c1, c2 = st.columns([3.5, 1.2])
        with c1:
            h_contrato_val = st.text_input("HC", value="04:30", key="hc_val", label_visibility="collapsed")
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

        # CHECK DE PAGO TOTAL Y LÓGICA DE ADELANTO
        pago_total = st.checkbox("✅ Pago Total")

        if pago_total:
            monto_adelanto = costo_total
            st.number_input("Adelanto (S/)", min_value=0, value=int(monto_adelanto), disabled=True, key="c_adelanto_dis")
        else:
            monto_adelanto = st.number_input("Adelanto (S/)", min_value=0, step=1, value=0, key="c_adelanto")

        monto_pendiente = max(0, int(costo_total) - int(monto_adelanto))

        if monto_pendiente == 0 and costo_total > 0:
            st.success("✅ SERVICIO TOTALMENTE CANCELADO")
        else:
            st.warning(f"💵 MONTO PENDIENTE: S/ {monto_pendiente}")

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
                    "Marca": marca_seleccionada,
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
