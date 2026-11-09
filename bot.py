"""
VENTIX AI - Bot de Telegram
Asistente inteligente de ventas automatizado
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from modules.catalogo import catalogo
from modules.pedidos import gestor_pedidos
from modules.inteligencia import inteligencia
from modules.telegram_handler import telegram_handler
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Handlers de comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /start."""
    mensaje = telegram_handler._comando_start(str(update.effective_user.id))
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /help."""
    mensaje = telegram_handler._comando_help()
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def catalogo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /catalogo."""
    mensaje = telegram_handler._comando_catalogo()
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def categorias_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /categorias."""
    mensaje = telegram_handler._comando_categorias()
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def carrito_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /carrito."""
    user_id = str(update.effective_user.id)
    mensaje = telegram_handler._comando_carrito(user_id)
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def vaciar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /vaciar."""
    user_id = str(update.effective_user.id)
    mensaje = telegram_handler._comando_vaciar_carrito(user_id)
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def pedido_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /pedido."""
    user_id = str(update.effective_user.id)
    mensaje = telegram_handler._comando_pedido(user_id)
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def contactar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler del comando /contactar."""
    mensaje = telegram_handler._comando_contactar()
    await update.message.reply_text(mensaje, parse_mode='Markdown')


async def mostrar_categoria(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra productos de una categoría específica."""
    user_id = str(update.effective_user.id)

    if context.args:
        categoria = ' '.join(context.args)
        productos = catalogo.obtener_por_categoria(categoria)

        if productos:
            mensaje = f"📦 **{categoria}**\n\n"
            for p in productos[:5]:
                mensaje += f"• {p['nombre']}\n"
                mensaje += f"  💰 ${p['precio']:.2f}\n"
                mensaje += f"  📦 {p['existencias']} disp.\n\n"

            # Crear botones para agregar al carrito
            keyboard = []
            for p in productos[:5]:
                keyboard.append([
                    InlineKeyboardButton(
                        f"Agregar {p['nombre']}",
                        callback_data=f"add_{p['id']}"
                    )
                ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(mensaje, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(f"❌ No encontré productos en la categoría {categoria}")
    else:
        await update.message.reply_text("❌ Por favor especifica una categoría. Ejemplo: /categoria Laptops")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para callbacks de botones inline."""
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data

    if data.startswith('add_'):
        producto_id = data[4:]
        mensaje = telegram_handler.agregar_producto_carrito(user_id, producto_id, 1)
        await query.edit_message_text(text=mensaje, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensajes de texto."""
    user_id = str(update.effective_user.id)
    texto = update.message.text

    # Procesar mensaje con el handler
    respuesta = telegram_handler.procesar_mensaje(user_id, texto)
    await update.message.reply_text(respuesta, parse_mode='Markdown')


def main():
    """Función principal del bot."""
    # Obtener token del bot desde variable de entorno
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN no está configurado")
        logger.error("Por favor configura la variable de entorno TELEGRAM_BOT_TOKEN")
        return

    # Crear la aplicación
    application = Application.builder().token(token).build()

    # Registrar handlers de comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("catalogo", catalogo_command))
    application.add_handler(CommandHandler("categorias", categorias_command))
    application.add_handler(CommandHandler("carrito", carrito_command))
    application.add_handler(CommandHandler("vaciar", vaciar_command))
    application.add_handler(CommandHandler("pedido", pedido_command))
    application.add_handler(CommandHandler("contactar", contactar_command))
    application.add_handler(CommandHandler("categoria", mostrar_categoria))

    # Registrar handler de callbacks
    application.add_handler(CallbackQueryHandler(button_callback))

    # Registrar handler de mensajes
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Iniciar el bot
    logger.info("🤖 Iniciando VENTIX AI Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
