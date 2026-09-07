import os
import base64
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# =========================================================================
# 1. CONFIGURACIÓN DE PÁGINA
# =========================================================================
st.set_page_config(
    page_title="AGENDA VIRTUAL MADAI", 
    page_icon="🎈", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Directorio del archivo script actual
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_EXCEL = os.path.join(DIRECTORIO_ACTUAL, "agenda_eventos.xlsx")

# Detección de fondo con ruta absoluta y múltiples extensiones
NOMBRES_FONDO = ["fondo.png", "fondo.jpg", "fondo.jpeg", "fondo.PNG", "fondo.JPG", "fondo.JPEG"]
PATH_FONDO = None

for nombre in NOMBRES_FONDO:
    ruta_posible = os.path.join(DIRECTORIO_ACTUAL, nombre)
    if os.path.exists(ruta_posible):
        PATH_FONDO = ruta_posible
        break

# Función para convertir imagen local a base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Configuración dinámica del CSS del fondo
if PATH_FONDO:
    encoded_bg = get_base64_of_bin_file(PATH_FONDO)
    ext = PATH_FONDO.split('.')[-1].lower()
    mime = "image/png" if ext in ["png", "PNG"] else "image/jpeg"
    
    bg_css_code = f"""
        background-image: linear-gradient(rgba(240, 230, 255, 0.82), rgba(240, 230, 255, 0.82)), url("data:{mime};base64,{encoded_bg}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    """
else:
    bg_css_code = "background: linear-gradient(135deg, #E1BEE7 0%, #FFF59D 50%, #80DEEA 100%);"

# =========================================================================
# 2. ESTILOS CSS - PALETA EL SHOW DE MADAI
# =========================================================================
st.markdown(f"""
    <style>
    /* Fondo global con overlay de contraste */
    .stApp {{
        {bg_css_code}
        font-family: 'Comic Sans MS', 'Chalkboard SE', 'Arial', sans-serif;
    }}
    
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 0.4rem !important;
        padding-right: 0.4rem !important;
    }}

    /* LOGO Y ENCABEZADO */
    [data-testid="stColumn"] img {{
        max-width: 65px !important;
        height: auto !important;
        margin: 0 auto;
        display: block;
    }}
    
    .header-title {{
        font-size: 1.25rem !important;
        font-weight: 800;
        color: #6A1B9A;
        line-height: 1.2 !important;
        margin: 0 !important;
        padding: 0 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }}
    
    /* DISPOSICIÓN FLEXIBLE EN MÓVIL */
    [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
        align-items: center !important;
        width: 100% !important;
    }}

    [data-testid="stHorizontalBlock"] > div {{
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }}

    /* BOTONES DE ACCIÓN */
    div[data-testid="column"] button {{
        width: 100% !important;
        background: linear-gradient(180deg, #FF4081 0%, #D81B60 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        border: 2px solid #AD1457 !important;
        padding: 6px 2px !important;
        font-weight: bold !important;
        font-size: 0.82rem !important;
        box-shadow: 0px 3px 0px #880E4F !important;
        transition: all 0.1s ease-in-out !important;
        white-space: nowrap !important;
    }}
    
    div[data-testid="column"] button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0px 4px 0px #880E4F !important;
        background: linear-gradient(180deg, #FF80AB 0%, #FF4081 100%) !important;
    }}
    
    div[data-testid="column"] button:active {{
        transform: translateY(2px) !important;
        box-shadow: 0px 1px 0px #880E4F !important;
    }}

    div[data-testid="stToggle"] label p {{
        font-size: 0.8rem !important;
        white-space: nowrap !important;
        font-weight: bold;
        color: #4A148C;
    }}

    /* TARJETAS DE EVENTOS */
    .card-evento {{
        background-color: rgba(255, 255, 255, 0.93);
        padding: 14px;
        border-radius: 20px;
        margin-bottom: 8px;
        border: 3px solid #AB47BC;
        box-shadow: 0 6px 12px rgba(106, 27, 154, 0.12);
    }}
    
    /* ETIQUETAS */
    .tag {{
        padding: 4px 10px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
        color: white;
    }}
    .tag-show {{ background-color: #00B0FF; }}
    .tag-decoracion {{ background-color: #E91E63; }}
    .tag-alquiler {{ background-color: #FFC107; color: #3E2723; }}
    .tag-combo {{ background-color: #9C27B0; }}
    </style>
""", unsafe_allow_html=True)

# Opción para subir imagen si no se encuentra en la carpeta
if not PATH_FONDO:
    with st.expander("🖼️ Configurar Fondo de Pantalla"):
        uploaded_bg = st.file_uploader("Subir imagen de fondo", type=["png", "jpg", "jpeg"], key="bg_up")
        if uploaded_bg is not None:
            ext = uploaded_bg.name.split(".")[-1].lower()
            ruta_guardado = os.path.join(DIRECTORIO_ACTUAL, f"fondo.{ext}")
            with open(ruta_guardado, "wb") as f:
                f.write(uploaded_bg.getbuffer())
            st.rerun()

# =========================================================================
# 3. ENCABEZADO Y LOGO
# =========================================================================
col_logo1, col_logo2 = st.columns([1, 4], vertical_alignment="center")

NOMBRES_LOGO = ["logo.png", "logo.jpg", "logo.jpeg", "logo.PNG", "logo.JPG"]
PATH_LOGO = None
for n_logo in NOMBRES_LOGO:
    r_logo = os.path.join(DIRECTORIO_ACTUAL, n_logo)
    if os.path.exists(r_logo):
        PATH_LOGO = r_logo
        break

with col_logo1:
    if PATH_LOGO:
        st.image(PATH_LOGO, use_container_width=True)
    else:
        uploaded_logo = st.file_uploader(
            "Subir Logo", 
            type=["png", "jpg", "jpeg"], 
            label_visibility="collapsed"
        )
        if uploaded_logo is not None:
            ext = uploaded_logo.name.split(".")[-1].lower()
            ruta_logo_save = os.path.join(DIRECTORIO_ACTUAL, f"logo.{ext}")
            with open(ruta_logo_save, "wb") as f:
                f.write(uploaded_logo.getbuffer())
            st.rerun()

with col_logo2:
    st.markdown("<p class='header-title'>🎪 AGENDA VIRTUAL MADAI</p>", unsafe_allow_html=True)
    st.caption("Gestión integral de eventos y servicios")

st.markdown("<hr style='margin: 8px 0 12px 0; border-color: #CE93D8;'>", unsafe_allow_html=True)

# =========================================================================
# 4. EXCEL Y DATOS
# =========================================================================
columnas_totales = [
    "Fecha", "Tipo", "Evento", "Hora", "Direccion", "Hora_Invitacion", 
    "Cliente", "Telefono", "Costo_Total", "Monto_Adelanto", "Estado_Pago", 
    "Descripcion", "Desglose_Costos", "Concepto_Alquiler"
]

def cargar_datos():
    if os.path.exists(ARCHIVO_EXCEL):
        try:
            df = pd.read_excel(ARCHIVO_EXCEL, dtype=str)
            df = df.dropna(subset=["Evento", "Fecha"], how="all")
            for col in columnas_totales:
                if col not in df.columns:
                    df[col] = "No registrado"
                else:
                    df[col] = df[col].fillna("No registrado").astype(str)
            return df
        except Exception:
            return pd.DataFrame(columns=columnas_totales)
    else:
        df = pd.DataFrame(columns=columnas_totales)
        df.to_excel(ARCHIVO_EXCEL, index=False)
        return df

def guardar_datos(df):
    try:
        df.to_excel(ARCHIVO_EXCEL, index=False)
        return True
    except PermissionError:
        st.error("⚠️ Cierra el archivo 'agenda_eventos.xlsx' en Excel e intenta nuevamente.")
        return False

def a_entero_string(val):
    """Convierte un valor de costo a texto en entero sin decimales."""
    try:
        return str(int(float(val)))
    except (ValueError, TypeError):
        return "0"

df_existente = cargar_datos()

# =========================================================================
# 5. DIÁLOGOS Y TARJETAS
# =========================================================================
@st.dialog("✏️ Editar Evento", width="large")
def mostrar_modal_editar(idx_registro, fila_data):
    st.subheader(f"Modificar: {fila_data['Evento']}")
    
    with st.form(f"form_editar_{idx_registro}"):
        e_titulo = st.text_input("1. Nombre / Motivo del evento", value=str(fila_data['Evento']))
        
        try:
            f_val = datetime.strptime(str(fila_data['Fecha']), "%Y-%m-%d").date()
        except Exception:
            f_val = datetime.now().date()
        e_fecha = st.date_input("2. Fecha del evento", value=f_val)
        
        col1, col2 = st.columns(2)
        with col1:
            e_hora_llegada = st.text_input("Tu hora / llegada", value=str(fila_data['Hora']))
        with col2:
            e_hora_invitacion = st.text_input("Hora invitación", value=str(fila_data['Hora_Invitacion']))
            
        e_direccion = st.text_input("4. Dirección exacta", value=str(fila_data['Direccion']))
        e_cliente = st.text_input("5. Nombre del cliente", value=str(fila_data['Cliente']))
        e_telefono = st.text_input("6. Celular del cliente", value=str(fila_data['Telefono']))
        
        e_tipo = st.selectbox(
            "7. Tipo de servicio", 
            ["Show", "Decoración", "Alquiler", "Show + Decoración", "Show + Alquiler", "Decoración + Alquiler", "Show + Decoración + Alquiler"],
            index=0
        )
        
        val_costo_tot = int(float(fila_data['Costo_Total'])) if fila_data['Costo_Total'].replace('.','',1).isdigit() else 0
        val_monto_adel = int(float(fila_data['Monto_Adelanto'])) if fila_data['Monto_Adelanto'].replace('.','',1).isdigit() else 0
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            e_costo_total = st.number_input("Costo Total (S/)", value=val_costo_tot, step=1)
        with col_p2:
            e_monto_adelanto = st.number_input("Monto Adelanto (S/)", value=val_monto_adel, step=1)
            
        e_estado_pago = st.radio("Estado del pago", ["Pendiente", "Adelanto parcial", "Pago completo"], horizontal=True)
        e_concepto_alq = st.text_input("Concepto de alquiler", value=str(fila_data.get('Concepto_Alquiler', 'N/A')))
        e_descripcion = st.text_area("Descripción", value=str(fila_data['Descripcion']))
        
        btn_actualizar = st.form_submit_button("💾 Guardar Cambios")
        
        if btn_actualizar:
            df_actual = cargar_datos()
            if idx_registro in df_actual.index:
                df_actual.at[idx_registro, 'Evento'] = e_titulo
                df_actual.at[idx_registro, 'Fecha'] = str(e_fecha)
                df_actual.at[idx_registro, 'Hora'] = e_hora_llegada
                df_actual.at[idx_registro, 'Hora_Invitacion'] = e_hora_invitacion
                df_actual.at[idx_registro, 'Direccion'] = e_direccion
                df_actual.at[idx_registro, 'Cliente'] = e_cliente
                df_actual.at[idx_registro, 'Telefono'] = e_telefono
                df_actual.at[idx_registro, 'Tipo'] = e_tipo
                df_actual.at[idx_registro, 'Costo_Total'] = str(int(e_costo_total))
                df_actual.at[idx_registro, 'Monto_Adelanto'] = str(int(e_monto_adelanto))
                df_actual.at[idx_registro, 'Estado_Pago'] = e_estado_pago
                df_actual.at[idx_registro, 'Concepto_Alquiler'] = e_concepto_alq
                df_actual.at[idx_registro, 'Descripcion'] = e_descripcion
                
                if guardar_datos(df_actual):
                    st.success("¡Evento actualizado correctamente!")
                    st.rerun()

def renderizar_tarjeta_con_acciones(idx, fila):
    val_fecha = str(fila['Fecha']).strip()
    try:
        fecha_dt = datetime.strptime(val_fecha, "%Y-%m-%d")
        fecha_formateada = fecha_dt.strftime("%d/%m/%Y")
    except Exception:
        fecha_formateada = val_fecha
    
    tipo_val = str(fila['Tipo']).strip()
    clase_tag = "tag-show"
    if tipo_val == "Decoración":
        clase_tag = "tag-decoracion"
    elif tipo_val == "Alquiler":
        clase_tag = "tag-alquiler"
    elif "Show" in tipo_val and "Decoración" in tipo_val:
        clase_tag = "tag-combo"
        
    estado_val = str(fila['Estado_Pago'])
    color_estado = "#D81B60"
    if estado_val == "Pago completo":
        color_estado = "#00C853"
    elif estado_val == "Adelanto parcial":
        color_estado = "#FF9100"
        
    html_desglose = ""
    desglose_val = str(fila.get('Desglose_Costos', ''))
    if desglose_val and desglose_val not in ["N/A", "No registrado"]:
        html_desglose = f"<p style='margin: 0; color: #8E24AA; font-size: 0.8rem;'>📊 <b>Desglose:</b> {desglose_val}</p>"

    concepto_alq = str(fila.get('Concepto_Alquiler', '')).strip()
    html_concepto = ""
    if concepto_alq and concepto_alq not in ["N/A", "No registrado"]:
        html_concepto = f"<p style='margin: 2px 0; color: #D81B60; font-size: 0.8rem;'>📦 <b>Alquiler de:</b> {concepto_alq}</p>"

    costo_tot_int = a_entero_string(fila['Costo_Total'])
    monto_adel_int = a_entero_string(fila['Monto_Adelanto'])

    html_card = f"""<div class="card-evento">
<div class="tag {clase_tag}">{tipo_val}</div>
<span style="color: #6A1B9A; font-size: 0.8rem; float: right; font-weight: bold;">📅 {fecha_formateada}</span>
<h3 style="margin: 2px 0 8px 0; color: #4A148C; font-size: 1.1rem;">🎉 {fila['Evento']}</h3>
<p style="margin: 0 0 4px 0; color: #212121; font-size: 0.85rem;">⏰ <b>Tu hora:</b> {fila['Hora']} | ✉️ <b>Invitación:</b> {fila['Hora_Invitacion']}</p>
<p style="margin: 0 0 8px 0; color: #424242; font-size: 0.8rem;">📍 <b>Dirección:</b> {fila['Direccion']}</p>
<div style="background-color: #F3E5F5; padding: 8px; border-radius: 10px; margin-bottom: 8px; border-left: 4px solid {color_estado};">
<p style="margin: 0; color: #212121; font-size: 0.85rem;">💰 <b>Total:</b> S/ {costo_tot_int} — 💸 <b>Adelanto:</b> S/ {monto_adel_int}</p>
<p style="margin: 2px 0 0 0; color: {color_estado}; font-size: 0.8rem; font-weight: bold;">📌 Estado: {estado_val}</p>
{html_desglose}
</div>
<div style="background-color: #FFFDE7; padding: 8px; border-radius: 10px; border: 1px solid #FFF59D;">
<span style="color: #AB47BC; font-size: 0.7rem; font-weight: bold; text-transform: uppercase;">DETALLES:</span>
<p style="margin: 2px 0; color: #212121; font-size: 0.8rem;">{fila['Descripcion']}</p>
{html_concepto}
<p style="margin: 0; color: #212121; font-size: 0.8rem;">👤 <b>Cliente:</b> {fila['Cliente']}<br>📱 <b>Cel:</b> {fila['Telefono']}</p>
</div>
</div>"""
    
    st.markdown(html_card, unsafe_allow_html=True)
    
    col_edit, col_del = st.columns(2)
    with col_edit:
        if st.button("✏️ Editar", key=f"btn_edit_{idx}"):
            mostrar_modal_editar(idx, fila)
    with col_del:
        if st.button("🗑️ Eliminar", key=f"btn_del_{idx}"):
            df_borrar = cargar_datos()
            if idx in df_borrar.index:
                df_borrar = df_borrar.drop(idx)
                if guardar_datos(df_borrar):
                    st.toast("🗑️ Evento eliminado con éxito")
                    st.rerun()

@st.dialog("🔍 Resultados de la Búsqueda", width="large")
def mostrar_modal_resultados(df_filtrado):
    st.caption(f"Se encontraron **{len(df_filtrado)}** evento(s) que coinciden con los criterios.")
    st.markdown("---")
    
    if not df_filtrado.empty:
        for idx, fila in df_filtrado.iterrows():
            renderizar_tarjeta_con_acciones(idx, fila)
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No se encontraron eventos con los filtros seleccionados.")
        
    st.markdown("---")
    if st.button("❌ Cerrar y volver"):
        st.rerun()

# =========================================================================
# 6. PESTAÑAS Y NAVEGACIÓN
# =========================================================================
tab_opciones = ["📅 Agenda del Día", "🔍 Buscar", "📝 Nuevo Servicio"]

if "tab_activa" not in st.session_state:
    st.session_state["tab_activa"] = "📅 Agenda del Día"

# Determinamos la posición por defecto para evitar errores de reinstanciación
idx_default = tab_opciones.index(st.session_state["tab_activa"]) if st.session_state["tab_activa"] in tab_opciones else 0

pestana_activa = st.radio(
    "Navegación", 
    tab_opciones, 
    index=idx_default,
    horizontal=True, 
    label_visibility="collapsed"
)

# PESTAÑA 1: AGENDA DEL DÍA
if pestana_activa == "📅 Agenda del Día":
    st.session_state["tab_activa"] = "📅 Agenda del Día"
    hoy = datetime.now().date()
    
    col_a1, col_a2 = st.columns([1.1, 1.9], vertical_alignment="center")
    with col_a1:
        st.subheader("📅 Eventos")
    with col_a2:
        ver_3_dias = st.toggle("Próximos 3 días", value=False)

    if not df_existente.empty:
        df_temp = df_existente.copy()
        df_temp['Fecha_DT'] = pd.to_datetime(df_temp['Fecha'], errors='coerce').dt.date
        
        if ver_3_dias:
            limite_dias = hoy + timedelta(days=3)
            df_filtrado = df_temp[(df_temp['Fecha_DT'] >= hoy) & (df_temp['Fecha_DT'] <= limite_dias)]
            st.info(f"Mostrando agenda hasta el {limite_dias.strftime('%d/%m/%Y')}")
        else:
            df_filtrado = df_temp[df_temp['Fecha_DT'] == hoy]

        if not df_filtrado.empty:
            df_ordenado = df_filtrado.sort_values(by=["Fecha", "Hora"])
            for idx, fila in df_ordenado.iterrows():
                renderizar_tarjeta_con_acciones(idx, fila)
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            if ver_3_dias:
                st.success("🎉 ¡No hay eventos agendados para los próximos 3 días!")
            else:
                st.success("🎉 ¡Hoy no tienes eventos agendados! Disfruta tu día.")
    else:
        st.info("No tienes ningún servicio agendado aún.")

# PESTAÑA 2: BUSCAR
elif pestana_activa == "🔍 Buscar":
    st.session_state["tab_activa"] = "🔍 Buscar"
    st.subheader("🔎 Filtros de Búsqueda")
    with st.container(border=True):
        busqueda_texto = st.text_input("Buscar por Nombre de Evento o Cliente", placeholder="Ej. Juana, Cumpleaños...")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_tipo = st.multiselect("Tipo de servicio", ["Show", "Decoración", "Alquiler", "Show + Decoración"])
        with col_f2:
            filtro_estado = st.multiselect("Estado de Pago", ["Pendiente", "Adelanto parcial", "Pago completo"])
            
        usar_filtro_fecha = st.checkbox("Filtrar por rango de fechas")
        if usar_filtro_fecha:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                fecha_inicio = st.date_input("Desde", datetime.now())
            with col_d2:
                fecha_fin = st.date_input("Hasta", datetime.now())
                
        boton_buscar = st.button("🔍 Aplicar Filtros")
        
        if boton_buscar:
            df_resultados = df_existente.copy()
            if busqueda_texto.strip():
                query = busqueda_texto.strip().lower()
                df_resultados = df_resultados[
                    df_resultados['Evento'].astype(str).str.lower().str.contains(query) |
                    df_resultados['Cliente'].astype(str).str.lower().str.contains(query)
                ]
            if filtro_tipo:
                df_resultados = df_resultados[df_resultados['Tipo'].isin(filtro_tipo)]
            if filtro_estado:
                df_resultados = df_resultados[df_resultados['Estado_Pago'].isin(filtro_estado)]
            if usar_filtro_fecha:
                try:
                    df_resultados['Fecha_DT'] = pd.to_datetime(df_resultados['Fecha'], errors='coerce')
                    f_i = pd.to_datetime(fecha_inicio)
                    f_f = pd.to_datetime(fecha_fin)
                    df_resultados = df_resultados[(df_resultados['Fecha_DT'] >= f_i) & (df_resultados['Fecha_DT'] <= f_f)]
                except Exception:
                    pass
            
            mostrar_modal_resultados(df_resultados)

# PESTAÑA 3: NUEVO SERVICIO
elif pestana_activa == "📝 Nuevo Servicio":
    st.session_state["tab_activa"] = "📝 Nuevo Servicio"
    st.subheader("📝 Registrar Nuevo Servicio")
    
    titulo_evento = st.text_input("1. Nombre / Motivo del evento", placeholder="Ej. Cumpleaños de Juana")
    fecha = st.date_input("2. Fecha del evento", datetime.now())
    
    st.markdown("**3. Horarios del Evento**")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        hora_inicio_val = st.time_input("Tu hora / llegada")
    with col_t2:
        hora_invitacion_val = st.time_input("Hora invitación")
        
    direccion_evento = st.text_input("4. Dirección exacta", placeholder="Calle, Número, Ciudad")
    nombre_cliente = st.text_input("5. Nombre completo del cliente")
    telefono_cliente = st.text_input("6. Celular del cliente", placeholder="Ej. 987654321")
    
    tipo_servicio = st.selectbox("7. Tipo de servicio principal", ["Show", "Decoración", "Alquiler", "Show + Decoración"])
    
    incluir_alquiler = False
    if tipo_servicio != "Alquiler":
        incluir_alquiler = st.checkbox("➕ ¿Deseas agregar Alquiler adicional a este servicio?")
        
    st.markdown("---")
    st.markdown("**💰 Control de Precios y Pagos (Nuevos Soles)**")
    
    costo_show = 0
    costo_deco = 0
    costo_alquiler = 0
    costo_general = 0
    concepto_alquiler = ""
    
    if tipo_servicio == "Show":
        costo_show = st.number_input("Costo Show (S/)", min_value=0, step=10, value=0)
    elif tipo_servicio == "Decoración":
        costo_deco = st.number_input("Costo Decoración (S/)", min_value=0, step=10, value=0)
    elif tipo_servicio == "Alquiler":
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            concepto_alquiler = st.text_input("Concepto de alquiler", placeholder="Ej. Mesas, Sillas, Inflable")
        with col_a2:
            costo_alquiler = st.number_input("Costo Alquiler (S/)", min_value=0, step=10, value=0)
    elif tipo_servicio == "Show + Decoración":
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            costo_show = st.number_input("Costo Show (S/)", min_value=0, step=10, value=0)
        with col_p2:
            costo_deco = st.number_input("Costo Decoración (S/)", min_value=0, step=10, value=0)

    if incluir_alquiler and tipo_servicio != "Alquiler":
        col_add1, col_add2 = st.columns(2)
        with col_add1:
            concepto_alquiler = st.text_input("Concepto de alquiler adicional", placeholder="Ej. Luces, Sillas, Equipo audio")
        with col_add2:
            costo_alquiler = st.number_input("Costo Adicional de Alquiler (S/)", min_value=0, step=10, value=0)
        
    costo_total_calculado = int(costo_show + costo_deco + costo_alquiler + costo_general)
    st.info(f"💵 **Total Calculado:** S/ {costo_total_calculado}")

    estado_pago = st.radio("Estado del pago", ["Pendiente", "Adelanto parcial", "Pago completo"], horizontal=True)
    
    monto_adelanto = 0
    if estado_pago == "Adelanto parcial":
        monto_adelanto = st.number_input("Monto de adelanto (S/)", min_value=0, max_value=costo_total_calculado if costo_total_calculado > 0 else 999999, step=10, value=0)
    elif estado_pago == "Pago completo":
        monto_adelanto = costo_total_calculado
    else:
        monto_adelanto = 0

    st.markdown("---")
    descripcion_evento = st.text_area("8. Descripción del servicio", placeholder="Detalles acordados con el cliente...")
    
    if st.button("✨ Registrar Servicio"):
        if not titulo_evento.strip():
            st.error("Por favor, ingresa el nombre o motivo del evento.")
        else:
            desglose_partes = []
            if costo_show > 0: desglose_partes.append(f"Show: S/ {costo_show}")
            if costo_deco > 0: desglose_partes.append(f"Deco: S/ {costo_deco}")
            if costo_alquiler > 0: 
                texto_alq = f"Alquiler: S/ {costo_alquiler}"
                if concepto_alquiler.strip():
                    texto_alq += f" ({concepto_alquiler.strip()})"
                desglose_partes.append(texto_alq)
            
            desglose_texto = " | ".join(desglose_partes) if desglose_partes else "N/A"
            
            tipo_final = tipo_servicio
            if incluir_alquiler and tipo_servicio != "Alquiler":
                tipo_final += " + Alquiler"

            str_hora_inicio = hora_inicio_val.strftime("%I:%M %p")
            str_hora_invitacion = hora_invitacion_val.strftime("%I:%M %p")
            
            nuevo_evento = pd.DataFrame([{
                "Fecha": str(fecha),
                "Tipo": tipo_final,
                "Evento": titulo_evento,
                "Hora": str_hora_inicio,
                "Direccion": direccion_evento if direccion_evento else "No registrada",
                "Hora_Invitacion": str_hora_invitacion,
                "Cliente": nombre_cliente if nombre_cliente else "No registrado",
                "Telefono": telefono_cliente if telefono_cliente else "No registrado",
                "Costo_Total": str(int(costo_total_calculado)),
                "Monto_Adelanto": str(int(monto_adelanto)),
                "Estado_Pago": estado_pago,
                "Descripcion": descripcion_evento if descripcion_evento else "Sin descripción",
                "Desglose_Costos": desglose_texto,
                "Concepto_Alquiler": concepto_alquiler if concepto_alquiler.strip() else "N/A"
            }])
            
            df_actualizado = pd.concat([df_existente, nuevo_evento], ignore_index=True)
            
            if guardar_datos(df_actualizado):
                st.session_state["tab_activa"] = "📅 Agenda del Día"
                st.rerun()