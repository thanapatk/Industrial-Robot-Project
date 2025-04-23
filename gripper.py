import socket
import logging
import time


class URGripper:
    """
    A class to control gripper via TCP.

    Methods:
        control_gripper(state): Opens or closes the gripper depending on the state.
    """

    def __init__(self, ip: str, port: int = 63352):
        """
        Initialize and activate the UR gripper.

        Connects to the gripper using a TCP socket, activates it if not already active,
        and sets default speed and force settings. Then, it initializes the gripper
        to the open position.

        Args:
            ip (str): IP address of the gripper.
            port (int): Port number for the TCP connection (default is 63352).
        """
        self.gripper_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gripper_socket.connect((ip, port))
        self.gripper_socket.send(b"GET ACT\n")

        socket_recv = self.gripper_socket.recv(10)
        if b"1" not in socket_recv:
            logging.warning("Gripper not activated")

        self.gripper_socket.send(b"GET POS\n")
        gripper_socket_recv = str(self.gripper_socket.recv(10), "UTF-8")
        if gripper_socket_recv:
            self.gripper_socket.send(b"SET ACT 1\n")  # set activation bit to 1
            gripper_socket_recv = str(self.gripper_socket.recv(255), "UTF-8")
            print(gripper_socket_recv)
            time.sleep(3)
            self.gripper_socket.send(
                b"SET GTO 1\n"
            )  # set gripper to move to requested position
            self.gripper_socket.send(b"SET SPE 255\n")  # set speed eco
            self.gripper_socket.send(b"SET FOR 255\n")  # set force

            self.control_gripper(False)

    def control_gripper(self, state: bool):
        """
        Control the gripper's position.

        Sends a command to either open or close the gripper based on the boolean `state`.

        Args:
            state (bool): If True, the gripper closes. If False, the gripper opens.

        Logs a warning if the gripper does not acknowledge the command.
        """
        self.gripper_socket.send(f"SET POS {255 if state else 0}\n".encode("UTF-8"))

        # acknowledge the gripper movement
        g_recv = self.gripper_socket.recv(10)
        if b"ack" not in g_recv:
            logging.warning("Gripper not acknowledge")
