import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import re
import os
import logging
from dotenv import load_dotenv

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

# --- CONFIGURACIÓN ---
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)  # Crea la carpeta si no existe

PRODUCTOS = [
    "https://nissei.com/py/impresora-3d-bambu-lab-a1-combo-ams-lite-multi-color-500mm-s",
    "https://nissei.com/py/xiaomi-redmi-note-14-5g-dual",
]

PRECIO_FILE = os.path.join(DATA_DIR, "productos.json")
LOG_FILE = os.path.join(DATA_DIR, "price_tracker.log")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# También mostramos los logs en consola
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)


# --- FUNCIONES AUXILIARES ---
def limpiar_precio(precio_str):
    """Extrae solo números del precio para comparaciones"""
    numeros = re.findall(r"\d+", precio_str.replace(".", ""))
    return int("".join(numeros)) if numeros else None


def enviar_correo(asunto, cuerpo):
    """Envía correo usando Gmail"""
    mensaje = MIMEMultipart()
    mensaje["From"] = EMAIL_SENDER
    mensaje["To"] = EMAIL_RECEIVER
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, mensaje.as_string())
        server.quit()
        logging.info("Correo enviado correctamente: %s", asunto)
    except Exception as e:
        logging.error("Error al enviar correo: %s", e)


# --- FUNCIÓN PRINCIPAL ---
def revisar_productos():
    resultados = []

    # Leer archivo previo (si existe)
    if os.path.exists(PRECIO_FILE):
        with open(PRECIO_FILE, "r") as f:
            datos_previos = json.load(f)
    else:
        datos_previos = {}

    for url in PRODUCTOS:
        logging.info("Revisando producto: %s", url)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.warning("Error al conectar con %s: %s", url, e)
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Extraer precio
        precio_tag = soup.find("span", class_="price")
        precio_texto = precio_tag.text.strip() if precio_tag else "Desconocido"
        precio_actual = (
            limpiar_precio(precio_texto) if precio_texto != "Desconocido" else None
        )

        # Extraer stock
        stock_tag = soup.find(
            "span", string=lambda text: text and "stock" in text.lower()
        )
        stock_actual = stock_tag.text.strip() if stock_tag else "Desconocido"

        # Recuperar datos previos
        previos = datos_previos.get(url, {})
        precio_anterior = previos.get("precio")
        stock_anterior = previos.get("stock")

        # Verificar cambios
        cambio = precio_actual != precio_anterior or stock_actual != stock_anterior

        resultados.append(
            {
                "url": url,
                "precio": precio_texto,
                "stock": stock_actual,
                "cambio": cambio,
            }
        )

        if cambio:
            logging.info(
                "Cambio detectado en %s | Precio: %s | Stock: %s",
                url,
                precio_texto,
                stock_actual,
            )

        # Actualizar datos
        datos_previos[url] = {"precio": precio_actual, "stock": stock_actual}

    # Guardar nuevos datos
    with open(PRECIO_FILE, "w") as f:
        json.dump(datos_previos, f, indent=4)

    # Preparar cuerpo del correo
    cuerpo = "Reporte diario de productos:\n\n"
    for r in resultados:
        cuerpo += f"Producto: {r['url']}\n"
        cuerpo += f"Precio: {r['precio']}\n"
        cuerpo += f"Stock: {r['stock']}\n"
        cuerpo += "Cambio detectado: {}\n\n".format("Sí" if r["cambio"] else "No")

    # Determinar asunto
    hubo_cambio = any(r["cambio"] for r in resultados)
    asunto = (
        "Cambios detectados en productos"
        if hubo_cambio
        else "Estado diario de productos"
    )

    enviar_correo(asunto, cuerpo)


# --- PROGRAMAR EJECUCIÓN DIARIA ---
schedule.every().day.at("12:00").do(revisar_productos)
logging.info("Tarea programada: revisión diaria a las 12:00")

while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except Exception as e:
        logging.critical("Error inesperado en el loop principal: %s", e)
        time.sleep(60)
