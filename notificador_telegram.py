import os
import requests
from datetime import datetime, timedelta
import pandas as pd

# ⚠️ REEMPLAZA AQUÍ TUS DATOS OBTENIDOS DE TELEGRAM:
TELEGRAM_TOKEN = os.environ.get("8841819382:AAGbMGI0ZB08-0iQLPrZP-jBJqAdaKqnXQ4")
TELEGRAM_CHAT_ID = os.environ.get("8978445198")

DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_EXCEL = os.path.join(DIRECTORIO_ACTUAL, "agenda_eventos.xlsx")

def enviar_mensaje_telegram(texto):
    """Envía un mensaje a tu chat de Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ ¡Mensaje de prueba enviado con éxito a tu Telegram!")
        else:
            print(f"❌ Error de Telegram: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def procesar_y_notificar():
    if not os.path.exists(ARCHIVO_EXCEL):
        print("⚠️ No se encontró el archivo agenda_eventos.xlsx")
        return

    try:
        df = pd.read_excel(ARCHIVO_EXCEL, dtype=str)
    except Exception as e:
        print(f"❌ Error al leer Excel: {e}")
        return

    if df.empty:
        print("ℹ️ El Excel está vacío.")
        return

    df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date

    # Evaluamos eventos para HOY o MAÑANA
    hoy = datetime.now().date()

    # Para probar de noche/mañana (Revisa eventos de HOY primeramente)
    eventos = df[df['Fecha_DT'] == hoy]
    titulo = "☀️ *EVENTOS PROGRAMADOS PARA HOY*"

    if eventos.empty:
        # Si no hay hoy, busca si hay eventos mañana
        manana = hoy + timedelta(days=1)
        eventos = df[df['Fecha_DT'] == manana]
        titulo = "🌙 *RECORDATORIO: EVENTOS PARA MAÑANA*"

    if eventos.empty:
        print("ℹ️ No hay eventos agendados para hoy ni para mañana. Enviando mensaje de prueba estándar...")
        enviar_mensaje_telegram("🤖 *Prueba de conexión exitosa:* El bot de Telegram de la Agenda Madai está funcionando correctamente.")
        return

    # Formatear el mensaje
    mensaje = f"{titulo}\n\n"
    for _, fila in eventos.iterrows():
        mensaje += f"🎉 *{fila['Evento']}*\n"
        mensaje += f"🏷️ *Tipo:* {fila['Tipo']}\n"
        mensaje += f"⏰ *Llegada:* {fila['Hora']} | *Invitación:* {fila['Hora_Invitacion']}\n"
        mensaje += f"📍 *Dirección:* {fila['Direccion']}\n"
        mensaje += f"💰 *Total:* S/ {fila['Costo_Total']} | *Adelanto:* S/ {fila['Monto_Adelanto']} ({fila['Estado_Pago']})\n"
        mensaje += f"👤 *Cliente:* {fila['Cliente']} - 📱 {fila['Telefono']}\n"
        mensaje += "-----------------------------------\n"

    enviar_mensaje_telegram(mensaje)

if __name__ == "__main__":
    procesar_y_notificar()