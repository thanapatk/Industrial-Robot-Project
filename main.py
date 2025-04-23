import math
import numpy as np
import time
import logging

logging.basicConfig(level=logging.INFO)

from arm import URARM
from gripper import URGripper
from conveyor import URConveyor
from vision import Vision
from equation_solver import solve_time

arm_ip = "10.10.0.14"
vision_ip = "10.10.1.10"
conv_ip = "0.0.0.0"

arm_port = 30003
gripper_port = 63352
vision_port = 2024
conv_port = 2002

# x y z rx ry rz
home_pos = [0.116, -0.300, 0.08, 128 * math.pi / 180, 128 * math.pi / 180, 0]

cam_offset_x = 185.15  # mm
conv_speed = 20e-3  # m/s

arm_v_max = 3  # m/s
arm_a_max = 5  # m/s^2

avg_box_width = (100 + 130) / 2  # mm
avg_box_height = (150 + 115) / 2  # mm

if __name__ == "__main__":
    arm = URARM(arm_ip, arm_port, home_pos)
    gripper = URGripper(arm_ip, gripper_port)
    conv = URConveyor(conv_ip, conv_port)
    vision = Vision(vision_ip, vision_port)

    # start conveyor
    conv.set_velocity(conv_speed * 1e3)
    conv.jog(True)

    # wait for box to be detected
    cam_dx, cam_dy, cam_theta, t_initial = vision.get_box_pos()
    logging.info(f"Box position: dx={cam_dx}, dy={cam_dy}, theta={cam_theta}")

    # calculate UR arm relative position to intercept with the box
    dx = (cam_dy + cam_offset_x + avg_box_width / 3) * 1e-3
    dy = (cam_dx) * 1e-3
    dz = -(380 - avg_box_height * 2 / 3) * 1e-3
    dtheta = np.deg2rad(cam_theta)

    time_to_reach = solve_time(dx, dy, dz, conv_speed, arm_v_max, arm_a_max)
    logging.info(f"Time to reach the target: {time_to_reach:.2f} seconds")

    # move to the intercept position
    arm.movel(
        URARM.relative_pose(
            dx - conv_speed * time_to_reach, -dy, dz, -math.pi / 6, 0, -dtheta
        ),
        a=arm_a_max,
        v=arm_v_max,
    )

    # start closing the gripper during the movel
    while time.perf_counter() - t_initial < time_to_reach * 0.625:
        pass
    gripper.control_gripper(True)

    # wait to reach the intercept position
    while time.perf_counter() - t_initial < time_to_reach:
        pass

    # move the UR arm up to prevent dragging the conveyor
    arm.speedl([-conv_speed, 0, 0.5, 0, 0, 0], a=arm_a_max, t=0.5)
    time.sleep(0.5)

    # move back to home position
    arm.movel(f"p{str(home_pos)}")

    conv.stop()
