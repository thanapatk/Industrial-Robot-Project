import socket
import logging
import time


class URConveyor:
    """
    A class to control a conveyor belt system via a TCP socket server.

    This class acts as a server that waits for a connection from the conveyor controller,
    activates it, and provides methods to control its motion, including setting velocity,
    jogging in forward/backward direction, and stopping.

    Methods:
        set_servo(state): Turn the conveyor motor on or off.
        set_velocity(velocity): Set the conveyor velocity (0–200 mm/s).
        jog(forward): Jog the conveyor forward or backward.
        stop(): Stop the conveyor's movement.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 2002):
        """
        Initialize the conveyor controller server and wait for a connection.

        Args:
            host (str): IP address to bind the server. Defaults to "0.0.0.0".
            port (int): Port number to bind the server. Defaults to 2002.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        logging.info(f"Hosted Server on port {port}")

        self.socket.listen(1)

        self.conn, self.addr = self.socket.accept()

        logging.info(f"Connected by {self.addr}")

        self.conn.sendall(b"activate,tcp\n")
        logging.info("Activated Conveyor")

        # time.sleep(1)

        self.set_servo(True)

        time.sleep(1)

    def _send(self, command: str):
        self.conn.sendall(command.encode())

    def set_servo(self, state: bool):
        """
        Turn the servo power on or off.

        Args:
            state (bool): True to turn on, False to turn off.
        """
        self._send(f"pwr_{('off', 'on')[state]},conv,0\n")
        logging.info(f"Servo power {('off','on')[state]}")

    def set_velocity(self, velocity: float):
        """
        Set the velocity of the conveyor.

        Args:
            velocity (float): Velocity in mm/s. Must be between 0 and 200.

        Raises:
            ValueError: If the velocity is out of the valid range.
        """
        if velocity < 0 or velocity > 200:
            raise ValueError("Velocity has to be in range of 0 to 200")

        self._send(f"set_vel,conv,{velocity}\n")
        logging.info(f"Set Conveyor Velocity to {velocity}")

    def jog(self, forward: bool):
        """
        Move the conveyor in a specified direction.

        Args:
            forward (bool): True to jog forward, False to jog backward.
        """
        self._send(f"jog_{'bf'[forward]}wd,conv,0\n")
        logging.info(f"Conveyor jog {('backward','forward')[forward]}")

    def stop(self):
        "Stop the conveyor's current motion."
        self._send(f"jog_stop,conv,0\n")
        logging.info("Stopped Conveyor")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    conv = URConveyor("0.0.0.0", 2002)

    conv.set_velocity(30)

    conv.jog(True)

    time.sleep(5)

    conv.stop()
