import os
import requests
from datetime import datetime, timedelta
import pandas as pd

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_EXCEL = os.path.join(DIRECTORIO_ACTUAL, "agenda_eventos.xlsx")

def enviar_mensaje_telegram(texto):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Error: Faltan las variables TELEGRAM_TOKEN o TELEGRAM_CHAT_ID")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Notificación enviada con éxito a Telegram")
        else:
            print(f"❌ Error al enviar mensaje: {response.text}")
    except Exception as e:
        print(f"❌ Excepción al conectar con Telegram: {e}")

def procesar_y_notificar():
    if not os.path.exists(ARCHIVO_EXCEL):
        enviar_mensaje_telegram("🤖 *Prueba de Agenda Madai:* Notificación exitosa. (No se encontró el archivo Excel).")
        return

    try:
        df = pd.read_excel(ARCHIVO_EXCEL, dtype=str)
    except Exception as e:
        enviar_mensaje_telegram(f"❌ Error al leer el archivo Excel: {e}")
        return

    if df.empty:
        enviar_mensaje_telegram("🤖 *Prueba de Agenda Madai:* Conexión exitosa. Tu Excel no tiene eventos guardados por ahora.")
        return

    df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
    
    hora_utc = datetime.utcnow().hour
    hoy = datetime.now().date()
    
    if 1 <= hora_utc <= 6:
        fecha_objetivo = hoy + timedelta(days=1)
        titulo = "🌙 *RECORDATORIO: EVENTOS PARA MAÑANA*"
    else:
        fecha_objetivo = hoy
        titulo = "☀️ *HOY TIENES EVENTOS PROGRAMADOS*"

    eventos = df[df['Fecha_DT'] == fecha_objetivo]

    if eventos.empty:
        enviar_mensaje_telegram(f"🤖 *Prueba Agenda Madai:* Notificador activo. No hay eventos registrados para la fecha objetivo ({fecha_objetivo.strftime('%d/%m/%Y')}).")
        return

    mensaje = f"{titulo}\n\n"
    for _, fila in eventos.iterrows():
        costo_total = fila.get('Costo_Total', '0')
        adelanto = fila.get('Monto_Adelanto', '0')
        
        mensaje += f"🎉 *{fila['Evento']}*\n"
        mensaje += f"🏷️ *Tipo:* {fila['Tipo']}\n"
        mensaje += f"⏰ *Llegada:* {fila['Hora']} | *Invitación:* {fila['Hora_Invitacion']}\n"
        mensaje += f"📍 *Dirección:* {fila['Direccion']}\n"
        mensaje += f"💰 *Total:* S/ {costo_total} | *Adelanto:* S/ {adelanto} ({fila['Estado_Pago']})\n"
        mensaje += f"👤 *Cliente:* {fila['Cliente']} - 📱 {fila['Telefono']}\n"
        
        concepto_alq = str(fila.get('Concepto_Alquiler', '')).strip()
        if concepto_alq and concepto_alq not in ['N/A', 'No registrado']:
            mensaje += f"📦 *Alquiler:* {concepto_alq}\n"
            
        mensaje += "-----------------------------------\n"

    enviar_mensaje_telegram(mensaje)

if __name__ == "__main__":
    procesar_y_notificar()
