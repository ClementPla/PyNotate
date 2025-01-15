import cv2
import base64
import numpy as np
from pathlib import Path
from typing import Union


def encode_image_as_base64png(image: np.ndarray) -> str:
    image = (image > 0).astype(np.uint8) * 255
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    if len(image.shape) == 2:
        image = np.stack([image, mask, mask, image], axis=-1)
    elif image.shape[-1] == 1:
        image = np.concatenate([image, mask, mask, image], axis=-1)

    elif image.shape[-1] == 3:
        alpha = np.any(image < 255, axis=-1)
        alpha = alpha[..., np.newaxis].astype(np.uint8) * 255
        image = np.concatenate([image, alpha], axis=-1)

    _, buffer = cv2.imencode(".png", image)

    encoded = "data:image/png;base64," + base64.b64encode(buffer).decode("utf-8")
    return encoded


def save_image(image: np.ndarray, filepath: Union[str, Path], normalize: bool = True):
    filepath = str(filepath)
    if normalize:
        image = (image - image.min()) / (image.max() - image.min()) * 255
    image = image.astype(np.uint8)
    cv2.imwrite(filepath, image[:, :, ::-1])
    return filepath
