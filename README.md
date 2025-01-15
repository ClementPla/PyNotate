# PyNotate

PyNotate is a Python package designed to facilitate communication with LabelMed (temporary name) from your Python code. It leverages WebSocket with ZeroMQ to send and retrieve data efficiently.

## Features

- Communicate with Annotator using WebSocket and ZeroMQ
- Send and receive data seamlessly
- Easy integration with your Python projects

## Installation

You can install PyNotate using pip:

```bash
pip install pynotate
```

## Usage

Here is a basic example of how to use PyNotate:

```python
import pynotate
import numpy as np
import cv2

img = cv2.imread('data.jpeg')


# Initialize the PyNotate client
with pynotate.conn() as cli:
    cli.display(img)


```

## Requirements

- Python 3.6+
- ZeroMQ
- WebSocket

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or issues, please open an issue on the [GitHub repository](https://github.com/yourusername/pynotate).
