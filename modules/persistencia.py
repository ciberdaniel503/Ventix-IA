"""
Módulo de persistencia con sincronización GitHub
Este módulo maneja la lectura/escritura de archivos JSON con respaldo automático en GitHub
para evitar pérdida de datos en Streamlit Community Cloud.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersistenciaGitHub:
    """
    Sistema de persistencia con sincronización automática a GitHub.
    Respalda automáticamente los datos JSON en un repositorio de GitHub.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Inicializa el sistema de persistencia.

        Args:
            data_dir: Directorio donde se almacenan los archivos JSON
        """
        self.data_dir = data_dir
        self.github_enabled = False
        self.github_token = None
        self.github_repo = None
        self.github_path = None

        # Intentar cargar configuración de GitHub desde secrets
        self._load_github_config()

    def _load_github_config(self):
        """Carga la configuración de GitHub desde el entorno o secrets de Streamlit."""
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO")
        self.github_path = os.getenv("GITHUB_DATA_PATH", "data")

        try:
            import streamlit as st
            from streamlit.errors import StreamlitSecretNotFoundError

            try:
                self.github_token = self.github_token or st.secrets.get("GITHUB_TOKEN")
                self.github_repo = self.github_repo or st.secrets.get("GITHUB_REPO")
                self.github_path = os.getenv("GITHUB_DATA_PATH") or st.secrets.get(
                    "GITHUB_DATA_PATH", self.github_path
                )
            except StreamlitSecretNotFoundError:
                pass
        except ImportError:
            pass

        if self.github_token and self.github_repo:
            self.github_enabled = True
            logger.info("✅ GitHub persistence habilitado")
        else:
            logger.warning("⚠️ GitHub persistence no configurado - usando almacenamiento local")

    def _get_file_path(self, filename: str) -> str:
        """Obtiene la ruta completa del archivo."""
        return os.path.join(self.data_dir, filename)

    def _read_json(self, filename: str) -> Dict:
        """Lee desde GitHub si está configurado; de lo contrario, desde el disco local."""
        if self.github_enabled:
            try:
                from github import Github, GithubException

                repo = Github(self.github_token).get_repo(self.github_repo)
                remote_path = f"{self.github_path}/{filename}".strip("/")
                try:
                    remote_file = repo.get_contents(remote_path)
                except GithubException as e:
                    if e.status != 404:
                        raise RuntimeError(f"No se pudo leer {remote_path} desde GitHub") from e
                else:
                    try:
                        return json.loads(remote_file.decoded_content.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as e:
                        raise RuntimeError(f"El archivo remoto {remote_path} no contiene JSON válido") from e
            except ImportError as e:
                raise RuntimeError("PyGithub es necesario para leer los datos compartidos") from e

        filepath = self._get_file_path(filename)

        if not os.path.exists(filepath):
            logger.warning(f"Archivo no encontrado: {filepath}, creando nuevo")
            return {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo {filename}: {e}")
            return {}

    def _write_json(self, filename: str, data: Dict) -> bool:
        """
        Escribe datos a un archivo JSON localmente.
        Si GitHub está habilitado, también hace commit al repositorio.
        """
        filepath = self._get_file_path(filename)

        try:
            # Asegurar que el directorio existe
            os.makedirs(self.data_dir, exist_ok=True)

            # Escribir localmente
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Archivo guardado localmente: {filename}")

            # Si GitHub está habilitado, el guardado remoto es parte de la operación.
            if self.github_enabled and not self._commit_to_github(filename):
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Error escribiendo {filename}: {e}")
            return False

    def _commit_to_github(self, filename: str):
        """
        Hace commit de cambios al repositorio de GitHub.
        Utiliza PyGithub para la API de GitHub.
        """
        try:
            from github import Github
            from github import GithubException

            if not self.github_enabled:
                return True

            # Conectar a GitHub
            g = Github(self.github_token)
            repo = g.get_repo(self.github_repo)

            # Leer el archivo
            filepath = self._get_file_path(filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Ruta en el repositorio
            github_file_path = f"{self.github_path}/{filename}".strip("/")

            try:
                # Intentar obtener el archivo existente
                file = repo.get_contents(github_file_path)
            except GithubException as e:
                if e.status == 404:
                    repo.create_file(
                        github_file_path,
                        f"Create {filename} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        content
                    )
                    logger.info(f"✅ Archivo creado en GitHub: {filename}")
                else:
                    raise
            else:
                repo.update_file(
                    github_file_path,
                    f"Update {filename} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    content,
                    file.sha
                )
                logger.info(f"✅ Commit exitoso a GitHub: {filename}")
            return True

        except ImportError:
            logger.warning("PyGithub no está instalado. GitHub sync no disponible.")
        except Exception as e:
            logger.error(f"❌ Error en commit a GitHub: {e}")
        return False

    def cargar_productos(self) -> List[Dict]:
        """Carga el catálogo de productos."""
        data = self._read_json("productos.json")
        return data.get("productos", [])

    def guardar_productos(self, productos: List[Dict]) -> bool:
        """Guarda el catálogo de productos."""
        data = {"productos": productos}
        return self._write_json("productos.json", data)

    def cargar_pedidos(self) -> List[Dict]:
        """Carga los pedidos."""
        data = self._read_json("pedidos.json")
        return data.get("pedidos", [])

    def guardar_pedidos(self, pedidos: List[Dict]) -> bool:
        """Guarda los pedidos."""
        data = {"pedidos": pedidos}
        return self._write_json("pedidos.json", data)

    def cargar_ventas(self) -> List[Dict]:
        """Carga el historial de ventas."""
        data = self._read_json("ventas.json")
        return data.get("ventas", [])

    def guardar_ventas(self, ventas: List[Dict]) -> bool:
        """Guarda el historial de ventas."""
        data = {"ventas": ventas}
        return self._write_json("ventas.json", data)

    def cargar_carritos(self) -> Dict:
        """Carga los carritos activos."""
        data = self._read_json("carritos.json")
        return data.get("carritos", {})

    def guardar_carritos(self, carritos: Dict) -> bool:
        """Guarda los carritos activos."""
        data = {"carritos": carritos}
        return self._write_json("carritos.json", data)

    def backup_automático(self):
        """
        Realiza un backup automático de todos los datos.
        Útil para llamarse periódicamente.
        """
        archivos = ["productos.json", "pedidos.json", "ventas.json", "carritos.json"]

        for archivo in archivos:
            filepath = self._get_file_path(archivo)
            if os.path.exists(filepath):
                self._commit_to_github(archivo)

        logger.info("🔄 Backup automático completado")


# Instancia global de persistencia
persistencia = PersistenciaGitHub()
