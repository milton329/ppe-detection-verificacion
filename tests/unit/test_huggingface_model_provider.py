"""Pruebas del adaptador HuggingFaceModelProvider: nunca descarga nada real,
solo verifica que se llame correctamente a hf_hub_download."""

from pathlib import Path
from unittest.mock import patch

from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import (
    HuggingFaceModelProvider,
)

MODULE = "ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider"


@patch(f"{MODULE}.hf_hub_download")
def test_get_model_path_usa_repo_y_archivo_por_defecto(mock_download):
    mock_download.return_value = "/cache/huggingface/hub/best.pt"

    provider = HuggingFaceModelProvider()
    path = provider.get_model_path()

    mock_download.assert_called_once_with(
        repo_id="melihuzunoglu/ppe-detection", filename="best.pt"
    )
    assert path == Path("/cache/huggingface/hub/best.pt")


@patch(f"{MODULE}.hf_hub_download")
def test_get_model_path_usa_repo_y_archivo_personalizados(mock_download):
    mock_download.return_value = "/cache/otro/modelo.pt"

    provider = HuggingFaceModelProvider(repo_id="otro-usuario/otro-repo", filename="modelo.pt")
    provider.get_model_path()

    mock_download.assert_called_once_with(repo_id="otro-usuario/otro-repo", filename="modelo.pt")


@patch(f"{MODULE}.hf_hub_download")
def test_get_model_path_devuelve_un_objeto_path(mock_download):
    mock_download.return_value = "/cache/huggingface/hub/best.pt"

    provider = HuggingFaceModelProvider()
    path = provider.get_model_path()

    assert isinstance(path, Path)


@patch(f"{MODULE}.hf_hub_download")
def test_get_model_path_delega_en_download_en_cada_llamada(mock_download):
    mock_download.return_value = "/cache/huggingface/hub/best.pt"

    provider = HuggingFaceModelProvider()
    provider.get_model_path()
    provider.get_model_path()

    assert mock_download.call_count == 2
