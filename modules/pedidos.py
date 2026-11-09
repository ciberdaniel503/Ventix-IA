"""
Módulo de gestión de pedidos y carritos
"""

from typing import Dict, List, Optional
from datetime import datetime
from modules.persistencia import persistencia
from modules.catalogo import catalogo
import logging

logger = logging.getLogger(__name__)


class GestorPedidos:
    """Gestiona pedidos y carritos de compras."""

    def __init__(self):
        """Inicializa el gestor de pedidos."""
        self.pedidos = persistencia.cargar_pedidos()
        self.carritos = persistencia.cargar_carritos()

    def _recargar_pedidos(self):
        self.pedidos = persistencia.cargar_pedidos()

    def _recargar_carritos(self):
        self.carritos = persistencia.cargar_carritos()

    def crear_carrito(self, usuario_id: str) -> Dict:
        """Crea un nuevo carrito para un usuario."""
        self._recargar_carritos()
        if usuario_id not in self.carritos:
            self.carritos[usuario_id] = {
                "usuario_id": usuario_id,
                "items": [],
                "creado_en": datetime.now().isoformat()
            }
            persistencia.guardar_carritos(self.carritos)
            logger.info(f"Carrito creado para usuario {usuario_id}")

        return self.carritos[usuario_id]

    def obtener_carrito(self, usuario_id: str) -> Optional[Dict]:
        """Obtiene el carrito de un usuario."""
        self._recargar_carritos()
        return self.carritos.get(usuario_id)

    def obtener_todos_carritos(self) -> Dict:
        """Obtiene los carritos activos desde el almacenamiento compartido."""
        self._recargar_carritos()
        return self.carritos

    def agregar_al_carrito(self, usuario_id: str, producto_id: str, cantidad: int = 1) -> bool:
        """
        Agrega un producto al carrito de un usuario.
        """
        try:
            self._recargar_carritos()

            # Verificar producto existe
            producto = catalogo.obtener_por_id(producto_id)
            if not producto:
                logger.error(f"Producto no encontrado: {producto_id}")
                return False

            # Verificar existencias
            if producto["existencias"] < cantidad:
                logger.error(f"Existencias insuficientes para {producto_id}")
                return False

            # Crear carrito si no existe
            if usuario_id not in self.carritos:
                self.carritos[usuario_id] = {
                    "usuario_id": usuario_id,
                    "items": [],
                    "creado_en": datetime.now().isoformat()
                }

            carrito = self.carritos[usuario_id]

            # Verificar si el producto ya está en el carrito
            for item in carrito["items"]:
                if item["producto_id"] == producto_id:
                    item["cantidad"] += cantidad
                    item["subtotal"] = item["cantidad"] * producto["precio"]
                    if not persistencia.guardar_carritos(self.carritos):
                        return False
                    logger.info(f"Cantidad actualizada en carrito: {producto_id}")
                    return True

            # Agregar nuevo item
            carrito["items"].append({
                "producto_id": producto_id,
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "cantidad": cantidad,
                "subtotal": cantidad * producto["precio"]
            })

            if not persistencia.guardar_carritos(self.carritos):
                return False
            logger.info(f"Producto agregado al carrito: {producto_id}")
            return True

        except Exception as e:
            logger.error(f"Error agregando al carrito: {e}")
            return False

    def eliminar_del_carrito(self, usuario_id: str, producto_id: str) -> bool:
        """Elimina un producto del carrito."""
        try:
            self._recargar_carritos()
            if usuario_id not in self.carritos:
                logger.error(f"Carrito no encontrado para usuario {usuario_id}")
                return False

            carrito = self.carritos[usuario_id]
            carrito["items"] = [item for item in carrito["items"] if item["producto_id"] != producto_id]

            if not persistencia.guardar_carritos(self.carritos):
                return False
            logger.info(f"Producto eliminado del carrito: {producto_id}")
            return True

        except Exception as e:
            logger.error(f"Error eliminando del carrito: {e}")
            return False

    def actualizar_cantidad_carrito(self, usuario_id: str, producto_id: str, cantidad: int) -> bool:
        """Actualiza la cantidad de un producto en el carrito."""
        try:
            self._recargar_carritos()
            if usuario_id not in self.carritos:
                return False

            carrito = self.carritos[usuario_id]

            for item in carrito["items"]:
                if item["producto_id"] == producto_id:
                    producto = catalogo.obtener_por_id(producto_id)

                    if cantidad <= 0:
                        # Eliminar si cantidad es 0 o negativa
                        return self.eliminar_del_carrito(usuario_id, producto_id)

                    if producto["existencias"] < cantidad:
                        logger.error(f"Existencias insuficientes")
                        return False

                    item["cantidad"] = cantidad
                    item["subtotal"] = cantidad * item["precio"]
                    return persistencia.guardar_carritos(self.carritos)

            return False

        except Exception as e:
            logger.error(f"Error actualizando cantidad: {e}")
            return False

    def vaciar_carrito(self, usuario_id: str) -> bool:
        """Vacía el carrito de un usuario."""
        try:
            self._recargar_carritos()
            if usuario_id in self.carritos:
                self.carritos[usuario_id]["items"] = []
                if not persistencia.guardar_carritos(self.carritos):
                    return False
                logger.info(f"Carrito vaciado para usuario {usuario_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error vaciando carrito: {e}")
            return False

    def calcular_total_carrito(self, usuario_id: str) -> float:
        """Calcula el total del carrito de un usuario."""
        carrito = self.obtener_carrito(usuario_id)
        if not carrito:
            return 0.0

        return sum(item["subtotal"] for item in carrito["items"])

    def crear_pedido(self, usuario_id: str, informacion_cliente: Dict) -> Optional[Dict]:
        """
        Crea un pedido a partir del carrito de un usuario.
        """
        try:
            carrito = self.obtener_carrito(usuario_id)
            if not carrito or not carrito["items"]:
                logger.error(f"Carrito vacío para usuario {usuario_id}")
                return None

            # Verificar existencias de todos los productos
            for item in carrito["items"]:
                producto = catalogo.obtener_por_id(item["producto_id"])
                if producto["existencias"] < item["cantidad"]:
                    logger.error(f"Existencias insuficientes para {item['producto_id']}")
                    return None

            # Generar ID del pedido con la lista compartida más reciente.
            self._recargar_pedidos()
            pedido_id = self._generar_pedido_id()

            # Crear pedido
            pedido = {
                "id": pedido_id,
                "usuario_id": usuario_id,
                "cliente": informacion_cliente,
                "items": carrito["items"].copy(),
                "total": self.calcular_total_carrito(usuario_id),
                "estado": "pendiente",
                "creado_en": datetime.now().isoformat(),
                "actualizado_en": datetime.now().isoformat()
            }

            # Actualizar existencias
            for item in carrito["items"]:
                catalogo.actualizar_existencias(item["producto_id"], -item["cantidad"])

            # Guardar pedido
            self.pedidos.append(pedido)
            if not persistencia.guardar_pedidos(self.pedidos):
                return None

            # Vaciar carrito
            self.vaciar_carrito(usuario_id)

            logger.info(f"Pedido creado: {pedido_id}")
            return pedido

        except Exception as e:
            logger.error(f"Error creando pedido: {e}")
            return None

    def obtener_pedido(self, pedido_id: str) -> Optional[Dict]:
        """Obtiene un pedido por su ID."""
        self._recargar_pedidos()
        for pedido in self.pedidos:
            if pedido["id"] == pedido_id:
                return pedido
        return None

    def obtener_pedidos_usuario(self, usuario_id: str) -> List[Dict]:
        """Obtiene todos los pedidos de un usuario."""
        self._recargar_pedidos()
        return [p for p in self.pedidos if p["usuario_id"] == usuario_id]

    def obtener_todos_pedidos(self) -> List[Dict]:
        """Obtiene todos los pedidos."""
        self._recargar_pedidos()
        return self.pedidos

    def actualizar_estado_pedido(self, pedido_id: str, nuevo_estado: str) -> bool:
        """
        Actualiza el estado de un pedido.
        Estados posibles: pendiente, en_proceso, enviado, entregado, cancelado
        """
        try:
            pedido = self.obtener_pedido(pedido_id)
            if not pedido:
                logger.error(f"Pedido no encontrado: {pedido_id}")
                return False

            estados_validos = ["pendiente", "en_proceso", "enviado", "entregado", "cancelado"]
            if nuevo_estado not in estados_validos:
                logger.error(f"Estado inválido: {nuevo_estado}")
                return False

            pedido["estado"] = nuevo_estado
            pedido["actualizado_en"] = datetime.now().isoformat()

            if not persistencia.guardar_pedidos(self.pedidos):
                return False
            logger.info(f"Estado actualizado: {pedido_id} -> {nuevo_estado}")
            return True

        except Exception as e:
            logger.error(f"Error actualizando estado: {e}")
            return False

    def obtener_pedidos_pendientes(self) -> List[Dict]:
        """Obtiene pedidos pendientes."""
        self._recargar_pedidos()
        return [p for p in self.pedidos if p["estado"] == "pendiente"]

    def _generar_pedido_id(self) -> str:
        """Genera un ID único para un pedido."""
        import random
        import string

        # Generar ID como ORD-XXXXX
        numero = len(self.pedidos) + 1
        return f"ORD-{numero:05d}"


# Instancia global del gestor de pedidos
gestor_pedidos = GestorPedidos()
