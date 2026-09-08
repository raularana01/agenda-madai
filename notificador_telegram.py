import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuración de credenciales desde las variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# URL CSV pública o de exportación de tu Google Sheet / Base de datos
# (Asegúrate de colocar la URL de tu Hoja de Cálculo o la fuente de datos que usas)
SHEET_URL = os.getenv("SHEET_URL", "https://docs.google.com/spreadsheets/d/TU_SHEET_ID/export?format=csv")

def enviar_mensaje(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: No se configuraron las variables TELEGRAM_TOKEN o TELEGRAM_CHAT_ID.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("Notificación enviada correctamente a Telegram.")
    else:
        print(f"Error enviando mensaje a Telegram: {res.text}")

def main():
    # Obtener hora actual en Perú (UTC-5)
    ahora_utc = datetime.utcnow()
    ahora_peru = ahora_utc - timedelta(hours=5)
    
    # Determinar qué fecha consultar según la hora de ejecución
    # Si se ejecuta de 18:00 a 23:59 (7:00 PM), busca eventos de MAÑANA
    if ahora_peru.hour >= 18:
        fecha_objetivo_dt = ahora_peru + timedelta(days=1)
        tipo_notificacion = "RECORDATORIO PARA MAÑANA"
    else:
        # En caso contrario (por ejemplo, a las 7:00 AM o prueba manual), busca eventos de HOY
        fecha_objetivo_dt = ahora_peru
        tipo_notificacion = "EVENTOS DE HOY"

    # Formatos de fecha en texto
    fecha_iso = fecha_objetivo_dt.strftime("%Y-%m-%d")        # Ejemplo: 2026-09-08
    fecha_latam = fecha_objetivo_dt.strftime("%d/%m/%Y")      # Ejemplo: 08/09/2026
    fecha_corta = f"{fecha_objetivo_dt.day}/{fecha_objetivo_dt.month}/{fecha_objetivo_dt.year}" # 8/9/2026

    print(f"Buscando eventos para la fecha: {fecha_iso} / {fecha_latam}")

    try:
        df = pd.read_csv(SHEET_URL)
    except Exception as e:
        print(f"Error leyendo los datos de la hoja: {e}")
        return

    if df.empty or "Fecha" not in df.columns:
        enviar_mensaje("🤖 <b>Prueba Agenda Madai:</b> No se pudieron cargar los datos o no existe la columna 'Fecha'.")
        return

    # Limpieza de fechas y normalización
    df["Fecha_Str"] = df["Fecha"].astype(str).str.strip()
    
    # Filtrar registros que coincidan con cualquier formato de la fecha objetivo
    eventos = df[
        (df["Fecha_Str"] == fecha_iso) | 
        (df["Fecha_Str"] == fecha_latam) | 
        (df["Fecha_Str"] == fecha_corta)
    ]

    if eventos.empty:
        # Si no hubo coincidencia exacta, intentar parsear la columna con pandas
        df["Fecha_Parsed"] = pd.to_datetime(df["Fecha_Str"], errors="coerce", dayfirst=True)
        df["Fecha_Clean"] = df["Fecha_Parsed"].dt.strftime("%Y-%m-%d")
        eventos = df[df["Fecha_Clean"] == fecha_iso]

    if not eventos.empty:
        mensaje = f"🎉 <b>AGENDA MADAI - {tipo_notificacion} ({fecha_latam})</b> 🎉\n"
        mensaje += "=============================\n\n"

        for idx, (_, row) in enumerate(eventos.iterrows(), 1):
            evento_nombre = row.get("Evento", "Evento")
            tipo_show = row.get("Tipo", "")
            hora_contrato = row.get("Hora", "N/A")
            hora_citacion = row.get("Hora_Invitacion", "N/A")
            cliente = row.get("Cliente", "N/A")
            telefono = row.get("Telefono", "N/A")
            direccion = row.get("Direccion", "N/A")
            costo = row.get("Costo_Total", "0")
            pago = row.get("Estado_Pago", "N/A")

            mensaje += f"<b>{idx}. {evento_nombre} ({tipo_show})</b>\n"
            mensaje += f"⏰ <b>Hora Contrato:</b> {hora_contrato} | <b>Citación:</b> {hora_citacion}\n"
            mensaje += f"👤 <b>Cliente:</b> {cliente} (📱 {telefono})\n"
            mensaje += f"📍 <b>Lugar:</b> {direccion}\n"
            mensaje += f"💰 <b>Total:</b> S/ {costo} ({pago})\n"
            mensaje += "-----------------------------\n"

        enviar_mensaje(mensaje)
    else:
        enviar_mensaje(f"🤖 <b>Prueba Agenda Madai:</b> Notificador activo. No hay eventos registrados para la fecha objetivo ({fecha_latam}).")

if __name__ == "__main__":
    main()
