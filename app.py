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

# CSS: Reducción de espacios y fondo
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

    /* Reducción máxima de márgenes y paddings en contenedor principal */
    [data-testid="stAppViewContainer"] > .main {{
        background-color: rgba(255, 255, 255, 0.96) !important;
        border-radius: 12px;
        padding: 8px !important;
        margin-top: 5px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }}

    .block-container {{
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
        max-width: 100% !important;
    }}

    /* Reducir espacio entre bloques verticales */
    div[data-testid="stVerticalBlock"] > div {{
        margin-bottom: -10px !important;
        padding-bottom: 0px !important;
    }}

    /* Encabezado compacto */
    .header-container {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
    }}
    
    .header-logo {{
        width: 48px;
        height: 48px;
        object-fit: contain;
        border-radius: 50%;
        border: 2px solid #FFFFFF;
    }}

    .header-title {{
        font-size: 26px;
        font-weight: 900;
        background: linear-gradient(45deg, #FF007F, #FF8C00, #00E5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
        line-height: 1;
    }}

    /* Legibilidad de textos */
    label, p, span, div, .stMarkdown, .stRadio label, .stCheckbox label {{
        color: #000000 !important;
        font-weight: 800 !important;
    }}

    /* Tarjetas Compactas */
    .card-madai {{
        background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%) !important;
        border-left: 6px solid #00838F;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 4px;
        box-shadow: 0 2px 8px rgba(0, 131, 143, 0.15);
    }}

    .card-risuena {{
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%) !important;
        border-left: 6px solid #7B1FA2;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 4px;
        box-shadow: 0 2px 8px rgba(123, 31, 162, 0.15);
    }}

    .badge-madai {{
        background-color: #00838F;
        color: #FFFFFF !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }}

    .badge-risuena {{
        background-color: #7B1FA2;
        color: #FFFFFF !important;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }}

    .card-header {{
        font-size: 15px;
        font-weight: bold;
        margin-bottom: 4px;
        color: #000000;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .card-sub {{
        font-size: 12px;
        color: #111111;
        margin-bottom: 2px;
        line-height: 1.2;
    }}

    /* Botones diminutos/compactos para las tarjetas */
    div[data-testid="stColumn"] button {{
        padding: 2px 6px !important;
        font-size: 11px !important;
        min-height: 28px !important;
        height: 28px !important;
    }}
</style>
""", unsafe_allow_html=True)

# Encabezado Compacto
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

# =========================================================
# VENTANAS EMERGENTES (DIALOGS)
# =========================================================

@st.dialog("👤 Asignar Personal al Evento")
def abrir_dialogo_personal(event_key):
    # Recuperar o inicializar estado guardado
    datos_guardados = st.session_state.get(f"data_personal_{event_key}", {})
    
    num_dalinas_init = datos_guardados.get("num_dalinas", 1)
    if f"temp_num_dalinas_{event_key}" not in st.session_state:
        st.session_state[f"temp_num_dalinas_{event_key}"] = num_dalinas_init

    num_dalinas = st.session_state[f"temp_num_dalinas_{event_key}"]
    st.markdown(f"**💃 Dalinas ({num_dalinas}/7):**")

    dalinas_inputs = []
    for i in range(num_dalinas):
        val_default = datos_guardados.get("dalinas", [])[i] if i < len(datos_guardados.get("dalinas", [])) else ""
        nombre_d = st.text_input(f"Dalina {i+1}", value=val_default, key=f"dlg_dalina_{i}_{event_key}", placeholder=f"Nombre Dalina {i+1}")
        dalinas_inputs.append(nombre_d)

    c_add, c_rem = st.columns(2)
    with c_add:
        if num_dalinas < 7:
            if st.button("➕ Agregar Dalina", key=f"dlg_btn_add_{event_key}", use_container_width=True):
                st.session_state[f"temp_num_dalinas_{event_key}"] += 1
                st.rerun()
    with c_rem:
        if num_dalinas > 1:
            if st.button("➖ Quitar Dalina", key=f"dlg_btn_rem_{event_key}", use_container_width=True):
                st.session_state[f"temp_num_dalinas_{event_key}"] -= 1
                st.rerun()

    st.write("---")

    opciones_animador = ["Ninguno(a)", "Madai", "Martha", "Eusy", "Antonio", "Jair", "Britny", "Gina"]
    anim_idx = opciones_animador.index(datos_guardados.get("animador", "Ninguno(a)")) if datos_guardados.get("animador") in opciones_animador else 0
    animador_val = st.selectbox("🎤 Animador(a):", opciones_animador, index=anim_idx, key=f"dlg_anim_{event_key}")

    c_dj, c_st = st.columns(2)
    with c_dj:
        dj_val = st.text_input("🎧 DJ:", value=datos_guardados.get("dj", ""), key=f"dlg_dj_{event_key}", placeholder="Nombre DJ")
    with c_st:
        staff_val = st.text_input("🛠️ Staff:", value=datos_guardados.get("staff", ""), key=f"dlg_staff_{event_key}", placeholder="Nombre Staff")

    duracion_val = st.text_input("⏳ Duración:", value=datos_guardados.get("duracion", ""), key=f"dlg_dur_{event_key}", placeholder="ej. 2 Horas")
    detalles_val = st.text_area("📝 Detalles:", value=datos_guardados.get("detalles", ""), key=f"dlg_det_{event_key}", placeholder="Observaciones...")

    if st.button("💾 Guardar Datos", key=f"dlg_btn_save_{event_key}", use_container_width=True, type="primary"):
        # Guardar permanentemente en session_state
        st.session_state[f"data_personal_{event_key}"] = {
            "num_dalinas": num_dalinas,
            "dalinas": [d.strip() for d in dalinas_inputs if d.strip()],
            "animador": animador_val,
            "dj": dj_val.strip(),
            "staff": staff_val.strip(),
            "duracion": duracion_val.strip(),
            "detalles": detalles_val.strip()
        }
        st.rerun()

@st.dialog("📜 Ficha Completa del Evento")
def abrir_dialogo_ficha(row, event_key):
    marca = obtener_valor(row, "Marca") or "Madai"
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
        v_total_num, v_pendiente_num = 0, 0

    datos_p = st.session_state.get(f"data_personal_{event_key}", {})
    dalinas_str = ", ".join(datos_p.get("dalinas", [])) if datos_p.get("dalinas") else "Ninguna asignada"
    anim_str = datos_p.get("animador", "Ninguno(a)")
    dj_str = datos_p.get("dj") or "No asignado"
    staff_str = datos_p.get("staff") or "No asignado"
    dur_str = datos_p.get("duracion") or "No especificada"
    det_str = datos_p.get("detalles") or "Sin detalles"

    st.markdown(f"""
    <div style="font-size: 13px; line-height: 1.4;">
        <p><b>🏷️ Marca:</b> {marca.upper()} | <b>🎉 Evento:</b> {v_evento} ({v_tipo})</p>
        <p><b>📅 Fecha:</b> {v_fecha} | <b>⏰ Contrato:</b> {h_contrato} | <b>Citación:</b> {h_citacion}</p>
        <p><b>👤 Cliente:</b> {v_cliente} | <b>📱 Teléfono:</b> {v_telefono}</p>
        <p><b>📍 Ubicación:</b> {v_lugar}</p>
        <p><b>💰 Total:</b> S/ {int(v_total_num)} | <b>Monto Pendiente:</b> S/ {v_pendiente_num}</p>
        <hr style="margin: 6px 0;">
        <p style="color:#7B1FA2; font-weight:bold; margin-bottom:4px;">👥 PERSONAL Y SHOW:</p>
        <p><b>💃 Dalina(s):</b> {dalinas_str}</p>
        <p><b>🎤 Animador(a):</b> {anim_str}</p>
        <p><b>🎧 DJ:</b> {dj_str} | <b>🛠️ Staff:</b> {staff_str}</p>
        <p><b>⏳ Duración:</b> {dur_str}</p>
        <p><b>📝 Detalles:</b> {det_str}</p>
    </div>
    """, unsafe_allow_html=True)


def renderizar_tarjeta(row, index_evento, muestra_fecha=False):
    marca = obtener_valor(row, "Marca") or "Madai"
    clase_tarjeta = "card-risuena" if marca.lower() == "risueña" else "card-madai"
    clase_badge = "badge-risuena" if marca.lower() == "risueña" else "badge-madai"

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
        v_total_num, v_pendiente_num = 0, 0

    texto_fecha = f"📅 {v_fecha} | " if muestra_fecha else ""

    # Tarjeta Ultra Simplificada
    st.markdown(f"""
    <div class="{clase_tarjeta}">
        <div class="card-header">
            <span>{texto_fecha}🎉 {v_evento} ({v_tipo})</span>
            <span class="{clase_badge}">🏷️ {marca.upper()}</span>
        </div>
        <div class="card-sub">⏰ <b>Hora Contrato:</b> {h_contrato} | <b>Citación:</b> {h_citacion}</div>
        <div class="card-sub">👤 <b>Cliente:</b> {v_cliente} | 📱 <b>Tel:</b> {v_telefono}</div>
        <div class="card-sub">📍 <b>Lugar:</b> {v_lugar} | 💰 <b>Total:</b> S/ {int(v_total_num)} | <b>Pendiente:</b> S/ {v_pendiente_num}</div>
    </div>
    """, unsafe_allow_html=True)

    event_key = f"evt_{index_evento}_{v_fecha}_{v_cliente}"

    # 2 Botones Pequeños alineados horizontalmente
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("👤 Asignar Personal", key=f"btn_asig_{event_key}", use_container_width=True):
            abrir_dialogo_personal(event_key)
    with btn_col2:
        if st.button("📋 Ver Ficha", key=f"btn_fich_{event_key}", use_container_width=True):
            abrir_dialogo_ficha(row, event_key)

    st.write("") # Pequeña separación


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
                "Categoría:",
                ["Eventos del día (Hoy)", "Próximos 3 días", "Todos los eventos"],
                horizontal=True
            )

            df_copia["Fecha_Date"] = pd.to_datetime(df_copia["Fecha_Str"], format="%Y-%m-%d", errors="coerce").dt.date

            if modo_vista == "Eventos del día (Hoy)":
                df_hoy = df_copia[df_copia["Fecha_Date"] == hoy_date]

                if not df_hoy.empty:
                    for idx, row in df_hoy.iterrows():
                        renderizar_tarjeta(row, index_evento=idx, muestra_fecha=False)
                else:
                    st.info(f"No hay eventos para hoy ({hoy_date.strftime('%Y-%m-%d')}).")

            elif modo_vista == "Próximos 3 días":
                limite_3dias = hoy_date + timedelta(days=3)
                mask_3dias = (df_copia["Fecha_Date"] >= hoy_date) & (df_copia["Fecha_Date"] <= limite_3dias)
                df_3dias = df_copia[mask_3dias].sort_values("Fecha_Date")

                if not df_3dias.empty:
                    for idx, row in df_3dias.iterrows():
                        renderizar_tarjeta(row, index_evento=idx, muestra_fecha=True)
                else:
                    st.info("No hay eventos en los próximos 3 días.")

            else:
                df_todos = df_copia.sort_values("Fecha_Date", ascending=True, na_position="last")

                if not df_todos.empty:
                    for idx, row in df_todos.iterrows():
                        renderizar_tarjeta(row, index_evento=idx, muestra_fecha=True)
                else:
                    st.warning("No se encontraron registros.")
        else:
            st.info("No hay datos guardados en la base de datos.")

    # =========================================================
    # 2. MENÚ: FILTRO
    # =========================================================
    elif st.session_state["menu_activo"] == "Filtro":
        st.subheader("🔍 Búsqueda y Filtros")
        
        filtro_cliente = st.text_input("👤 Cliente / Nombre del Evento:", placeholder="Buscar cliente...")
        filtro_telefono = st.text_input("📱 Número de Teléfono:", placeholder="Buscar número...")
        rango_fechas = st.date_input("📅 Rango de Fechas:", value=())

        tiene_filtro_fechas = isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2
        filtro_activo = bool(filtro_cliente.strip() or filtro_telefono.strip() or tiene_filtro_fechas)

        if not filtro_activo:
            st.info("👉 Ingresa un nombre, número de teléfono o rango de fechas.")
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

            st.write(f"**Resultados:** {len(df_filtrado)}")
            st.dataframe(df_filtrado, use_container_width=True)

    # =========================================================
    # 3. MENÚ: NUEVO (FORMULARIO)
    # =========================================================
    elif st.session_state["menu_activo"] == "Nuevo":
        marca_seleccionada = st.radio("🏷️ Marca", ["Madai", "Risueña"], horizontal=True)

        fecha_input = st.date_input("📅 Fecha", datetime.now())
        fecha_str = fecha_input.strftime("%Y-%m-%d")

        tipo_servicio = st.selectbox("🎭 Servicio", ["Show", "Decoración", "Show + Decoración", "Alquiler"])

        nombre_evento = st.text_input("🎉 Evento", placeholder="ej. Cumpleaños Gia")

        cliente = st.text_input("👤 Cliente", placeholder="ej. María López")

        st.caption("⏰ **Hora Contrato**")
        c1, c2 = st.columns([3.5, 1.2])
        with c1:
            h_contrato_val = st.text_input("HC", value="04:30", key="hc_val", label_visibility="collapsed")
        with c2:
            ampm_contrato = st.selectbox("AP1", ["PM", "AM"], key="hc_ap", label_visibility="collapsed")
        hora_contrato_str = f"{h_contrato_val.strip()} {ampm_contrato}"

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
