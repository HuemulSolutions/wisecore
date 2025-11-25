from abc import ABC, abstractmethod
from typing import Optional


class BaseMailProvider(ABC):
    """
    Clase base abstracta para proveedores de correo electrónico.
    Define la interfaz común para enviar códigos de verificación.
    """
    
    @abstractmethod
    def send_verification_code(self, to_email: str, verification_code: str, **kwargs) -> bool:
        """
        Envía un código de verificación por correo electrónico.
        
        Args:
            to_email (str): Dirección de correo del destinatario
            verification_code (str): Código de verificación a enviar
            **kwargs: Parámetros adicionales específicos del proveedor
            
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario
            
        Raises:
            NotImplementedError: Debe ser implementado por las clases hijas
        """
        raise NotImplementedError("El método send_verification_code debe ser implementado por la clase hija")