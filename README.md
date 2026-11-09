# 🤖 VENTIX AI

Sistema inteligente de ventas mediante Telegram y Streamlit para tiendas de tecnología.

## 📋 Descripción

VENTIX AI es una plataforma completa de automatización de ventas que combina:

- **Bot de Telegram inteligente** para atención automatizada de clientes
- **Panel administrativo Streamlit** para gestión del negocio
- **Sistema de IA** para procesamiento de lenguaje natural
- **Persistencia con GitHub** para evitar pérdida de datos en Streamlit Cloud

## ✨ Características

### 🤖 Bot de Telegram
- Atención automatizada 24/7
- Catálogo interactivo por categorías
- Recomendaciones por presupuesto
- Comparación de productos
- Gestión de carritos de compras
- Consultas de stock y precios
- Procesamiento de lenguaje natural

### 📊 Panel Administrativo
- Dashboard con métricas en tiempo real
- Gestión completa de productos (CRUD)
- Gestión de pedidos y estados
- Análisis de ventas y reportes
- Gráficas interactivas
- Sistema de autenticación

### 🧠 Inteligencia Artificial
- Interpretación de consultas en lenguaje natural
- Detección de intenciones del usuario
- Recomendaciones inteligentes
- Contexto de conversación

### 💾 Persistencia
- Almacenamiento en JSON (sin base de datos)
- Sincronización automática con GitHub
- Respaldo de datos en la nube
- Recuperación automática ante reinicios

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- Cuenta de Telegram (para crear el bot)
- Cuenta de GitHub (opcional, para persistencia en la nube)

### 1. Clonar el Repositorio
```bash
git clone <tu-repositorio>
cd ventix-ai
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

### Configurar Bot de Telegram

1. **Crear el bot en Telegram:**
   - Abre una conversación con [@BotFather](https://t.me/BotFather) en Telegram
   - Envía `/newbot`
   - Sigue las instrucciones para crear tu bot
   - Copia el token que te proporciona

2. **Configurar variable de entorno:**
   ```bash
   # En Windows (PowerShell)
   $env:TELEGRAM_BOT_TOKEN = "tu-token-aqui"

   # En Linux/Mac
   export TELEGRAM_BOT_TOKEN="tu-token-aqui"
   ```

### Configurar Sincronización GitHub (Opcional pero Recomendado)

1. **Crear token de acceso personal en GitHub:**
   - Ve a GitHub Settings → Developer settings → Personal access tokens
   - Crea un nuevo token con permisos `repo`
   - Copia el token

2. **Crear repositorio en GitHub:**
   - Crea un nuevo repositorio para guardar los datos
   - El repositorio debe ser público o privado según tu preferencia

3. **Configurar secrets en Streamlit Community Cloud:**
   - Ve a tu app en Streamlit Cloud
   - Settings → Secrets
   - Agrega los siguientes secrets:

   ```toml
   GITHUB_TOKEN = "tu-token-de-github"
   GITHUB_REPO = "usuario/nombre-repositorio"
   GITHUB_DATA_PATH = "data"  # Opcional, valor por defecto
   ```

### Configurar Panel Administrativo

El panel utiliza credenciales por defecto:
- **Usuario:** `admin`
- **Contraseña:** `admin123`

Puedes cambiar estas credenciales desde el panel en la sección Configuración.

## 🏃 Ejecución

### Ejecutar Panel Administrativo (Streamlit)
```bash
streamlit run app.py
```

El panel estará disponible en `http://localhost:8501`

### Ejecutar Bot de Telegram
```bash
python bot.py
```

El bot comenzará a responder mensajes en Telegram.

## 📁 Estructura del Proyecto

```
VENTIX-AI/
│
├── app.py                          # Panel administrativo Streamlit
├── bot.py                          # Bot de Telegram
├── requirements.txt                 # Dependencias Python
├── .gitignore                      # Archivos a ignorar
├── README.md                       # Documentación
│
├── data/                           # Almacenamiento JSON
│   ├── productos.json              # Catálogo de productos
│   ├── pedidos.json                # Pedidos de clientes
│   ├── ventas.json                 # Historial de ventas
│   └── carritos.json               # Carritos activos
│
├── modules/                        # Módulos del sistema
│   ├── __init__.py
│   ├── catalogo.py                 # Gestión del catálogo
│   ├── pedidos.py                  # Gestión de pedidos
│   ├── ventas.py                   # Gestión de ventas
│   ├── inteligencia.py             # Sistema de IA
│   ├── autenticacion.py            # Autenticación
│   ├── telegram_handler.py         # Handler de Telegram
│   └── persistencia.py             # Persistencia con GitHub
│
├── assets/                         # Recursos estáticos
│   └── styles.css                  # Estilos personalizados
│
└── .streamlit/
    └── config.toml                 # Configuración de Streamlit
```

## 🌐 Despliegue en Streamlit Community Cloud

### 1. Preparar Repositorio

Asegúrate de que tu repositorio de GitHub contenga:
- Todos los archivos del proyecto
- El archivo `requirements.txt`
- Los archivos JSON en `data/` (inicialmente vacíos o con datos de ejemplo)

### 2. Crear App en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Haz clic en "New app"
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Repository:** Tu repositorio
   - **Branch:** `main` (o tu branch principal)
   - **Main file path:** `app.py`
5. Haz clic en "Deploy"

### 3. Configurar Secrets

En tu app de Streamlit Cloud, ve a Settings → Secrets y agrega:

```toml
TELEGRAM_BOT_TOKEN = "tu-token-de-telegram"
GITHUB_TOKEN = "tu-token-de-github"
GITHUB_REPO = "usuario/nombre-repositorio"
GITHUB_DATA_PATH = "data"
```

### 4. Limitaciones Importantes

⚠️ **Streamlit Community Cloud NO ejecuta procesos independientes:**
- El bot de Telegram (`bot.py`) NO puede ejecutarse en Streamlit Cloud
- Debes ejecutar el bot en un servidor separado (Heroku, Railway, Render, etc.)
- O usar un servicio de webhooks para Telegram

**Solución:**
1. **Opción A:** Despliega el bot en un servicio gratuito como [Render](https://render.com) o [Railway](https://railway.app)
2. **Opción B:** Ejecuta el bot localmente si no necesitas disponibilidad 24/7
3. **Opción C:** Usa webhooks de Telegram con un servicio como ngrok para desarrollo

## 📚 Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Iniciar el bot y ver bienvenida |
| `/help` | Ver lista de comandos disponibles |
| `/catalogo` | Ver catálogo completo de productos |
| `/categorias` | Ver categorías disponibles |
| `/carrito` | Ver tu carrito de compras |
| `/vaciar` | Vaciar tu carrito |
| `/pedido` | Ver tus pedidos |
| `/contactar` | Contactar con un humano |

## 💬 Consultas Naturales

El bot también responde a consultas en lenguaje natural:

- "Muéstrame las laptops"
- "Productos hasta $500"
- "¿Cuánto cuesta el iPhone?"
- "Compara MacBook y HP"
- "¿Tienen stock de monitores?"

## 🔧 Personalización

### Agregar Productos

Puedes agregar productos de dos formas:

1. **Desde el panel administrativo:**
   - Ve a la sección "Productos"
   - Pestaña "Agregar Producto"
   - Completa el formulario

2. **Editando `data/productos.json` directamente:**
   ```json
   {
     "id": "P009",
     "nombre": "Nombre del producto",
     "categoria": "Laptops",
     "precio": 999.99,
     "existencias": 10,
     "descripcion": "Descripción del producto",
     "especificaciones": {
       "procesador": "Intel Core i7",
       "ram": "16GB"
     }
   }
   ```

### Modificar Estilos

Edita `assets/styles.css` para personalizar el diseño del panel.

### Cambiar Credenciales

Desde el panel, ve a Configuración → Gestión de Cuentas para cambiar la contraseña.

## 🐛 Solución de Problemas

### El bot no responde
- Verifica que el token sea correcto
- Asegúrate de que el bot esté ejecutándose
- Revisa los logs del bot

### Los datos se pierden al reiniciar
- Configura la sincronización con GitHub
- Verifica que los secrets estén configurados correctamente

### Error de importación de módulos
- Asegúrate de estar en el directorio del proyecto
- Verifica que el entorno virtual esté activado
- Reinstala las dependencias: `pip install -r requirements.txt`

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para soporte, contacta a:
- Email: soporte@ventix.ai
- Telegram: @ventix_support

---

Desarrollado con ❤️ para tiendas de tecnología
