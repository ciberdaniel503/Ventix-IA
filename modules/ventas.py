"""
Módulo de gestión de ventas y estadísticas
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from modules.persistencia import persistencia
from modules.pedidos import gestor_pedidos
import logging

logger = logging.getLogger(__name__)


class GestorVentas:
    """Gestiona el historial de ventas y estadísticas."""

    def __init__(self):
        """Inicializa el gestor de ventas."""
        self.ventas = persistencia.cargar_ventas()

    def registrar_venta(self, pedido: Dict) -> bool:
        """
        Registra una venta a partir de un pedido completado.
        """
        try:
            venta = {
                "id": pedido["id"],
                "pedido_id": pedido["id"],
                "usuario_id": pedido["usuario_id"],
                "items": pedido["items"].copy(),
                "total": pedido["total"],
                "fecha": datetime.now().isoformat(),
                "metodo_pago": pedido.get("metodo_pago", "no especificado")
            }

            self.ventas.append(venta)
            persistencia.guardar_ventas(self.ventas)

            logger.info(f"Venta registrada: {venta['id']}")
            return True

        except Exception as e:
            logger.error(f"Error registrando venta: {e}")
            return False

    def obtener_todas_ventas(self) -> List[Dict]:
        """Obtiene todas las ventas."""
        return self.ventas

    def obtener_ventas_por_periodo(self, dias: int = 30) -> List[Dict]:
        """
        Obtiene ventas de los últimos N días.
        """
        fecha_limite = datetime.now() - timedelta(days=dias)

        ventas_filtradas = []
        for venta in self.ventas:
            fecha_venta = datetime.fromisoformat(venta["fecha"])
            if fecha_venta >= fecha_limite:
                ventas_filtradas.append(venta)

        return ventas_filtradas

    def obtener_total_ventas(self) -> float:
        """Calcula el total de todas las ventas."""
        return sum(venta["total"] for venta in self.ventas)

    def obtener_total_ventas_periodo(self, dias: int = 30) -> float:
        """Calcula el total de ventas de los últimos N días."""
        ventas_periodo = self.obtener_ventas_por_periodo(dias)
        return sum(venta["total"] for venta in ventas_periodo)

    def obtener_productos_mas_vendidos(self, limite: int = 10) -> List[Dict]:
        """
        Obtiene los productos más vendidos.
        """
        conteo_productos = {}

        for venta in self.ventas:
            for item in venta["items"]:
                producto_id = item["producto_id"]
                nombre = item["nombre"]
                cantidad = item["cantidad"]

                if producto_id not in conteo_productos:
                    conteo_productos[producto_id] = {
                        "producto_id": producto_id,
                        "nombre": nombre,
                        "cantidad_vendida": 0,
                        "total_ingresos": 0.0
                    }

                conteo_productos[producto_id]["cantidad_vendida"] += cantidad
                conteo_productos[producto_id]["total_ingresos"] += item["subtotal"]

        # Ordenar por cantidad vendida
        productos_ordenados = sorted(
            conteo_productos.values(),
            key=lambda x: x["cantidad_vendida"],
            reverse=True
        )

        return productos_ordenados[:limite]

    def obtener_ventas_por_dia(self, dias: int = 30) -> Dict[str, float]:
        """
        Obtiene las ventas agrupadas por día.
        """
        ventas_por_dia = {}

        for venta in self.ventas:
            fecha = datetime.fromisoformat(venta["fecha"]).strftime("%Y-%m-%d")
            if fecha not in ventas_por_dia:
                ventas_por_dia[fecha] = 0.0
            ventas_por_dia[fecha] += venta["total"]

        # Filtrar últimos N días
        fecha_limite = datetime.now() - timedelta(days=dias)
        ventas_filtradas = {
            fecha: total
            for fecha, total in ventas_por_dia.items()
            if datetime.strptime(fecha, "%Y-%m-%d") >= fecha_limite
        }

        return ventas_filtradas

    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas generales de ventas.
        """
        pedidos = gestor_pedidos.obtener_todos_pedidos()

        total_ventas = self.obtener_total_ventas()
        total_pedidos = len(pedidos)
        pedidos_pendientes = len([p for p in pedidos if p["estado"] == "pendiente"])
        pedidos_completados = len([p for p in pedidos if p["estado"] == "entregado"])

        return {
            "total_ventas": total_ventas,
            "total_pedidos": total_pedidos,
            "pedidos_pendientes": pedidos_pendientes,
            "pedidos_completados": pedidos_completados,
            "ticket_promedio": total_ventas / total_pedidos if total_pedidos > 0 else 0.0
        }

    def obtener_resumen_mensual(self) -> Dict:
        """
        Obtiene un resumen de ventas del mes actual.
        """
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        ventas_mes = []
        for venta in self.ventas:
            fecha_venta = datetime.fromisoformat(venta["fecha"])
            if fecha_venta >= inicio_mes:
                ventas_mes.append(venta)

        total = sum(v["total"] for v in ventas_mes)
        cantidad = len(ventas_mes)

        return {
            "mes": hoy.strftime("%B %Y"),
            "total_ventas": total,
            "cantidad_ventas": cantidad,
            "ticket_promedio": total / cantidad if cantidad > 0 else 0.0
        }


# Instancia global del gestor de ventas
gestor_ventas = GestorVentas()
