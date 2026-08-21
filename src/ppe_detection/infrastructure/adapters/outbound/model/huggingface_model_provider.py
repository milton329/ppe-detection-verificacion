from pathlib import Path

from huggingface_hub import hf_hub_download


class HuggingFaceModelProvider:
    """Adaptador de salida que obtiene los pesos del modelo desde Hugging Face Hub.

    Implementa `ModelProviderPort`. Usa `hf_hub_download`, que descarga el
    archivo solo la primera vez: en llamadas posteriores reutiliza la copia
    cacheada en `~/.cache/huggingface/hub/` sin volver a descargar.
    """

    def __init__(
        self,
        repo_id: str = "melihuzunoglu/ppe-detection",
        filename: str = "best.pt",
    ) -> None:
        self._repo_id = repo_id
        self._filename = filename

    def get_model_path(self) -> Path:
        local_path = hf_hub_download(repo_id=self._repo_id, filename=self._filename)
        return Path(local_path)
