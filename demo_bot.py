"""
Script de demostración para el bot de VENTIX AI
Simula interacciones con el bot sin necesidad de Telegram
"""

from modules.telegram_handler import telegram_handler
from modules.inteligencia import inteligencia
from modules.catalogo import catalogo
from modules.pedidos import gestor_pedidos

def demo_conversacion_bot():
    """Simula una conversación completa con el bot."""

    print("=" * 60)
    print("VENTIX AI - Demo de Conversacion con Cliente")
    print("=" * 60)
    print()

    # Simular usuario
    user_id = "demo_user_123"

    # 1. Cliente inicia conversación
    print("CLIENTE: /start")
    print()
    respuesta = telegram_handler._comando_start(user_id)
    print(f"BOT: {respuesta}")
    print()
    print("-" * 60)
    print()

    # 2. Cliente pide ayuda
    print("CLIENTE: ¿Qué puedes hacer?")
    print()
    resultado = inteligencia.procesar_consulta("¿Qué puedes hacer?")
    print(f"BOT: {resultado['respuesta']}")
    print()
    print("-" * 60)
    print()

    # 3. Cliente busca laptops
    print("CLIENTE: Muéstrame las laptops")
    print()
    resultado = inteligencia.procesar_consulta("Muéstrame las laptops")
    print(f"BOT: {resultado['respuesta']}")
    print()
    print("-" * 60)
    print()

    # 4. Cliente pregunta por presupuesto
    print("CLIENTE: Tengo un presupuesto de $1000, ¿qué laptops me recomiendas?")
    print()
    resultado = inteligencia.procesar_consulta("Tengo un presupuesto de $1000, ¿qué laptops me recomiendas?")
    print(f"BOT: {resultado['respuesta']}")
    print()
    print("-" * 60)
    print()

    # 5. Cliente agrega producto al carrito
    print("CLIENTE: Quiero agregar la MacBook Air M2 al carrito")
    print()
    producto = catalogo.obtener_por_id("P002")  # MacBook Air M2
    if producto:
        respuesta = telegram_handler.agregar_producto_carrito(user_id, "P002", 1)
        print(f"BOT: {respuesta}")
    print()
    print("-" * 60)
    print()

    # 6. Cliente agrega otro producto
    print("CLIENTE: Agrega también el teclado mecánico")
    print()
    respuesta = telegram_handler.agregar_producto_carrito(user_id, "P007", 1)
    print(f"BOT: {respuesta}")
    print()
    print("-" * 60)
    print()

    # 7. Cliente consulta su carrito
    print("CLIENTE: /carrito")
    print()
    respuesta = telegram_handler._comando_carrito(user_id)
    print(f"BOT: {respuesta}")
    print()
    print("-" * 60)
    print()

    # 8. Cliente pregunta por stock
    print("CLIENTE: ¿Tienen stock de celulares?")
    print()
    resultado = inteligencia.procesar_consulta("¿Tienen stock de celulares?")
    print(f"BOT: {resultado['respuesta']}")
    print()
    print("-" * 60)
    print()

    # 9. Cliente compara productos
    print("CLIENTE: Compara el iPhone 15 Pro con el Samsung Galaxy S24")
    print()
    resultado = inteligencia.procesar_consulta("Compara el iPhone 15 Pro con el Samsung Galaxy S24")
    print(f"BOT: {resultado['respuesta']}")
    print()
    print("-" * 60)
    print()

    # 10. Cliente pregunta precio específico
    print("CLIENTE: ¿Cuánto cuesta el monitor LG?")
    print()
    resultado = inteligencia.procesar_consulta("¿Cuánto cuesta el monitor LG?")
    print(f"BOT: {resultado['respuesta']}")
    print()
    print("-" * 60)
    print()

    # 11. Cliente quiere contacto humano
    print("CLIENTE: /contactar")
    print()
    respuesta = telegram_handler._comando_contactar()
    print(f"BOT: {respuesta}")
    print()
    print("-" * 60)
    print()

    print("=" * 60)
    print("Fin de la demo")
    print("=" * 60)


def demo_flujo_pedido_completo():
    """Simula el flujo completo de un pedido."""

    print("\n" + "=" * 60)
    print("VENTIX AI - Demo de Flujo de Pedido Completo")
    print("=" * 60)
    print()

    user_id = "demo_user_456"

    # 1. Usuario busca productos
    print("CLIENTE: Quiero ver celulares")
    print()
    resultado = inteligencia.procesar_consulta("Quiero ver celulares")
    print(f"BOT: {resultado['respuesta']}")
    print()

    # 2. Usuario agrega al carrito
    print("CLIENTE: Agregar iPhone 15 Pro al carrito")
    telegram_handler.agregar_producto_carrito(user_id, "P004", 1)
    print("BOT: iPhone 15 Pro agregado al carrito (1 unidad/es).")
    print()

    # 3. Usuario agrega más productos
    print("CLIENTE: Agregar también el Samsung Galaxy S24")
    telegram_handler.agregar_producto_carrito(user_id, "P005", 1)
    print("BOT: Samsung Galaxy S24 agregado al carrito (1 unidad/es).")
    print()

    # 4. Usuario ve el carrito
    print("CLIENTE: /carrito")
    print()
    respuesta = telegram_handler._comando_carrito(user_id)
    print(f"BOT: {respuesta}")
    print()

    # 5. Usuario crea pedido (simulado)
    print("CLIENTE: Quiero confirmar mi pedido")
    print()
    carrito = gestor_pedidos.obtener_carrito(user_id)
    if carrito and carrito['items']:
        informacion_cliente = {
            "nombre": "Cliente Demo",
            "email": "demo@example.com",
            "telefono": "+1234567890"
        }
        pedido = gestor_pedidos.crear_pedido(user_id, informacion_cliente)

        if pedido:
            print(f"BOT: Pedido creado exitosamente")
            print(f"ID del pedido: {pedido['id']}")
            print(f"Total: ${pedido['total']:.2f}")
            print(f"Items: {len(pedido['items'])} productos")
            print()
            print("Resumen del pedido:")
            for item in pedido['items']:
                print(f"   - {item['nombre']} x{item['cantidad']} - ${item['subtotal']:.2f}")
        else:
            print("BOT: No se pudo crear el pedido")
    print()

    print("=" * 60)
    print("Flujo de pedido completado")
    print("=" * 60)


def demo_inteligencia_ia():
    """Prueba las capacidades de IA del bot."""

    print("\n" + "=" * 60)
    print("VENTIX AI - Demo de Inteligencia Artificial")
    print("=" * 60)
    print()

    consultas = [
        "Necesito una computadora barata",
        "¿Qué laptops tienes menos de $1000?",
        "Muéstrame accesorios",
        "Compara HP Pavilion con MacBook Air",
        "¿Cuánto cuesta el iPhone?",
        "Tengo $500, ¿qué me recomiendas?",
        "¿Tienen stock de monitores?",
        "Voy a comprar un celular"
    ]

    for consulta in consultas:
        print(f"CLIENTE: {consulta}")
        resultado = inteligencia.procesar_consulta(consulta)
        print(f"INTENCION DETECTADA: {resultado['intencion']}")
        print(f"RESPUESTA: {resultado['respuesta'][:200]}...")
        print("-" * 60)
        print()


if __name__ == "__main__":
    print("\n" + "=" * 30)
    print("INICIANDO DEMO DEL BOT VENTIX AI")
    print("=" * 30)
    print()

    # Ejecutar demos
    demo_conversacion_bot()
    demo_flujo_pedido_completo()
    demo_inteligencia_ia()

    print("\n" + "=" * 30)
    print("DEMO COMPLETADA EXITOSAMENTE")
    print("=" * 30)
