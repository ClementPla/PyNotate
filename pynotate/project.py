from typing import Optional
import zmq
import json
from pynotate.utils.image import encode_image_as_base64png
from pynotate.client import Client
from pathlib import Path
import shutil
import time

class Project:
    def __init__(
        self,
        project_name,
        input_dir,
        output_dir=".",
        is_segmentation: bool = False,
        is_classification: bool = False,
        is_instance_segmentation: bool = False,
        segmentation_classes = None,
        classification_classes = None,
        classification_multilabel = None,
    ):
        self.project_name = project_name
        self.input_dir = Path(input_dir)
        if(not self.input_dir.exists()):
            self.input_dir.mkdir(parents=True)
        self.output_dir = Path(output_dir)
        self.is_segmentation = (
            is_segmentation
            or is_instance_segmentation
            or (segmentation_classes is not None)
        )
        self.is_classification = is_classification or (
            classification_classes is not None
        ) or classification_multilabel is not None

        self.is_instance_segmentation = is_instance_segmentation
        self.segmentation_classes = segmentation_classes
        self.classification_classes = classification_classes

        self.config = {
            "project_name": self.project_name,
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "is_segmentation": self.is_segmentation,
            "is_classification": self.is_classification,
            "is_instance_segmentation": self.is_instance_segmentation,
            "segmentation_classes": self.segmentation_classes,
            "classification_classes": self.classification_classes,
            "classification_multilabel": classification_multilabel,
        }

        self.list_files = Path(input_dir).rglob("*.*")
        self.client = Client()


    def __enter__(self):
        with self.client.connection() as client:
            response = client.send_command("CreateProject", self.config)
            if not response.success:
                raise RuntimeError(f"Failed to create project: {response.error}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
    # def get_images(self):
    #     context = zmq.Context()
    #     socket = context.socket(zmq.REQ)
    #     socket.connect("tcp://localhost:5555")

    #     message = json.dumps({"command": "get_images", "data": {}})
    #     socket.send_string(message)

    #     response = socket.recv_string()
    #     data = json.loads(response)
    #     return data["images"]

    def load_image(
        self,
        image_path,
        segmentation_masks,
        copy_to_input_dir=True,
        segmentation_classes=None,
        multiclass_choices=None,
        multilabel_choices=None,
    ):
        if not Path(image_path).is_file():
            raise FileNotFoundError(f"File not found: {image_path}")

        if image_path not in self.list_files:
            if copy_to_input_dir:
                try:
                    shutil.copy(image_path, self.input_dir / Path(image_path).name)
                    image_path = str(self.input_dir / Path(image_path).name)
                except shutil.SameFileError:
                    print(
                        f"File {Path(image_path).name} already exists in {self.input_dir}, skipping copy"
                    )
            else:
                raise FileNotFoundError(
                    f"File not found in input_dir: {image_path} and copy_to_input_dir is set to False"
                )
        if segmentation_classes is None:
            segmentation_classes = self.segmentation_classes

        segmentation_data = [
            encode_image_as_base64png(mask) for mask in segmentation_masks
        ]
        with self.client.connection() as client:

            response = client.send_command(
                "LoadImage",
                {
                    "image_path": image_path,
                    "mask_data": segmentation_data,
                    "segmentation_classes": segmentation_classes,
                    "classification_classes": multiclass_choices,
                    "classification_multilabel": multilabel_choices,
                },
            )
            if not response.success:
                raise RuntimeError(f"Failed to load image: {response.error}")
