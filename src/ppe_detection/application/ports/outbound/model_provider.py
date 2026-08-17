from pathlib import Path
from typing import Protocol


class ModelProviderPort(Protocol):
    """Puerto de salida para obtener los pesos del modelo de detección.

    Define el contrato que necesita la aplicación sin acoplarla a un
    proveedor concreto (Hugging Face, disco local, S3, etc.). Los
    adaptadores en `infrastructure/adapters/outbound/model/` implementan
    esta interfaz.
    """

    def get_model_path(self) -> Path:
        """Devuelve la ruta local al archivo de pesos del modelo.

        Si el archivo no está disponible localmente, el adaptador es
        responsable de obtenerlo (por ejemplo, descargándolo).
        """
        ...
