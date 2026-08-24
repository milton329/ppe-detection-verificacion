"""Pruebas del adaptador YoloDetector: aísla la lógica de mapeo de resultados
del modelo real, sustituyendo YOLO y la clase Results de ultralytics."""

from unittest.mock import patch

import pytest

from ppe_detection.infrastructure.adapters.outbound.model.yolo_detector import YoloDetector


class FakeModelProvider:
    """Sustituto de ModelProviderPort con una ruta fija."""

    def __init__(self, path: str = "fake/model/best.pt") -> None:
        self.path = path

    def get_model_path(self) -> str:
        return self.path


class FakeBoxes:
    """Sustituto de `ultralytics.engine.results.Boxes` con acceso indexado
    a clase, confianza y coordenadas, igual que el objeto real."""

    def __init__(self, entries: list[tuple[int, float, tuple[float, float, float, float]]]) -> None:
        self._entries = entries

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def cls(self):
        return [e[0] for e in self._entries]

    @property
    def conf(self):
        return [e[1] for e in self._entries]

    @property
    def xyxy(self):
        return [e[2] for e in self._entries]


class FakeResult:
    """Sustituto de `ultralytics.engine.results.Results`."""

    def __init__(self, boxes: FakeBoxes | None) -> None:
        self.boxes = boxes


@pytest.fixture
def patched_yolo():
    """Reemplaza YOLO y Results dentro del módulo bajo prueba, para que
    YoloDetector nunca toque el modelo real ni descargue nada."""
    with (
        patch("ppe_detection.infrastructure.adapters.outbound.model.yolo_detector.YOLO") as mock_yolo_cls,
        patch("ppe_detection.infrastructure.adapters.outbound.model.yolo_detector.Results", FakeResult),
        patch("ppe_detection.infrastructure.adapters.outbound.model.yolo_detector.Image") as mock_image,
    ):
        mock_image.open.return_value.convert.return_value = "imagen-convertida"
        yield mock_yolo_cls


def test_detect_mapea_boxes_a_entidades_detection(patched_yolo):
    mock_model = patched_yolo.return_value
    mock_model.names = {0: "human", 1: "helmet"}
    boxes = FakeBoxes(
        [
            (0, 0.88, (100.0, 20.0, 200.0, 300.0)),
            (1, 0.91, (112.4, 40.2, 188.0, 121.7)),
        ]
    )
    mock_model.predict.return_value = [FakeResult(boxes)]

    detector = YoloDetector(FakeModelProvider())
    detections = detector.detect(b"bytes-imagen", confidence=0.3)

    assert len(detections) == 2
    assert detections[0].class_name == "human"
    assert detections[0].confidence == pytest.approx(0.88)
    assert detections[0].bbox == (100.0, 20.0, 200.0, 300.0)
    assert detections[1].class_name == "helmet"
    assert detections[1].confidence == pytest.approx(0.91)


def test_detect_devuelve_lista_vacia_cuando_no_hay_boxes(patched_yolo):
    mock_model = patched_yolo.return_value
    mock_model.names = {}
    mock_model.predict.return_value = [FakeResult(boxes=None)]

    detector = YoloDetector(FakeModelProvider())
    detections = detector.detect(b"bytes-imagen")

    assert detections == []


def test_detect_devuelve_lista_vacia_cuando_boxes_esta_vacio(patched_yolo):
    mock_model = patched_yolo.return_value
    mock_model.names = {}
    mock_model.predict.return_value = [FakeResult(boxes=FakeBoxes([]))]

    detector = YoloDetector(FakeModelProvider())
    detections = detector.detect(b"bytes-imagen")

    assert detections == []


def test_detect_pasa_el_umbral_de_confianza_al_predict(patched_yolo):
    mock_model = patched_yolo.return_value
    mock_model.names = {}
    mock_model.predict.return_value = [FakeResult(boxes=FakeBoxes([]))]

    detector = YoloDetector(FakeModelProvider())
    detector.detect(b"bytes-imagen", confidence=0.65)

    _, kwargs = mock_model.predict.call_args
    assert kwargs["conf"] == pytest.approx(0.65)


def test_detect_usa_025_como_confianza_por_defecto(patched_yolo):
    mock_model = patched_yolo.return_value
    mock_model.names = {}
    mock_model.predict.return_value = [FakeResult(boxes=FakeBoxes([]))]

    detector = YoloDetector(FakeModelProvider())
    detector.detect(b"bytes-imagen")

    _, kwargs = mock_model.predict.call_args
    assert kwargs["conf"] == pytest.approx(0.25)


def test_modelo_se_carga_una_sola_vez_entre_llamadas(patched_yolo):
    mock_model = patched_yolo.return_value
    mock_model.names = {}
    mock_model.predict.return_value = [FakeResult(boxes=FakeBoxes([]))]

    detector = YoloDetector(FakeModelProvider())
    detector.detect(b"primera-llamada")
    detector.detect(b"segunda-llamada")

    patched_yolo.assert_called_once()


def test_detect_usa_la_ruta_que_entrega_el_model_provider(patched_yolo):
    mock_model = patched_yolo.return_value
    mock_model.names = {}
    mock_model.predict.return_value = [FakeResult(boxes=FakeBoxes([]))]
    provider = FakeModelProvider(path="ruta/personalizada/pesos.pt")

    detector = YoloDetector(provider)
    detector.detect(b"bytes-imagen")

    patched_yolo.assert_called_once_with("ruta/personalizada/pesos.pt")
