import streamlit as st
import pandas as pd
import requests

# Configuración de la página
st.set_page_config(
    page_title="AGENDA VIRTUAL MADAI",
    page_icon="📅",
    layout="wide"
)

# URL de tu implementación de Google Apps Script
# Reemplaza esta URL con la tuya de Apps Script
WEB_APP_URL = "TU_URL_DE_GOOGLE_APPS_SCRIPT_AQUI"

# Función para cargar datos desde la hoja pública/JSON o CSV
@st.cache_data(ttl=5)
def cargar_datos():
    # Opción alternativa si publicas la hoja como CSV o lees directo por API
    # Reemplaza con tu URL CSV pública de Google Sheets si corresponde:
    # return pd.read_csv("TU_URL_CSV_DE_GOOGLE_SHEETS")
    return pd.DataFrame()

# --- TÍTULO PRINCIPAL ---
st.title("📅 AGENDA VIRTUAL MADAI")

# Botón para refrescar caché
if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()

# Crear Pestañas
tab1, tab2 = st.tabs(["📋 Lista de Eventos", "➕ Llenar Servicio"])

# ==========================================
# TAB 1: LISTA DE EVENTOS
# ==========================================
with tab1:
    st.subheader("Búsqueda y Filtro de Eventos")
    
    # Filtro exclusivo por teléfono o cliente
    busqueda_cliente = st.text_input(
        "🔍 Buscar por Teléfono o Cliente:",
        placeholder="Ingrese número de celular o nombre del cliente..."
    )

    # Cargar dataframe
    df = cargar_datos()

    if not df.empty:
        # Aplicar filtro solo por teléfono o cliente
        if busqueda_cliente:
            busqueda_str = str(busqueda_cliente).lower().strip()
            condicion_tel = df["Telefono"].astype(str).str.lower().str.contains(busqueda_str, na=False)
            condicion_cli = df["Cliente"].astype(str).str.lower().str.contains(busqueda_str, na=False)
            df_filtrado = df[condicion_tel | condicion_cli]
        else:
            df_filtrado = df

        # Mostrar tabla/tarjetas de resultados
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Ingresa la URL pública CSV o conecta la lectura para visualizar la lista de eventos.")

# ==========================================
# TAB 2: LLENAR SERVICIO
# ==========================================
with tab2:
    st.subheader("Registro de Nuevo Servicio")

    with st.form("form_registro_evento", clear_on_submit=True):
        # 1. Datos Generales
        col_fecha, col_tipo = st.columns(2)
        
        with col_fecha:
            fecha_evento = st.date_input("1. Fecha del Evento")

        with col_tipo:
            tipo_servicio = st.selectbox(
                "2. Tipo de Servicio",
                ["Show", "Decoración", "Show + Decoración", "Decoración + Alquiler"]
            )

        # Nombre del Evento (Sin espacios vacíos excesivos arriba)
        nombre_evento = st.text_input("Nombre del Evento", placeholder="ej. Cumpleaños de Gia")

        # Hora e Invitación (Selección AM/PM dentro del mismo grupo)
        col_h1, col_h2 = st.columns(2)

        with col_h1:
            st.write("**Hora Contrato / Inicio Show**")
            col_hora_val, col_hora_ampm = st.columns([3, 1.5])
            with col_hora_val:
                hora_input = st.text_input("Hora", placeholder="ej. 04:00", label_visibility="collapsed")
            with col_hora_ampm:
                formato_ampm = st.selectbox("", ["AM", "PM"], key="ampm_show", label_visibility="collapsed")

        with col_h2:
            st.write("**Hora Invitación**")
            col_inv_val, col_inv_ampm = st.columns([3, 1.5])
            with col_inv_val:
                hora_inv_input = st.text_input("Hora Inv", placeholder="ej. 03:30", label_visibility="collapsed")
            with col_inv_ampm:
                formato_inv_ampm = st.selectbox("", ["AM", "PM"], key="ampm_inv", label_visibility="collapsed")

        # Dirección y Datos de Cliente
        direccion = st.text_input("Dirección del Evento", placeholder="ej. La Florida")

        col_cli, col_tel = st.columns(2)
        with col_cli:
            cliente = st.text_input("Nombre del Cliente", placeholder="ej. Viviana Tuesta")
        with col_tel:
            telefono = st.text_input("Teléfono del Cliente", placeholder="ej. 900783201")

        # Costos y Pagos (Sin título "Costo en soles")
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            costo_total = st.number_input("Costo Total (S/)", min_value=0.0, step=10.0, value=0.0)
        with col_c2:
            monto_adelanto = st.number_input("Monto Adelanto (S/)", min_value=0.0, step=10.0, value=0.0)
        with col_c3:
            estado_pago = st.selectbox("Estado de Pago", ["Adelanto", "Pago completo", "Pendiente"])

        # Detalle adicional
        descripcion = st.text_area("Descripción", placeholder="Detalles o anotaciones adicionales...", value="Sin Descripción")
        desglose_costos = st.text_input("Desglose Costos", value="Show: S/ 0")
        concepto_alquiler = st.text_input("Concepto Alquiler", value="No registrado")

        # Botón para enviar datos
        submit_btn = st.form_submit_button("💾 Guardar Servicio", use_container_width=True)

        if submit_btn:
            # Armar los valores compuestos de hora
            hora_completa = f"{hora_input} {formato_ampm}".strip() if hora_input else "No registrado"
            hora_inv_completa = f"{hora_inv_input} {formato_inv_ampm}".strip() if hora_inv_input else "No registrado"

            # Crear diccionario con los datos
            payload = {
                "Fecha": str(fecha_evento),
                "Tipo": tipo_servicio,
                "Evento": nombre_evento if nombre_evento else "Sin Nombre",
                "Hora": hora_completa,
                "Direccion": direccion if direccion else "No registrado",
                "Hora_Invitacion": hora_inv_completa,
                "Cliente": cliente if cliente else "No registrado",
                "Telefono": telefono if telefono else "No registrado",
                "Costo_Total": str(costo_total),
                "Monto_Adelanto": str(monto_adelanto),
                "Estado_Pago": estado_pago,
                "Descripcion": descripcion,
                "Desglose_Costos": desglose_costos,
                "Concepto_Alquiler": concepto_alquiler
            }

            # Enviar petición POST a Google Apps Script
            try:
                response = requests.post(WEB_APP_URL, json=payload)
                if response.status_code == 200:
                    st.success("✅ ¡Evento guardado correctamente en tu tabla principal!")
                    st.cache_data.clear()
                else:
                    st.error(f"❌ Error al guardar. Código: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Ocurrió un error al conectar con Google Sheets: {e}")
                
