"""
Módulo de gestión del catálogo de productos
"""

from typing import Dict, List, Optional
from modules.persistencia import persistencia
import logging

logger = logging.getLogger(__name__)


class Catalogo:
    """Gestiona el catálogo de productos."""

    def __init__(self):
        """Inicializa el catálogo."""
        self.productos = persistencia.cargar_productos()

    def recargar(self):
        """Recarga los productos desde el almacenamiento persistente."""
        self.productos = persistencia.cargar_productos()

    def obtener_todos(self) -> List[Dict]:
        """Obtiene todos los productos."""
        return self.productos

    def obtener_por_id(self, producto_id: str) -> Optional[Dict]:
        """Obtiene un producto por su ID."""
        for producto in self.productos:
            if producto["id"] == producto_id:
                return producto
        return None

    def obtener_por_categoria(self, categoria: str) -> List[Dict]:
        """Obtiene productos de una categoría específica."""
        return [p for p in self.productos if p["categoria"] == categoria]

    def obtener_categorias(self) -> List[str]:
        """Obtiene todas las categorías únicas."""
        categorias = set(p["categoria"] for p in self.productos)
        return sorted(list(categorias))

    def buscar(self, query: str) -> List[Dict]:
        """
        Busca productos por nombre o descripción.
        Búsqueda case-insensitive.
        """
        query = query.lower()
        resultados = []

        for producto in self.productos:
            if (query in producto["nombre"].lower() or
                query in producto["descripcion"].lower() or
                query in producto["categoria"].lower()):
                resultados.append(producto)

        return resultados

    def agregar_producto(self, producto: Dict) -> bool:
        """
        Agrega un nuevo producto al catálogo.
        Genera automáticamente un ID si no se proporciona.
        """
        try:
            # Generar ID si no existe
            if "id" not in producto or not producto["id"]:
                producto["id"] = self._generar_id()

            # Validar campos requeridos
            campos_requeridos = ["id", "nombre", "categoria", "precio", "existencias", "descripcion"]
            for campo in campos_requeridos:
                if campo not in producto:
                    logger.error(f"Falta campo requerido: {campo}")
                    return False

            # Verificar que el ID sea único
            if self.obtener_por_id(producto["id"]):
                logger.error(f"ID ya existe: {producto['id']}")
                return False

            self.productos.append(producto)
            return persistencia.guardar_productos(self.productos)

        except Exception as e:
            logger.error(f"Error agregando producto: {e}")
            return False

    def editar_producto(self, producto_id: str, datos_actualizados: Dict) -> bool:
        """Edita un producto existente."""
        try:
            producto = self.obtener_por_id(producto_id)
            if not producto:
                logger.error(f"Producto no encontrado: {producto_id}")
                return False

            # Actualizar campos
            for campo, valor in datos_actualizados.items():
                if campo in producto:
                    producto[campo] = valor

            return persistencia.guardar_productos(self.productos)

        except Exception as e:
            logger.error(f"Error editando producto: {e}")
            return False

    def eliminar_producto(self, producto_id: str) -> bool:
        """Elimina un producto del catálogo."""
        try:
            producto = self.obtener_por_id(producto_id)
            if not producto:
                logger.error(f"Producto no encontrado: {producto_id}")
                return False

            self.productos.remove(producto)
            return persistencia.guardar_productos(self.productos)

        except Exception as e:
            logger.error(f"Error eliminando producto: {e}")
            return False

    def actualizar_existencias(self, producto_id: str, cantidad: int) -> bool:
        """
        Actualiza las existencias de un producto.
        cantidad puede ser positivo (agregar) o negativo (restar).
        """
        try:
            producto = self.obtener_por_id(producto_id)
            if not producto:
                logger.error(f"Producto no encontrado: {producto_id}")
                return False

            nueva_cantidad = producto["existencias"] + cantidad

            if nueva_cantidad < 0:
                logger.error(f"Existencias insuficientes para {producto_id}")
                return False

            producto["existencias"] = nueva_cantidad
            return persistencia.guardar_productos(self.productos)

        except Exception as e:
            logger.error(f"Error actualizando existencias: {e}")
            return False

    def obtener_productos_bajo_stock(self, umbral: int = 5) -> List[Dict]:
        """Obtiene productos con existencias por debajo del umbral."""
        return [p for p in self.productos if p["existencias"] <= umbral]

    def _generar_id(self) -> str:
        """Genera un ID único para un nuevo producto."""
        import random
        import string

        # Generar ID como PXXX
        numero = len(self.productos) + 1
        return f"P{numero:03d}"

    def comparar_productos(self, ids: List[str]) -> List[Dict]:
        """
        Compara múltiples productos y devuelve sus características.
        """
        productos = []
        for producto_id in ids:
            producto = self.obtener_por_id(producto_id)
            if producto:
                productos.append(producto)
        return productos

    def recomendar_por_presupuesto(self, presupuesto: float, categoria: Optional[str] = None) -> List[Dict]:
        """
        Recomienda productos dentro de un presupuesto.
        Opcionalmente filtra por categoría.
        """
        productos = self.productos

        if categoria:
            productos = self.obtener_por_categoria(categoria)

        # Filtrar por presupuesto
        recomendados = [p for p in productos if p["precio"] <= presupuesto]

        # Ordenar por precio descendente (mejor valor dentro del presupuesto)
        recomendados.sort(key=lambda x: x["precio"], reverse=True)

        return recomendados


# Instancia global del catálogo
catalogo = Catalogo()
