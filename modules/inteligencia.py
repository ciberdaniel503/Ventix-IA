"""
Módulo de inteligencia artificial para procesamiento de lenguaje natural
Interpreta consultas de clientes y genera respuestas inteligentes
"""

import re
from typing import Dict, List, Optional, Tuple
from modules.catalogo import catalogo
import logging

logger = logging.getLogger(__name__)


class InteligenciaNLP:
    """Sistema de IA para interpretar consultas de clientes."""

    def __init__(self):
        """Inicializa el sistema de IA."""
        self.patron_presupuesto = re.compile(r'(\d+[\.,]?\d*)\s*(?:dólares?|usd|\$|euros?|€)?', re.IGNORECASE)
        self.patron_categoria = {
            'computadora|computadoras|desktop|pc|torre': 'Computadoras',
            'laptop|notebook|portátil|portatil': 'Laptops',
            'celular|celulares|móvil|movil|telefono|telefonos|smartphone': 'Celulares',
            'accesorio|accesorios|mouse|teclado|monitor|auricular|cargador': 'Accesorios'
        }

    def procesar_consulta(self, texto: str) -> Dict:
        """
        Procesa una consulta de texto y extrae información relevante.

        Returns:
            Dict con: {
                'intencion': str (catalogo, presupuesto, comparar, stock, etc.),
                'categoria': Optional[str],
                'presupuesto': Optional[float],
                'productos': List[Dict],
                'respuesta': str
            }
        """
        texto_lower = texto.lower()

        # Detectar intención
        intencion = self._detectar_intencion(texto_lower)

        # Extraer información según intención
        resultado = {
            'intencion': intencion,
            'categoria': None,
            'presupuesto': None,
            'productos': [],
            'respuesta': ''
        }

        if intencion == 'catalogo':
            resultado['categoria'] = self._detectar_categoria(texto_lower)
            if resultado['categoria']:
                resultado['productos'] = catalogo.obtener_por_categoria(resultado['categoria'])
            else:
                resultado['productos'] = catalogo.obtener_todos()
            resultado['respuesta'] = self._generar_respuesta_catalogo(resultado)

        elif intencion == 'presupuesto':
            resultado['presupuesto'] = self._extraer_presupuesto(texto)
            resultado['categoria'] = self._detectar_categoria(texto_lower)
            resultado['productos'] = catalogo.recomendar_por_presupuesto(
                resultado['presupuesto'],
                resultado['categoria']
            )
            resultado['respuesta'] = self._generar_respuesta_presupuesto(resultado)

        elif intencion == 'producto':
            productos = catalogo.buscar(texto)
            resultado['productos'] = productos
            resultado['respuesta'] = self._generar_respuesta_producto(productos)

        elif intencion == 'stock':
            productos = catalogo.buscar(texto)
            resultado['productos'] = productos
            resultado['respuesta'] = self._generar_respuesta_stock(productos)

        elif intencion == 'comparar':
            productos = catalogo.buscar(texto)
            resultado['productos'] = productos[:3]  # Limitar a 3 productos
            resultado['respuesta'] = self._generar_respuesta_comparar(resultado['productos'])

        elif intencion == 'saludo':
            resultado['respuesta'] = self._generar_respuesta_saludo()

        elif intencion == 'ayuda':
            resultado['respuesta'] = self._generar_respuesta_ayuda()

        else:
            resultado['respuesta'] = self._generar_respuesta_no_entendido()

        return resultado

    def _detectar_intencion(self, texto: str) -> str:
        """Detecta la intención del usuario."""
        if any(palabra in texto for palabra in ['hola', 'buenos', 'buenas', 'hey', 'saludos']):
            return 'saludo'

        if any(palabra in texto for palabra in ['ayuda', 'qué puedes', 'que puedes', 'opciones', 'comandos']):
            return 'ayuda'

        if any(palabra in texto for palabra in ['catálogo', 'catalogo', 'productos', 'ver', 'mostrar']):
            return 'catalogo'

        if any(palabra in texto for palabra in ['presupuesto', 'precio', 'menos de', 'hasta', 'máximo', 'maximo']):
            return 'presupuesto'

        if any(palabra in texto for palabra in ['comparar', 'diferencia', 'cual es mejor', 'comparación']):
            return 'comparar'

        if any(palabra in texto for palabra in ['stock', 'existencias', 'disponible', 'tienen', 'hay']):
            return 'stock'

        if any(palabra in texto for palabra in ['cuánto', 'cuanto', 'precio', 'cuesta', 'vale']):
            return 'producto'

        # Por defecto, asumir búsqueda de producto
        return 'producto'

    def _detectar_categoria(self, texto: str) -> Optional[str]:
        """Detecta la categoría mencionada en el texto."""
        for patron, categoria in self.patron_categoria.items():
            if re.search(patron, texto, re.IGNORECASE):
                return categoria
        return None

    def _extraer_presupuesto(self, texto: str) -> Optional[float]:
        """Extrae el presupuesto del texto."""
        coincidencias = self.patron_presupuesto.findall(texto)
        if coincidencias:
            try:
                # Limpiar el número (eliminar comas, puntos de miles)
                numero = coincidencias[0].replace(',', '').replace('.', '')
                return float(numero)
            except:
                return None
        return None

    def _generar_respuesta_catalogo(self, resultado: Dict) -> str:
        """Genera respuesta para mostrar catálogo."""
        productos = resultado['productos']
        categoria = resultado['categoria']

        if not productos:
            return "No encontré productos en esa categoría. ¿Te gustaría ver otra categoría?"

        if categoria:
            respuesta = f"📦 **Catálogo de {categoria}**\n\n"
        else:
            respuesta = "📦 **Catálogo Completo**\n\n"

        for producto in productos[:5]:  # Limitar a 5 productos
            respuesta += f"• {producto['nombre']}\n"
            respuesta += f"  💰 ${producto['precio']:.2f}\n"
            respuesta += f"  📦 {producto['existencias']} disponibles\n"
            respuesta += f"  📝 {producto['descripcion']}\n\n"

        respuesta += f"\nMostrando {len(productos[:5])} de {len(productos)} productos."
        return respuesta

    def _generar_respuesta_presupuesto(self, resultado: Dict) -> str:
        """Genera respuesta para recomendaciones por presupuesto."""
        productos = resultado['productos']
        presupuesto = resultado['presupuesto']
        categoria = resultado['categoria']

        if not productos:
            return f"No encontré productos dentro de tu presupuesto de ${presupuesto:.2f}. " \
                   f"¿Te gustaría aumentar el presupuesto o buscar en otra categoría?"

        if categoria:
            respuesta = f"💡 **Recomendaciones de {categoria} hasta ${presupuesto:.2f}**\n\n"
        else:
            respuesta = f"💡 **Recomendaciones hasta ${presupuesto:.2f}**\n\n"

        for producto in productos[:5]:
            respuesta += f"✨ {producto['nombre']}\n"
            respuesta += f"   💰 ${producto['precio']:.2f}\n"
            respuesta += f"   📦 {producto['existencias']} disponibles\n\n"

        return respuesta

    def _generar_respuesta_producto(self, productos: List[Dict]) -> str:
        """Genera respuesta para información de producto específico."""
        if not productos:
            return "No encontré ese producto. ¿Podrías ser más específico o buscar por categoría?"

        if len(productos) == 1:
            p = productos[0]
            respuesta = f"🔍 **{p['nombre']}**\n\n"
            respuesta += f"💰 Precio: ${p['precio']:.2f}\n"
            respuesta += f"📦 Existencias: {p['existencias']}\n"
            respuesta += f"📝 Descripción: {p['descripcion']}\n\n"
            respuesta += "**Especificaciones:**\n"
            for clave, valor in p.get('especificaciones', {}).items():
                respuesta += f"• {clave}: {valor}\n"
            return respuesta
        else:
            respuesta = f"Encontré {len(productos)} productos:\n\n"
            for p in productos[:5]:
                respuesta += f"• {p['nombre']} - ${p['precio']:.2f}\n"
            return respuesta

    def _generar_respuesta_stock(self, productos: List[Dict]) -> str:
        """Genera respuesta para consulta de stock."""
        if not productos:
            return "No encontré información de stock para esos productos."

        respuesta = "📦 **Estado de Stock**\n\n"
        for p in productos[:5]:
            if p['existencias'] > 10:
                emoji = "✅"
            elif p['existencias'] > 0:
                emoji = "⚠️"
            else:
                emoji = "❌"

            respuesta += f"{emoji} {p['nombre']}: {p['existencias']} unidades\n"

        return respuesta

    def _generar_respuesta_comparar(self, productos: List[Dict]) -> str:
        """Genera respuesta para comparar productos."""
        if len(productos) < 2:
            return "Necesito al menos 2 productos para comparar. ¿Podrías mencionar más productos?"

        respuesta = "⚖️ **Comparación de Productos**\n\n"

        for p in productos:
            respuesta += f"🔹 {p['nombre']}\n"
            respuesta += f"   💰 ${p['precio']:.2f}\n"
            respuesta += f"   📦 {p['existencias']} disponibles\n"
            if 'especificaciones' in p:
                for clave, valor in p['especificaciones'].items():
                    respuesta += f"   • {clave}: {valor}\n"
            respuesta += "\n"

        return respuesta

    def _generar_respuesta_saludo(self) -> str:
        """Genera respuesta de saludo."""
        return "👋 ¡Hola! Soy tu asistente de ventas de VENTIX AI.\n\n" \
               "Puedo ayudarte a:\n" \
               "• 📦 Ver el catálogo de productos\n" \
               "• 💰 Buscar productos por presupuesto\n" \
               "• 🔍 Comparar productos\n" \
               "• 📦 Consultar stock y precios\n" \
               "• 🛒 Agregar productos al carrito\n\n" \
               "¿En qué puedo ayudarte hoy?"

    def _generar_respuesta_ayuda(self) -> str:
        """Genera respuesta de ayuda."""
        return "📖 **Comandos Disponibles**\n\n" \
               "• Ver catálogo: \"Muéstrame el catálogo\" o \"ver laptops\"\n" \
               "• Buscar por presupuesto: \"Productos hasta $500\" o \"Laptops hasta $1000\"\n" \
               "• Información de producto: \"¿Cuánto cuesta el iPhone?\" o \"Infórmame sobre el MacBook\"\n" \
               "• Consultar stock: \"¿Tienen stock de laptops?\"\n" \
               "• Comparar: \"Compara iPhone y Samsung\"\n\n" \
               "Escribe tu consulta de forma natural y te ayudaré."

    def _generar_respuesta_no_entendido(self) -> str:
        """Genera respuesta cuando no se entiende la consulta."""
        return "🤔 No estoy seguro de entender tu consulta. " \
               "¿Podrías reformularla o usar palabras clave como: catálogo, presupuesto, comparar, stock?\n\n" \
               "Escribe \"ayuda\" para ver los comandos disponibles."

    def recomendar_producto(self, consulta: str) -> Optional[Dict]:
        """
        Recomienda un producto basado en una consulta.
        """
        resultado = self.procesar_consulta(consulta)
        if resultado['productos']:
            return resultado['productos'][0]
        return None


# Instancia global de IA
inteligencia = InteligenciaNLP()
