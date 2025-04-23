import socket
import logging
from typing import Tuple
import time


class Vision:
    """
    A class to interface with NI Vision Builder.
    """

    def __init__(self, ip: str, port: int):
        """
        Initialize the Vision system interface.

        Establishes a TCP connection to the vision system at the specified IP and port.

        Args:
            ip (str): IP address of the vision system.
            port (int): Port number used by the vision system.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        logging.info(f"Connected to vision system at {ip}:{port}")

    def get_box_pos(self) -> Tuple[float, float, float, float]:
        """
        Receive and parse the box position from the vision system.

        Returns:
            Tuple[float, float, float, float]: A tuple containing:
                - dx (float): Displacement along the x-axis.
                - dy (float): Displacement along the y-axis.
                - theta (float): Orientation angle in radians or degrees.
                - t_initial (float): Timestamp (in seconds) at which data was received,
                                     measured using `time.perf_counter()`.
        """

        data = self.socket.recv(1024)
        t_initial = time.perf_counter()
        dx, dy, theta = map(float, data.decode("utf-8").strip().split("|"))

        return dx, dy, theta, t_initial
