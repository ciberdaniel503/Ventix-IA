"""
Módulo de manejo del bot de Telegram
Gestiona comandos, mensajes y carritos de usuarios
"""

from typing import Dict, Optional
from modules.catalogo import catalogo
from modules.pedidos import gestor_pedidos
from modules.inteligencia import inteligencia
import logging

logger = logging.getLogger(__name__)


class TelegramHandler:
    """Manejador del bot de Telegram."""

    def __init__(self):
        """Inicializa el manejador."""
        self.contextos = {}  # Mantener contexto de conversación por usuario

    def procesar_mensaje(self, user_id: str, texto: str) -> str:
        """
        Procesa un mensaje de un usuario de Telegram.

        Args:
            user_id: ID del usuario de Telegram
            texto: Texto del mensaje

        Returns:
            str: Respuesta para el usuario
        """
        try:
            # Procesar comando si comienza con /
            if texto.startswith('/'):
                return self._procesar_comando(user_id, texto)

            # Procesar mensaje normal con IA
            resultado = inteligencia.procesar_consulta(texto)

            # Mantener contexto
            self.contextos[user_id] = {
                'ultima_consulta': texto,
                'intencion': resultado['intencion']
            }

            if resultado['intencion'] == 'compra':
                if resultado['compra_directa']:
                    producto = resultado['productos'][0]
                    return self.agregar_producto_carrito(user_id, producto['id'])
                return resultado['respuesta']

            texto_normalizado = inteligencia._normalizar_texto(texto)
            if 'carrito' in texto_normalizado.split():
                return self._comando_carrito(user_id)

            return resultado['respuesta']

        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return "❌ Ocurrió un error al procesar tu mensaje. Por favor intenta nuevamente."

    def _procesar_comando(self, user_id: str, comando: str) -> str:
        """Procesa comandos del bot."""
        comando = comando.lower()

        if comando == '/start':
            return self._comando_start(user_id)
        elif comando == '/help':
            return self._comando_help()
        elif comando == '/catalogo':
            return self._comando_catalogo()
        elif comando == '/categorias':
            return self._comando_categorias()
        elif comando == '/carrito':
            return self._comando_carrito(user_id)
        elif comando == '/vaciar':
            return self._comando_vaciar_carrito(user_id)
        elif comando == '/pedido':
            return self._comando_pedido(user_id)
        elif comando == '/contactar':
            return self._comando_contactar()
        else:
            return "❓ Comando no reconocido. Usa /help para ver los comandos disponibles."

    def _comando_start(self, user_id: str) -> str:
        """Comando /start - Bienvenida."""
        mensaje = "🤖 **¡Bienvenido a VENTIX AI!**\n\n"
        mensaje += "Soy tu asistente inteligente de ventas. "
        mensaje += "Estoy aquí para ayudarte a encontrar el producto perfecto.\n\n"
        mensaje += "📦 Explora nuestro catálogo\n"
        mensaje += "💰 Compra dentro de tu presupuesto\n"
        mensaje += "🔍 Compara productos\n"
        mensaje += "🛒 Gestiona tu carrito\n\n"
        mensaje += "Escribe /help para ver todos los comandos disponibles."
        return mensaje

    def _comando_help(self) -> str:
        """Comando /help - Ayuda."""
        mensaje = "📖 **Comandos Disponibles**\n\n"
        mensaje += "🔹 /start - Iniciar el bot\n"
        mensaje += "🔹 /help - Ver esta ayuda\n"
        mensaje += "🔹 /catalogo - Ver catálogo completo\n"
        mensaje += "🔹 /categorias - Ver categorías disponibles\n"
        mensaje += "🔹 /carrito - Ver mi carrito\n"
        mensaje += "🔹 /vaciar - Vaciar mi carrito\n"
        mensaje += "🔹 /pedido - Ver mis pedidos\n"
        mensaje += "🔹 /contactar - Hablar con un humano\n\n"
        mensaje += "💬 **Consultas Naturales**\n\n"
        mensaje += "También puedes escribir en lenguaje natural:\n"
        mensaje += "• \"Muéstrame las laptops\"\n"
        mensaje += "• \"Productos hasta $500\"\n"
        mensaje += "• \"¿Cuánto cuesta el iPhone?\"\n"
        mensaje += "• \"Compara MacBook y HP\"\n"
        mensaje += "• \"¿Tienen stock de monitores?\"\n"
        mensaje += "• \"Quiero comprar MacBook Air M2\" (lo agrega al carrito)"
        return mensaje

    def _comando_catalogo(self) -> str:
        """Comando /catalogo - Mostrar catálogo."""
        productos = catalogo.obtener_todos()

        if not productos:
            return "❌ No hay productos disponibles en este momento."

        mensaje = "📦 **Catálogo Completo**\n\n"

        for p in productos[:10]:  # Limitar a 10 productos
            mensaje += f"• {p['nombre']}\n"
            mensaje += f"  💰 ${p['precio']:.2f}\n"
            mensaje += f"  📦 {p['existencias']} disp.\n\n"

        if len(productos) > 10:
            mensaje += f"\nMostrando 10 de {len(productos)} productos."

        return mensaje

    def _comando_categorias(self) -> str:
        """Comando /categorias - Mostrar categorías."""
        categorias = catalogo.obtener_categorias()

        mensaje = "📂 **Categorías Disponibles**\n\n"

        for i, cat in enumerate(categorias, 1):
            productos = catalogo.obtener_por_categoria(cat)
            mensaje += f"{i}. {cat} ({len(productos)} productos)\n"

        mensaje += "\nEscribe el nombre de una categoría para ver sus productos."
        return mensaje

    def _comando_carrito(self, user_id: str) -> str:
        """Comando /carrito - Ver carrito."""
        carrito = gestor_pedidos.obtener_carrito(user_id)

        if not carrito or not carrito['items']:
            return "🛒 Tu carrito está vacío.\n\nEscribe el nombre de un producto para agregarlo."

        mensaje = "🛒 **Tu Carrito**\n\n"

        total = 0
        for item in carrito['items']:
            mensaje += f"• {item['nombre']}\n"
            mensaje += f"  Cantidad: {item['cantidad']}\n"
            mensaje += f"  Subtotal: ${item['subtotal']:.2f}\n\n"
            total += item['subtotal']

        mensaje += f"💰 **Total: ${total:.2f}**\n\n"
        mensaje += "Para confirmar tu pedido, usa el comando /pedido"

        return mensaje

    def _comando_vaciar_carrito(self, user_id: str) -> str:
        """Comando /vaciar - Vaciar carrito."""
        gestor_pedidos.vaciar_carrito(user_id)
        return "🗑️ Tu carrito ha sido vaciado."

    def _comando_pedido(self, user_id: str) -> str:
        """Comando /pedido - Ver pedidos."""
        pedidos = gestor_pedidos.obtener_pedidos_usuario(user_id)

        if not pedidos:
            return "📋 No tienes pedidos registrados.\n\nAgrega productos a tu carrito para realizar un pedido."

        mensaje = "📋 **Tus Pedidos**\n\n"

        for pedido in pedidos:
            emoji_estado = self._get_emoji_estado(pedido['estado'])
            mensaje += f"{emoji_estado} **Pedido {pedido['id']}**\n"
            mensaje += f"   Estado: {pedido['estado']}\n"
            mensaje += f"   Total: ${pedido['total']:.2f}\n"
            mensaje += f"   Fecha: {pedido['creado_en'][:10]}\n\n"

        return mensaje

    def _comando_contactar(self) -> str:
        """Comando /contactar - Contactar humano."""
        return "👤 **Contactar con un Humano**\n\n" \
               "Si necesitas ayuda personalizada, puedes:\n" \
               "• Llamar al: +1 234 567 890\n" \
               "• Email: soporte@ventix.ai\n" \
               "• WhatsApp: +1 234 567 890\n\n" \
               "Horario de atención: Lun-Vie 9:00-18:00"

    def _get_emoji_estado(self, estado: str) -> str:
        """Obtiene emoji según estado del pedido."""
        emojis = {
            'pendiente': '⏳',
            'en_proceso': '🔄',
            'enviado': '🚚',
            'entregado': '✅',
            'cancelado': '❌'
        }
        return emojis.get(estado, '❓')

    def agregar_producto_carrito(self, user_id: str, producto_id: str, cantidad: int = 1) -> str:
        """Agrega un producto al carrito del usuario."""
        if gestor_pedidos.agregar_al_carrito(user_id, producto_id, cantidad):
            producto = catalogo.obtener_por_id(producto_id)
            return f"✅ **{producto['nombre']}** agregado al carrito ({cantidad} unidad/es)."
        else:
            return "❌ No pude agregar el producto. Verifica que exista y tenga stock disponible."

    def obtener_resumen_producto(self, producto_id: str) -> str:
        """Obtiene un resumen de un producto para mostrar en Telegram."""
        producto = catalogo.obtener_por_id(producto_id)

        if not producto:
            return "❌ Producto no encontrado."

        mensaje = f"🔍 **{producto['nombre']}**\n\n"
        mensaje += f"💰 Precio: ${producto['precio']:.2f}\n"
        mensaje += f"📦 Stock: {producto['existencias']}\n"
        mensaje += f"📝 {producto['descripcion']}\n\n"
        mensaje += "**Especificaciones:**\n"

        for clave, valor in producto.get('especificaciones', {}).items():
            mensaje += f"• {clave}: {valor}\n"

        return mensaje


# Instancia global del manejador de Telegram
telegram_handler = TelegramHandler()
