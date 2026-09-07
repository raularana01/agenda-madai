import streamlit as st
import pandas as pd
import requests
import datetime

# Configuración de la página
st.set_page_config(
    page_title="AGENDA VIRTUAL MADAI",
    page_icon="📅",
    layout="wide"
)

# 1. URL pública CSV de tu Google Sheet para LECTURA
# Remplaza este enlace por el enlace CSV público de tu Google Sheet
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT.../pub?output=csv"

# 2. URL de tu Google Apps Script para ESCRITURA
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyUBzRiK_5Eiuadgt-U2goi4KyaRo18pDAB727D6HpmPhjqPpCMNaty2Ah9moEZCeqI/exec"

# Función para cargar datos desde Google Sheets
@st.cache_data(ttl=5)
def cargar_datos():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if "Fecha" in df.columns:
            df["Fecha_DT"] = pd.to_datetime(df["Fecha"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Error al conectar con la hoja de Google Sheets: {e}")
        return pd.DataFrame()

# --- TÍTULO PRINCIPAL ---
st.title("📅 AGENDA VIRTUAL MADAI")

# Botón para refrescar datos
if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()

# Cargar los datos
df_eventos = cargar_datos()

# Crear las 3 Pestañas requeridas
tab1, tab2, tab3 = st.tabs([
    "📆 Eventos (Próximos 3 días)", 
    "📋 Lista Completa de Eventos", 
    "➕ Llenar Servicio"
])

# ==========================================
# TAB 1: EVENTOS PRÓXIMOS 3 DÍAS
# ==========================================
with tab1:
    st.subheader("Eventos Programados para los Próximos 3 Días")
    
    if not df_eventos.empty and "Fecha_DT" in df_eventos.columns:
        hoy = pd.to_datetime(datetime.date.today())
        limite_dias = hoy + pd.Timedelta(days=3)
        
        # Filtrar eventos entre hoy y los próximos 3 días
        filtro_3dias = (df_eventos["Fecha_DT"] >= hoy) & (df_eventos["Fecha_DT"] <= limite_dias)
        df_3dias = df_eventos[filtro_3dias].copy()
        
        if not df_3dias.empty:
            df_3dias_mostrar = df_3dias.drop(columns=["Fecha_DT"], errors="ignore")
            st.dataframe(df_3dias_mostrar, use_container_width=True)
        else:
            st.info("No hay eventos programados para los próximos 3 días.")
    else:
        st.info("Asegúrate de configurar la Variable SHEET_CSV_URL para cargar la lista.")

# ==========================================
# TAB 2: LISTA COMPLETA Y BÚSQUEDA
# ==========================================
with tab2:
    st.subheader("Búsqueda y Filtro de Eventos")
    
    busqueda_cliente = st.text_input(
        "🔍 Buscar por Teléfono o Cliente:",
        placeholder="Ingrese número de celular o nombre del cliente..."
    )

    if not df_eventos.empty:
        df_mostrar = df_eventos.drop(columns=["Fecha_DT"], errors="ignore")
        
        if busqueda_cliente:
            busqueda_str = str(busqueda_cliente).lower().strip()
            condicion_tel = df_mostrar["Telefono"].astype(str).str.lower().str.contains(busqueda_str, na=False)
            condicion_cli = df_mostrar["Cliente"].astype(str).str.lower().str.contains(busqueda_str, na=False)
            df_filtrado = df_mostrar[condicion_tel | condicion_cli]
        else:
            df_filtrado = df_mostrar

        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar. Revisa el enlace CSV.")

# ==========================================
# TAB 3: LLENAR SERVICIO
# ==========================================
with tab3:
    st.subheader("Registro de Nuevo Servicio")

    with st.form("form_registro_evento", clear_on_submit=True):
        col_fecha, col_tipo = st.columns(2)
        
        with col_fecha:
            fecha_evento = st.date_input("1. Fecha del Evento")

        with col_tipo:
            tipo_servicio = st.selectbox(
                "2. Tipo de Servicio",
                ["Show", "Decoración", "Show + Decoración", "Decoración + Alquiler"]
            )

        nombre_evento = st.text_input("Nombre del Evento", placeholder="ej. Cumpleaños de Gia")

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

        direccion = st.text_input("Dirección del Evento", placeholder="ej. La Florida")

        col_cli, col_tel = st.columns(2)
        with col_cli:
            cliente = st.text_input("Nombre del Cliente", placeholder="ej. Viviana Tuesta")
        with col_tel:
            telefono = st.text_input("Teléfono del Cliente", placeholder="ej. 900783201")

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            costo_total = st.number_input("Costo Total (S/)", min_value=0.0, step=10.0, value=0.0)
        with col_c2:
            monto_adelanto = st.number_input("Monto Adelanto (S/)", min_value=0.0, step=10.0, value=0.0)
        with col_c3:
            estado_pago = st.selectbox("Estado de Pago", ["Adelanto", "Pago completo", "Pendiente"])

        descripcion = st.text_area("Descripción", placeholder="Detalles adicionales...", value="Sin Descripción")
        desglose_costos = st.text_input("Desglose Costos", value="Show: S/ 0")
        concepto_alquiler = st.text_input("Concepto Alquiler", value="No registrado")

        submit_btn = st.form_submit_button("💾 Guardar Servicio", use_container_width=True)

        if submit_btn:
            hora_completa = f"{hora_input} {formato_ampm}".strip() if hora_input else "No registrado"
            hora_inv_completa = f"{hora_inv_input} {formato_inv_ampm}".strip() if hora_inv_input else "No registrado"

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

            try:
                response = requests.post(WEB_APP_URL, json=payload)
                if response.status_code == 200:
                    st.success("✅ ¡Evento guardado correctamente!")
                    st.cache_data.clear()
                else:
                    st.error(f"❌ Error al guardar. Código: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")
                
