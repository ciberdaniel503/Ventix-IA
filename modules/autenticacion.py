"""
Módulo de autenticación para el panel administrativo
"""

import hashlib
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class Autenticacion:
    """Sistema de autenticación simple para el panel administrativo."""

    def __init__(self):
        """Inicializa el sistema de autenticación."""
        # Usuario por defecto (se puede cambiar en configuración)
        self.usuarios = {
            "admin": {
                "password_hash": self._hash_password("admin123"),
                "nombre": "Administrador",
                "rol": "admin"
            }
        }

    def _hash_password(self, password: str) -> str:
        """Genera un hash SHA-256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()

    def verificar_credenciales(self, username: str, password: str) -> bool:
        """
        Verifica las credenciales de un usuario.
        """
        if username not in self.usuarios:
            logger.warning(f"Usuario no encontrado: {username}")
            return False

        usuario = self.usuarios[username]
        password_hash = self._hash_password(password)

        if password_hash == usuario["password_hash"]:
            logger.info(f"Autenticación exitosa: {username}")
            return True
        else:
            logger.warning(f"Contraseña incorrecta: {username}")
            return False

    def obtener_usuario(self, username: str) -> Optional[Dict]:
        """Obtiene información de un usuario."""
        return self.usuarios.get(username)

    def cambiar_password(self, username: str, password_actual: str, nuevo_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.
        """
        if username not in self.usuarios:
            return False

        if not self.verificar_credenciales(username, password_actual):
            return False

        self.usuarios[username]["password_hash"] = self._hash_password(nuevo_password)
        logger.info(f"Contraseña actualizada: {username}")
        return True


# Instancia global de autenticación
autenticacion = Autenticacion()
