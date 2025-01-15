from dataclasses import dataclass
from typing import Optional, Generic, TypeVar
import zmq
import uuid
from contextlib import contextmanager
import time

T = TypeVar('T')

@dataclass
class Response(Generic[T]):
    success: bool
    data: Optional[T]
    error: Optional[str]

class Client:
    def __init__(self, timeout: int = 5000):
        self.context = zmq.Context()
        self._socket = None
        self.timeout = timeout
        self.max_retries = 3

    @contextmanager
    def connection(self):
        try:
            socket = self.context.socket(zmq.REQ)
            socket.connect("tcp://localhost:5555")
            socket.RCVTIMEO = self.timeout
            self._socket = socket
            yield self
        finally:
            if self._socket:
                self._socket.close(linger=0)
                self._socket = None

    def send_command(self, command: str, data: dict, retry_count: int = 0) -> Response:
        if not self._socket:
            raise RuntimeError("Not connected")
            
        try:
            message = {
                command: {
                    **data,
                }
            }
            self._socket.send_json(message)
            response = self._socket.recv_json()
            return Response(**response)
            
        except zmq.Again:
            if retry_count < self.max_retries:
                time.sleep(0.1 * (retry_count + 1))
                # Reset socket state
                self._socket.close(linger=0)
                self._socket = self.context.socket(zmq.REQ)
                self._socket.connect("tcp://localhost:5555")
                self._socket.RCVTIMEO = self.timeout
                return self.send_command(command, data, retry_count + 1)
            raise TimeoutError(f"Command {command} timed out after {self.max_retries} retries")