"""
VENTIX AI - Panel Administrativo
Sistema inteligente de ventas mediante Telegram y Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Importar módulos
from modules.catalogo import catalogo
from modules.pedidos import gestor_pedidos
from modules.ventas import gestor_ventas
from modules.autenticacion import autenticacion
from modules.persistencia import persistencia

# Configuración de la página
st.set_page_config(
    page_title="VENTIX AI - Panel Administrativo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos CSS
def load_css():
    css_path = os.path.join("assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Sistema de autenticación
def check_authentication():
    """Verifica si el usuario está autenticado."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.session_state.show_login = True
    else:
        st.session_state.show_login = False

def login_page():
    """Página de login."""
    st.markdown("<h1>🔐 VENTIX AI - Login</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.container(border=True):
            st.markdown("### Iniciar Sesión")

            username = st.text_input("Usuario", placeholder="admin")
            password = st.text_input("Contraseña", type="password", placeholder="admin123")

            if st.button("Iniciar Sesión", use_container_width=True):
                if autenticacion.verificar_credenciales(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Autenticación exitosa")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

        st.markdown("---")
        st.info("🔑 Credenciales por defecto:\nUsuario: admin\nContraseña: admin123")

def main_app():
    """Aplicación principal."""
    # Sidebar
    with st.sidebar:
        st.markdown("### 🤖 VENTIX AI")
        st.markdown("---")

        # Usuario
        st.markdown(f"👤 **{st.session_state.username}**")
        st.markdown("---")

        # Navegación
        page = st.radio(
            "Navegación",
            ["📊 Dashboard", "📦 Productos", "🛒 Pedidos", "💰 Ventas", "⚙️ Configuración"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Información de persistencia
        if persistencia.github_enabled:
            st.success("✅ GitHub Sync: Activo")
        else:
            st.warning("⚠️ GitHub Sync: Inactivo")

        st.markdown("---")

        # Botón logout
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # Renderizar página seleccionada
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "📦 Productos":
        productos_page()
    elif page == "🛒 Pedidos":
        pedidos_page()
    elif page == "💰 Ventas":
        ventas_page()
    elif page == "⚙️ Configuración":
        configuracion_page()

def dashboard_page():
    """Página de dashboard."""
    st.markdown("<h1>📊 Dashboard</h1>", unsafe_allow_html=True)

    # Cargar estadísticas
    stats = gestor_ventas.obtener_estadisticas()
    productos = catalogo.obtener_todos()
    productos_bajo_stock = catalogo.obtener_productos_bajo_stock(umbral=5)

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Ventas",
            f"${stats['total_ventas']:.2f}",
            delta=None
        )

    with col2:
        st.metric(
            "Total Pedidos",
            stats['total_pedidos'],
            delta=None
        )

    with col3:
        st.metric(
            "Pedidos Pendientes",
            stats['pedidos_pendientes'],
            delta=None
        )

    with col4:
        st.metric(
            "Productos Disponibles",
            len(productos),
            delta=None
        )

    st.markdown("---")

    # Gráficas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Ventas por Día (Últimos 30 días)")
        ventas_por_dia = gestor_ventas.obtener_ventas_por_dia(30)

        if ventas_por_dia:
            df_ventas = pd.DataFrame(list(ventas_por_dia.items()), columns=['Fecha', 'Ventas'])
            df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha'])
            df_ventas = df_ventas.sort_values('Fecha')

            fig = px.line(
                df_ventas,
                x='Fecha',
                y='Ventas',
                title="Ventas Diarias",
                markers=True
            )
            fig.update_layout(
                plot_bgcolor='rgba(15, 15, 35, 0.8)',
                paper_bgcolor='rgba(15, 15, 35, 0.8)',
                font_color='#e8e8e8'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de ventas para mostrar")

    with col2:
        st.markdown("### 🏆 Productos Más Vendidos")
        productos_top = gestor_ventas.obtener_productos_mas_vendidos(5)

        if productos_top:
            df_top = pd.DataFrame(productos_top)

            fig = px.bar(
                df_top,
                x='nombre',
                y='cantidad_vendida',
                title="Top 5 Productos",
                color='cantidad_vendida',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                plot_bgcolor='rgba(15, 15, 35, 0.8)',
                paper_bgcolor='rgba(15, 15, 35, 0.8)',
                font_color='#e8e8e8',
                xaxis_title="",
                yaxis_title="Cantidad Vendida"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de ventas para mostrar")

    st.markdown("---")

    # Alertas de stock bajo
    if productos_bajo_stock:
        st.markdown("### ⚠️ Productos con Stock Bajo")
        with st.container(border=True):
            for producto in productos_bajo_stock:
                st.warning(f"📦 {producto['nombre']}: {producto['existencias']} unidades")
    else:
        st.success("✅ Todos los productos tienen stock suficiente")

def productos_page():
    """Página de gestión de productos."""
    st.markdown("<h1>📦 Gestión de Productos</h1>", unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Ver Productos", "➕ Agregar Producto", "✏️ Editar Producto"])

    with tab1:
        st.markdown("### Catálogo de Productos")

        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            categoria_filtro = st.selectbox(
                "Filtrar por categoría",
                ["Todas"] + catalogo.obtener_categorias()
            )
        with col2:
            busqueda = st.text_input("Buscar producto", placeholder="Nombre o descripción")

        # Filtrar productos
        productos = catalogo.obtener_todos()

        if categoria_filtro != "Todas":
            productos = catalogo.obtener_por_categoria(categoria_filtro)

        if busqueda:
            productos = catalogo.buscar(busqueda)

        # Mostrar productos
        if productos:
            df_productos = pd.DataFrame(productos)
            df_productos = df_productos[['id', 'nombre', 'categoria', 'precio', 'existencias']]
            st.dataframe(df_productos, width='stretch', hide_index=True)
        else:
            st.info("No hay productos que coincidan con los filtros")

    with tab2:
        st.markdown("### Agregar Nuevo Producto")

        with st.form("form_agregar_producto"):
            nombre = st.text_input("Nombre del producto*")
            categoria = st.selectbox(
                "Categoría*",
                catalogo.obtener_categorias() if catalogo.obtener_categorias() else ["Computadoras", "Laptops", "Celulares", "Accesorios"]
            )
            precio = st.number_input("Precio*", min_value=0.0, step=0.01)
            existencias = st.number_input("Existencias*", min_value=0, step=1)
            descripcion = st.text_area("Descripción*", height=100)

            st.markdown("### Especificaciones (opcional)")
            procesador = st.text_input("Procesador")
            ram = st.text_input("RAM")
            almacenamiento = st.text_input("Almacenamiento")
            pantalla = st.text_input("Pantalla")

            submitted = st.form_submit_button("Agregar Producto", use_container_width=True)

            if submitted:
                if nombre and categoria and precio >= 0 and existencias >= 0 and descripcion:
                    especificaciones = {}
                    if procesador:
                        especificaciones['procesador'] = procesador
                    if ram:
                        especificaciones['ram'] = ram
                    if almacenamiento:
                        especificaciones['almacenamiento'] = almacenamiento
                    if pantalla:
                        especificaciones['pantalla'] = pantalla

                    nuevo_producto = {
                        "nombre": nombre,
                        "categoria": categoria,
                        "precio": precio,
                        "existencias": existencias,
                        "descripcion": descripcion,
                        "especificaciones": especificaciones
                    }

                    if catalogo.agregar_producto(nuevo_producto):
                        st.success("✅ Producto agregado exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al agregar el producto")
                else:
                    st.error("❌ Por favor completa todos los campos obligatorios")

    with tab3:
        st.markdown("### Editar Producto")

        productos = catalogo.obtener_todos()
        if productos:
            producto_seleccionado = st.selectbox(
                "Seleccionar producto",
                options=[p['id'] for p in productos],
                format_func=lambda x: f"{x} - {catalogo.obtener_por_id(x)['nombre']}"
            )

            if producto_seleccionado:
                producto = catalogo.obtener_por_id(producto_seleccionado)

                with st.form("form_editar_producto"):
                    nombre = st.text_input("Nombre", value=producto['nombre'])
                    categoria = st.selectbox(
                        "Categoría",
                        catalogo.obtener_categorias(),
                        index=catalogo.obtener_categorias().index(producto['categoria'])
                    )
                    precio = st.number_input("Precio", value=producto['precio'], min_value=0.0, step=0.01)
                    existencias = st.number_input("Existencias", value=producto['existencias'], min_value=0, step=1)
                    descripcion = st.text_area("Descripción", value=producto['descripcion'], height=100)

                    submitted = st.form_submit_button("Actualizar Producto", use_container_width=True)

                    if submitted:
                        datos_actualizados = {
                            "nombre": nombre,
                            "categoria": categoria,
                            "precio": precio,
                            "existencias": existencias,
                            "descripcion": descripcion
                        }

                        if catalogo.editar_producto(producto_seleccionado, datos_actualizados):
                            st.success("✅ Producto actualizado exitosamente")
                            st.rerun()
                        else:
                            st.error("❌ Error al actualizar el producto")

                # Botón eliminar
                if st.button("🗑️ Eliminar Producto", type="secondary"):
                    if catalogo.eliminar_producto(producto_seleccionado):
                        st.success("✅ Producto eliminado")
                        st.rerun()
                    else:
                        st.error("❌ Error al eliminar el producto")
        else:
            st.info("No hay productos disponibles")

def pedidos_page():
    """Página de gestión de pedidos."""
    st.markdown("<h1>🛒 Gestión de Pedidos</h1>", unsafe_allow_html=True)

    if st.button("🔄 Actualizar datos", key="actualizar_pedidos"):
        st.rerun()

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "📋 Todos los Pedidos",
        "⏳ Pedidos Pendientes",
        "🛍️ Carritos Activos"
    ])

    with tab1:
        st.markdown("### Historial de Pedidos")

        pedidos = gestor_pedidos.obtener_todos_pedidos()

        if pedidos:
            df_pedidos = pd.DataFrame(pedidos)
            df_pedidos = df_pedidos[['id', 'usuario_id', 'total', 'estado', 'creado_en']]
            df_pedidos['creado_en'] = pd.to_datetime(df_pedidos['creado_en']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df_pedidos, width='stretch', hide_index=True)
        else:
            st.info("No hay pedidos registrados")

    with tab2:
        st.markdown("### Pedidos Pendientes")

        pedidos_pendientes = gestor_pedidos.obtener_pedidos_pendientes()

        if pedidos_pendientes:
            for pedido in pedidos_pendientes:
                with st.expander(f"Pedido {pedido['id']} - ${pedido['total']:.2f}"):
                    st.markdown(f"**Usuario ID:** {pedido['usuario_id']}")
                    st.markdown(f"**Fecha:** {pedido['creado_en']}")

                    st.markdown("### Items:")
                    for item in pedido['items']:
                        st.markdown(f"• {item['nombre']} x{item['cantidad']} - ${item['subtotal']:.2f}")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button(f"Procesar {pedido['id']}", key=f"proc_{pedido['id']}"):
                            if gestor_pedidos.actualizar_estado_pedido(pedido['id'], 'en_proceso'):
                                st.success("✅ Pedido en proceso")
                                st.rerun()

                    with col2:
                        if st.button(f"Enviar {pedido['id']}", key=f"env_{pedido['id']}"):
                            if gestor_pedidos.actualizar_estado_pedido(pedido['id'], 'enviado'):
                                st.success("✅ Pedido enviado")
                                st.rerun()

                    with col3:
                        if st.button(f"Entregar {pedido['id']}", key=f"ent_{pedido['id']}"):
                            if gestor_pedidos.actualizar_estado_pedido(pedido['id'], 'entregado'):
                                # Registrar venta
                                gestor_ventas.registrar_venta(pedido)
                                st.success("✅ Pedido entregado y venta registrada")
                                st.rerun()
        else:
            st.success("✅ No hay pedidos pendientes")

    with tab3:
        st.markdown("### Carritos activos de Telegram")
        carritos = gestor_pedidos.obtener_todos_carritos()
        carritos_activos = [
            (usuario_id, carrito)
            for usuario_id, carrito in carritos.items()
            if carrito.get("items")
        ]

        if carritos_activos:
            resumen_carritos = []
            for usuario_id, carrito in carritos_activos:
                items = carrito["items"]
                resumen_carritos.append({
                    "Usuario Telegram": usuario_id,
                    "Productos": len(items),
                    "Unidades": sum(item["cantidad"] for item in items),
                    "Total": sum(item["subtotal"] for item in items),
                    "Creado": carrito.get("creado_en", "")
                })

            st.dataframe(pd.DataFrame(resumen_carritos), width='stretch', hide_index=True)

            for usuario_id, carrito in carritos_activos:
                total = sum(item["subtotal"] for item in carrito["items"])
                with st.expander(f"Carrito {usuario_id} - ${total:.2f}"):
                    for item in carrito["items"]:
                        st.markdown(
                            f"• {item['nombre']} x{item['cantidad']} "
                            f"- ${item['subtotal']:.2f}"
                        )
        else:
            st.info("No hay carritos activos")

        if persistencia.github_enabled:
            st.caption("Los carritos se comparten con el bot mediante GitHub. Pulsa «Actualizar datos» para consultar los cambios recientes.")
        else:
            st.warning("GitHub Sync está inactivo. Los carritos solo están disponibles en esta instancia.")

def ventas_page():
    """Página de gestión de ventas."""
    st.markdown("<h1>💰 Gestión de Ventas</h1>", unsafe_allow_html=True)

    # Resumen mensual
    resumen = gestor_ventas.obtener_resumen_mensual()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            f"Ventas {resumen['mes']}",
            f"${resumen['total_ventas']:.2f}",
            delta=None
        )

    with col2:
        st.metric(
            "Cantidad de Ventas",
            resumen['cantidad_ventas'],
            delta=None
        )

    with col3:
        st.metric(
            "Ticket Promedio",
            f"${resumen['ticket_promedio']:.2f}",
            delta=None
        )

    st.markdown("---")

    # Historial de ventas
    st.markdown("### Historial de Ventas")

    ventas = gestor_ventas.obtener_todas_ventas()

    if ventas:
        df_ventas = pd.DataFrame(ventas)
        df_ventas = df_ventas[['id', 'usuario_id', 'total', 'fecha']]
        df_ventas['fecha'] = pd.to_datetime(df_ventas['fecha']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(df_ventas, width='stretch', hide_index=True)
    else:
        st.info("No hay ventas registradas")

    st.markdown("---")

    # Productos más vendidos
    st.markdown("### 🏆 Productos Más Vendidos")

    productos_top = gestor_ventas.obtener_productos_mas_vendidos(10)

    if productos_top:
        df_top = pd.DataFrame(productos_top)
        st.dataframe(df_top, width='stretch', hide_index=True)
    else:
        st.info("No hay datos de ventas para mostrar")

def configuracion_page():
    """Página de configuración."""
    st.markdown("<h1>⚙️ Configuración</h1>", unsafe_allow_html=True)

    st.markdown("### Información del Sistema")

    with st.container(border=True):
        st.markdown(f"**Estado de Persistencia GitHub:**")
        if persistencia.github_enabled:
            st.success("✅ Activo - Los datos se sincronizan automáticamente")
            st.info(f"📁 Repositorio: {persistencia.github_repo}")
            st.info(f"📂 Ruta datos: {persistencia.github_path}")
        else:
            st.warning("⚠️ Inactivo - Los datos solo se guardan localmente")
            st.error("⚠️ ADVERTENCIA: En Streamlit Community Cloud, los datos locales pueden perderse al reiniciar la aplicación.")
            st.markdown("""
            **Para activar GitHub Sync:**

            1. Crea un repositorio en GitHub
            2. Agrega los siguientes secrets en Streamlit Community Cloud:
               - `GITHUB_TOKEN`: Tu token de acceso personal de GitHub
               - `GITHUB_REPO`: `usuario/nombre-repositorio`
               - `GITHUB_DATA_PATH`: `data` (opcional, valor por defecto)

            3. Esto garantizará que tus datos persistan incluso si la aplicación se reinicia.
            """)

    st.markdown("---")

    st.markdown("### Información del Negocio")

    with st.form("form_info_negocio"):
        nombre_negocio = st.text_input("Nombre del negocio", value="VENTIX AI")
        telefono = st.text_input("Teléfono", value="+1 234 567 890")
        email = st.text_input("Email", value="soporte@ventix.ai")

        st.form_submit_button("Guardar Configuración", use_container_width=True)

    st.markdown("---")

    st.markdown("### Gestión de Cuentas")

    with st.container(border=True):
        st.markdown("**Cambiar Contraseña**")

        username = st.text_input("Usuario", value="admin")
        password_actual = st.text_input("Contraseña actual", type="password")
        nuevo_password = st.text_input("Nueva contraseña", type="password")

        if st.button("Actualizar Contraseña", use_container_width=True):
            if autenticacion.cambiar_password(username, password_actual, nuevo_password):
                st.success("✅ Contraseña actualizada")
            else:
                st.error("❌ Error al actualizar la contraseña")

# Función principal
def main():
    """Función principal de la aplicación."""
    check_authentication()

    if st.session_state.show_login:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
