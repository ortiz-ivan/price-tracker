Price Tracker Automation

Price Tracker Automation es un script desarrollado en Python que realiza el seguimiento automático de productos en un e-commerce, detectando cambios de precio o disponibilidad, almacenando registros locales y enviando notificaciones por correo electrónico de forma programada.

Este proyecto está diseñado con un enfoque modular, seguro y fácilmente mantenible, integrando buenas prácticas de desarrollo para la automatización de tareas y monitoreo de datos web.

Características principales

Web Scraping automatizado: obtiene dinámicamente precios y estado de stock desde páginas de productos.

Persistencia local: guarda los datos históricos en productos.json para detectar cambios entre ejecuciones.

Notificaciones por correo electrónico: envía alertas automáticas ante variaciones de precio o stock.

Logging estructurado: registra toda la actividad en data/price_tracker.log con formato legible y trazabilidad completa.

Configuración segura: utiliza variables de entorno con .env para proteger credenciales.

Ejecución programada: emplea schedule para automatizar la ejecución diaria sin intervención manual.

Estructura del proyecto
price-tracker/
│
├── main.py                 # Script principal del sistema
├── requirements.txt        # Dependencias del proyecto
├── .env                    # Variables de entorno (no se versiona)
├── .env.example            # Plantilla de variables de entorno
├── .gitignore              # Archivos y carpetas excluidos del control de versiones
└── data/
    ├── productos.json      # Historial de precios y stock
    └── price_tracker.log   # Registro de ejecución y eventos


Instalación y configuración

1. Clonar el repositorio
   git clone https://github.com/tu_usuario/price-tracker.git
   cd price-tracker

2. Crear entorno virtual (opcional pero recomendado)
   python -m venv venv
   source venv/bin/activate # En Linux/macOS
   venv\Scripts\activate # En Windows

3. Instalar dependencias
   pip install -r requirements.txt

4. Configurar variables de entorno

Copia el archivo .env.example y renómbralo como .env:

cp .env.example .env

Edita el archivo .env con tus credenciales:

EMAIL_SENDER="tu_correo@gmail.com"
EMAIL_PASSWORD="tu_token_o_contraseña_app"
EMAIL_RECEIVER="correo_destino@gmail.com"

Importante: si usas Gmail, debes generar un token de aplicación
en lugar de usar tu contraseña real.

Ejecución

Ejecuta el script principal:

python main.py

El sistema ejecutará la tarea automáticamente todos los días a la hora configurada, almacenando resultados y registros en la carpeta data/.

Puedes modificar la hora en esta línea del código:

schedule.every().day.at("11:31").do(revisar_productos)

Tecnologías utilizadas
Módulo Descripción
requests Realiza solicitudes HTTP para obtener el HTML del sitio.
BeautifulSoup (bs4) Analiza el contenido HTML y extrae la información relevante.
schedule Programa la ejecución periódica de tareas.
logging Gestiona registros estructurados de eventos y errores.
smtplib / email.mime Permite enviar notificaciones por correo electrónico.
dotenv Carga de forma segura las variables de entorno desde .env.
Buenas prácticas implementadas

Separación de configuración y lógica: uso de .env y env.example para credenciales y ajustes.

Persistencia inteligente: evita duplicar información al comparar precios históricos.

Gestión de errores y trazabilidad: control de excepciones, logs con timestamps y diferentes niveles (INFO, WARNING, ERROR).

Estructura escalable: posibilidad de ampliar la lista de productos o incorporar nuevas fuentes fácilmente.

Compatibilidad multiplataforma: funciona en cualquier sistema con Python 3.x.
