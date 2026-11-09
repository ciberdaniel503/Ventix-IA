"""
Módulo de inteligencia artificial para procesamiento de lenguaje natural
Interpreta consultas de clientes y genera respuestas inteligentes
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple
from modules.catalogo import catalogo
import logging

logger = logging.getLogger(__name__)


class InteligenciaNLP:
    """Sistema de IA para interpretar consultas de clientes."""

    def __init__(self):
        """Inicializa el sistema de IA."""
        self.patron_presupuesto = re.compile(
            r'(?<!\w)(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?)(?!\w)'
        )
        self.patron_categoria = {
            'computadora|computadoras|desktop|pc|torre': 'Computadoras',
            'laptop|notebook|portátil|portatil': 'Laptops',
            'celular|celulares|móvil|movil|telefono|telefonos|smartphone': 'Celulares',
            'accesorio|accesorios|mouse|teclado|monitor|auricular|cargador': 'Accesorios'
        }
        self.palabras_ignoradas_busqueda = {
            'quiero', 'comprar', 'compra', 'comprame', 'adquirir', 'agregar',
            'agrega', 'añadir', 'anadir', 'anade', 'añade', 'carrito', 'al',
            'una', 'uno', 'unos', 'unas', 'un', 'el', 'la', 'los', 'las',
            'de', 'del', 'por', 'favor', 'me', 'gustaria', 'gustaría',
            'podrias', 'podrías', 'puedes', 'puedo', 'dame', 'necesito',
            'tienen', 'tiene', 'hay', 'disponible', 'disponibles', 'stock',
            'existencias', 'cuanto', 'cuánto', 'cuesta', 'precio', 'vale',
            'informacion', 'información', 'sobre', 'que', 'qué', 'es',
            'compara', 'comparar', 'con', 'y'
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
            'compra_directa': False,
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
            if resultado['presupuesto'] is not None:
                resultado['productos'] = catalogo.recomendar_por_presupuesto(
                    resultado['presupuesto'],
                    resultado['categoria']
                )
            resultado['respuesta'] = self._generar_respuesta_presupuesto(resultado)

        elif intencion == 'producto':
            resultado['categoria'] = self._detectar_categoria(texto_lower)
            productos, _ = self._buscar_productos_consulta(texto, resultado['categoria'])
            resultado['productos'] = productos
            resultado['respuesta'] = self._generar_respuesta_producto(productos)

        elif intencion == 'stock':
            resultado['categoria'] = self._detectar_categoria(texto_lower)
            productos, _ = self._buscar_productos_consulta(texto, resultado['categoria'])
            resultado['productos'] = productos
            resultado['respuesta'] = self._generar_respuesta_stock(productos)

        elif intencion == 'comparar':
            resultado['categoria'] = self._detectar_categoria(texto_lower)
            productos, _ = self._buscar_productos_consulta(
                texto, resultado['categoria'], coincidir_cualquier_termino=True
            )
            resultado['productos'] = productos[:3]  # Limitar a 3 productos
            resultado['respuesta'] = self._generar_respuesta_comparar(resultado['productos'])

        elif intencion == 'compra':
            resultado['categoria'] = self._detectar_categoria(texto_lower)
            productos, compra_directa = self._buscar_productos_consulta(
                texto, resultado['categoria']
            )
            resultado['productos'] = productos
            resultado['compra_directa'] = compra_directa and len(productos) == 1
            resultado['respuesta'] = self._generar_respuesta_compra(
                productos, resultado['categoria'], resultado['compra_directa']
            )

        elif intencion == 'saludo':
            resultado['respuesta'] = self._generar_respuesta_saludo()

        elif intencion == 'ayuda':
            resultado['respuesta'] = self._generar_respuesta_ayuda()

        else:
            resultado['respuesta'] = self._generar_respuesta_no_entendido()

        return resultado

    def _detectar_intencion(self, texto: str) -> str:
        """Detecta la intención del usuario."""
        texto = self._normalizar_texto(texto)

        if any(palabra in texto for palabra in ['hola', 'buenos', 'buenas', 'hey', 'saludos']):
            return 'saludo'

        if any(palabra in texto for palabra in ['ayuda', 'que puedes', 'opciones', 'comandos']):
            return 'ayuda'

        if any(palabra in texto for palabra in ['comparar', 'compara', 'diferencia', 'cual es mejor']):
            return 'comparar'

        if any(palabra in texto for palabra in ['presupuesto', 'menos de', 'hasta', 'maximo', 'dolares', 'usd', 'euros', '$', '€']):
            return 'presupuesto'

        if re.search(r'\b\d+(?:[.,]\d+)?\b', texto) and any(
            frase in texto for frase in ['puedo comprar', 'que puedo comprar', 'puedo gastar']
        ):
            return 'presupuesto'

        if any(palabra in texto for palabra in ['comprar', 'compra', 'comprame', 'adquirir', 'agregar', 'agrega', 'anadir', 'anade']):
            return 'compra'

        if any(palabra in texto for palabra in ['catalogo', 'productos', 'ver', 'mostrar']):
            return 'catalogo'

        if any(palabra in texto for palabra in ['stock', 'existencias', 'disponible', 'tienen', 'hay']):
            return 'stock'

        if any(palabra in texto for palabra in ['cuanto', 'precio', 'cuesta', 'vale']):
            return 'producto'

        # Por defecto, asumir búsqueda de producto
        return 'producto'

    def _detectar_categoria(self, texto: str) -> Optional[str]:
        """Detecta la categoría mencionada en el texto."""
        for patron, categoria in self.patron_categoria.items():
            if re.search(patron, texto, re.IGNORECASE):
                return categoria
        return None

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        texto = unicodedata.normalize('NFD', texto.lower())
        return ''.join(
            caracter for caracter in texto
            if unicodedata.category(caracter) != 'Mn'
        )

    def _buscar_productos_consulta(
        self,
        texto: str,
        categoria: Optional[str] = None,
        coincidir_cualquier_termino: bool = False
    ) -> Tuple[List[Dict], bool]:
        """Busca por palabras del nombre, ignorando frases de cortesía e intención."""
        palabras_categoria = {
            palabra
            for patron in self.patron_categoria
            for palabra in patron.split('|')
        }
        tokens = re.findall(r'\w+', self._normalizar_texto(texto))
        terminos = [
            token for token in tokens
            if token not in self.palabras_ignoradas_busqueda
            and token not in palabras_categoria
        ]
        terminos = [
            ''.join(
                caracter for caracter in unicodedata.normalize('NFD', termino)
                if unicodedata.category(caracter) != 'Mn'
            )
            for termino in terminos
        ]

        if terminos:
            consulta = set(terminos)
            coincidencias_nombre = []
            for producto in catalogo.obtener_todos():
                nombre = self._normalizar_texto(producto['nombre'])
                palabras_nombre = set(re.findall(r'\w+', nombre))
                if consulta.issubset(palabras_nombre):
                    coincidencias_nombre.append(producto)

            if coincidencias_nombre:
                return coincidencias_nombre, True

            coincidencias = []
            for producto in catalogo.obtener_todos():
                texto_producto = self._normalizar_texto(
                    f"{producto['nombre']} {producto['descripcion']} {producto['categoria']}"
                )
                if (
                    any(termino in texto_producto for termino in terminos)
                    if coincidir_cualquier_termino
                    else all(termino in texto_producto for termino in terminos)
                ):
                    coincidencias.append(producto)
            if coincidencias:
                return coincidencias, False

        if categoria:
            return catalogo.obtener_por_categoria(categoria), False

        return [], False

    def _generar_respuesta_compra(
        self, productos: List[Dict], categoria: Optional[str], compra_directa: bool
    ) -> str:
        if compra_directa:
            producto = productos[0]
            return f"Voy a agregar **{producto['nombre']}** a tu carrito."

        if not productos:
            return "¿Qué producto quieres comprar? Escribe su nombre del catálogo, por ejemplo: MacBook Air M2."

        encabezado = "Para ayudarte a comprar, estas son las opciones disponibles"
        if categoria:
            encabezado += f" en {categoria}"
        respuesta = f"📦 {encabezado}:\n\n"
        for producto in productos[:5]:
            respuesta += (
                f"• {producto['nombre']} — ${producto['precio']:.2f} "
                f"({producto['existencias']} disponibles)\n"
            )
        respuesta += "\nEscribe el nombre del producto que quieres agregar al carrito."
        return respuesta

    def _extraer_presupuesto(self, texto: str) -> Optional[float]:
        """Extrae el presupuesto del texto."""
        coincidencias = self.patron_presupuesto.findall(texto)
        if coincidencias:
            try:
                numero = coincidencias[0]
                if ',' in numero and '.' in numero:
                    separador_decimal = ',' if numero.rfind(',') > numero.rfind('.') else '.'
                    separador_miles = '.' if separador_decimal == ',' else ','
                    numero = numero.replace(separador_miles, '').replace(separador_decimal, '.')
                elif ',' in numero or '.' in numero:
                    separador = ',' if ',' in numero else '.'
                    partes = numero.split(separador)
                    if len(partes) > 2 or len(partes[-1]) == 3:
                        numero = ''.join(partes)
                    else:
                        numero = separador.join(partes).replace(separador, '.')
                return float(numero)
            except ValueError:
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

        if presupuesto is None:
            return "¿Cuál es tu presupuesto? Por ejemplo: “Tengo 1000 dólares, ¿qué puedo comprar?”"

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
            return "¿Qué dos productos quieres comparar? Por ejemplo: “Compara iPhone y Samsung”."

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
