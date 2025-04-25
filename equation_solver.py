import numpy as np


def solve_time(
    dx: float, dy: float, dz: float, v_con: float, v_max: float, a_max: float
) -> float:
    """
    Calculate the time at which the UR robotic arm should intercept the moving box.

    This function solves for the time required for the robotic arm to reach a target position
    (dx, dy, dz) given a box moving at constant velocity `v_con`, while considering the robot's
    maximum velocity `v_max` and maximum acceleration `a_max`.

    Args:
        dx (float): Distance along the x-axis [meters].
        dy (float): Distance along the y-axis [meters].
        dz (float): Distance along the z-axis [meters].
        v_con (float): Velocity of the box on the conveyor [m/s].
        v_max (float): Maximum velocity of the robotic arm [m/s].
        a_max (float): Maximum acceleration of the robotic arm [m/s²].

    Returns:
        float: Time [s] at which the robotic arm should intercept the moving box.
    """
    return -(
        v_max**3
        + np.sqrt(
            a_max**2 * dx**2 * v_max**2
            - a_max**2 * dy**2 * v_con**2
            + a_max**2 * dy**2 * v_max**2
            - a_max**2 * dz**2 * v_con**2
            + a_max**2 * dz**2 * v_max**2
            - 2 * a_max * dx * v_con * v_max**3
            + v_con**2 * v_max**4
        )
        - a_max * dx * v_con
    ) / (a_max * (v_con**2 - v_max**2))


if __name__ == "__main__":
    dx = 170e-3  # Example values
    dy = 5e-3  # Example values
    dz = -0.2
    v_con = 30e-3  # Example values
    v_max = 1.5  # Example values
    a_max = 2.5  # Example values

    try:
        time_to_reach = solve_time(dx, dy, dz, v_con, v_max, a_max)
        print(f"Time to reach the target: {time_to_reach} seconds")
    except ValueError as e:
        print(e)
