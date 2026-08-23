import io

from PIL import Image
from ultralytics.engine.results import Results
from ultralytics.models.yolo.model import YOLO

from ppe_detection.application.ports.outbound.model_provider import ModelProviderPort
from ppe_detection.domain.entities.detection import Detection


class YoloDetector:
    """Adaptador de salida que ejecuta el modelo YOLO sobre una imagen.

    Implementa `DetectorPort`. El modelo se carga una sola vez (en el primer
    `detect()`) y se reutiliza en llamadas posteriores.
    """

    def __init__(self, model_provider: ModelProviderPort) -> None:
        self._model_provider = model_provider
        self._model: YOLO | None = None

    def _get_model(self) -> YOLO:
        if self._model is None:
            self._model = YOLO(self._model_provider.get_model_path())
        return self._model

    def detect(self, image_bytes: bytes, confidence: float = 0.25) -> list[Detection]:
        model = self._get_model()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        results = list(model.predict(source=image, conf=confidence, save=False, verbose=False))
        result = results[0]
        assert isinstance(result, Results), "predict sobre una imagen devuelve un Results"

        detections: list[Detection] = []
        boxes = result.boxes
        if boxes is None:
            return detections

        for i in range(len(boxes)):
            class_name = model.names[int(boxes.cls[i])]
            box_confidence = float(boxes.conf[i])
            x1, y1, x2, y2 = (float(v) for v in boxes.xyxy[i])
            detections.append(Detection(class_name, box_confidence, (x1, y1, x2, y2)))

        return detections
