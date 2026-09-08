import os
import requests
from datetime import datetime, timedelta
import pandas as pd

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GOOGLE_SHEET_URL = os.environ.get("GOOGLE_SHEET_URL")

def enviar_mensaje_telegram(texto):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Faltan credenciales de Telegram.")
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
            print("✅ Notificación enviada a Telegram.")
        else:
            print(f"❌ Error Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def procesar_y_notificar():
    if not GOOGLE_SHEET_URL:
        enviar_mensaje_telegram("❌ Error: No se ha configurado la variable GOOGLE_SHEET_URL en GitHub Secrets.")
        return

    try:
        df = pd.read_csv(GOOGLE_SHEET_URL, dtype=str)
    except Exception as e:
        enviar_mensaje_telegram(f"❌ Error al leer Google Sheets: {e}")
        return

    if df.empty:
        enviar_mensaje_telegram("ℹ️ La hoja de eventos en Google Sheets está vacía.")
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
        print(f"No hay eventos para la fecha: {fecha_objetivo}")
        return

    mensaje = f"{titulo}\n\n"
    for _, fila in eventos.iterrows():
        mensaje += f"🎉 *{fila.get('Evento', '')}*\n"
        mensaje += f"🏷️ *Tipo:* {fila.get('Tipo', '')}\n"
        mensaje += f"⏰ *Llegada:* {fila.get('Hora', '')} | *Invitación:* {fila.get('Hora_Invitacion', '')}\n"
        mensaje += f"📍 *Dirección:* {fila.get('Direccion', '')}\n"
        mensaje += f"💰 *Total:* S/ {fila.get('Costo_Total', '0')} | *Adelanto:* S/ {fila.get('Monto_Adelanto', '0')} ({fila.get('Estado_Pago', '')})\n"
        mensaje += f"👤 *Cliente:* {fila.get('Cliente', '')} - 📱 {fila.get('Telefono', '')}\n"
        mensaje += "-----------------------------------\n"

    enviar_mensaje_telegram(mensaje)

if __name__ == "__main__":
    procesar_y_notificar()
