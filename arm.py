import socket
import time
import struct


class URARM:
    """
    A class for communicating and controlling a Universal Robots arm.

    Methods:
        relative_pose(x, y, z, rx, ry, rz): Generate a relative pose from the current TCP pose.
        get_actual_tcp_pose(): Retrieve the current pose of the tool center point (TCP).
        get_current_joint_angle(): Retrieve the current joint angles of the robot.
        movej(pose, a, v, t, r): Command a joint-space movement to the specified pose.
        movel(pose, a, v, t, r): Command a linear movement to the specified pose in Cartesian space.
        speedl(velocity, a, t): Command a speed in Cartesian space for a specific duration.
    """

    def __init__(
        self,
        robot_ip: str,
        arm_port: int = 30003,
        home_pose=None,
    ):
        """
        Initialize and connect to the robot arm.

        Args:
            robot_ip (str): IP address of the UR robot.
            arm_port (int, optional): Port to connect to the robot. Defaults to 30003.
            home_pose (list, optional): Pose to move the arm to after connection. Defaults to None.
        """
        self.arm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.arm_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.arm_socket.connect((robot_ip, arm_port))

        if home_pose:
            self.movel(f"p{str(home_pose)}")
            time.sleep(1)

    @staticmethod
    def relative_pose(
        x: float = 0,
        y: float = 0,
        z: float = 0,
        rx: float = 0,
        ry: float = 0,
        rz: float = 0,
    ) -> str:
        """
        Generate a URScript string to get a pose relative to the current TCP pose.

        Args:
            x (float): Relative x displacement.
            y (float): Relative y displacement.
            z (float): Relative z displacement.
            rx (float): Relative rotation around x-axis.
            ry (float): Relative rotation around y-axis.
            rz (float): Relative rotation around z-axis.

        Returns:
            str: A URScript string representing the relative pose command.
        """
        return f"pose_add(get_actual_tcp_pose(), p[{x},{y},{z},{rx},{ry},{rz}])"

    def get_actual_tcp_pose(self):
        """
        Get the current pose of the TCP.

        Returns:
            tuple: A tuple of 6 floats representing (x, y, z, rx, ry, rz) in meters and radians.
        """
        self.arm_socket.send(b"get_actual_tcp_pose()\n")
        recv = self.arm_socket.recv(1108)
        tcp_pose = struct.unpack("!6d", recv[588:636])
        return tcp_pose

    def get_current_joint_angle(self):
        """
        Get the current joint angles of the robot.

        Returns:
            tuple: A tuple of 6 floats representing joint positions in radians.
        """
        self.arm_socket.send(b"get_actual_joint_positions()\n")
        recv = self.arm_socket.recv(1108)
        joint_positions = struct.unpack("!6d", recv[252:300])
        return joint_positions

    def movej(
        self, pose, a: float = 1.2, v: float = 0.5, t: float = 0, r: float = 0
    ) -> None:
        """
        Move the robot in joint space using the movej command.

        Args:
            pose: The target joint positions or pose (URScript format).
            a (float): Acceleration in rad/s^2.
            v (float): Velocity in rad/s.
            t (float): Time to complete the motion.
            r (float): Blend radius.
        """
        self.arm_socket.send(f"movej({pose},{a},{v},{t},{r})\n".encode("UTF-8"))

    def movel(
        self, pose, a: float = 1.2, v: float = 0.5, t: float = 0, r: float = 0
    ) -> None:
        """
        Move the robot in Cartesian space using the movel command.

        Args:
            pose: The target pose in Cartesian space (URScript format).
            a (float): Acceleration in m/s^2.
            v (float): Velocity in m/s.
            t (float): Time to complete the motion.
            r (float): Blend radius.
        """
        self.arm_socket.send(f"movel({pose},{a},{v},{t},{r})\n".encode("UTF-8"))

    def speedl(self, velocity, a: float = 1.2, t: float = 0) -> None:
        """
        Set the TCP to move at a specified speed using the speedl command.

        Args:
            pose: The velocity vector in Cartesian space (URScript format).
            a (float): Acceleration in m/s^2.
            t (float): Time to maintain the velocity (0 for indefinite).
        """
        self.arm_socket.send(f"speedl({velocity},{a},{t})\n".encode("UTF-8"))


if __name__ == "__main__":
    import math

    home_pos = [0.116, -0.300, 0.08, 128 * math.pi / 180, 128 * math.pi / 180, 0]

    arm = URARM("10.10.0.14", home_pose=home_pos)
