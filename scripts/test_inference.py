"""Pruebas iniciales de inferencia sobre la imagen de referencia del modelo
melihuzunoglu/ppe-detection, para comparar detecciones a distintos umbrales
de confianza y elegir uno adecuado para casco y chaleco."""

from pathlib import Path

from huggingface_hub import hf_hub_download
from ultralytics.engine.results import Results
from ultralytics.models.yolo.model import YOLO

from ppe_detection.infrastructure.adapters.outbound.model.huggingface_model_provider import (
    HuggingFaceModelProvider,
)

REPO_ID = "melihuzunoglu/ppe-detection"
THRESHOLDS = [0.15, 0.25, 0.35, 0.5]
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "inference_output"


def main() -> None:
    model_path = HuggingFaceModelProvider(repo_id=REPO_ID).get_model_path()
    image_path = hf_hub_download(repo_id=REPO_ID, filename="sample_image.jpg")
    model = YOLO(model_path)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for conf in THRESHOLDS:
        results = list(
            model.predict(
                source=image_path,
                conf=conf,
                save=True,
                project=str(OUTPUT_DIR),
                name=f"conf_{conf}",
                exist_ok=True,
            )
        )
        result = results[0]
        assert isinstance(result, Results), "predict sobre una imagen devuelve un Results"
        print(f"\n--- Umbral de confianza: {conf} ---")
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            print("Sin detecciones")
            continue
        for i in range(len(boxes)):
            cls_name = model.names[int(boxes.cls[i])]
            confidence = float(boxes.conf[i])
            print(f"{cls_name}: {confidence:.2f}")


if __name__ == "__main__":
    main()
