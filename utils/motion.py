import math
from session_manager import *


def move_to(target_x, target_y, target_theta = None):

    manager = SessionManager()
    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service('ALRobotPosture')

    ALRobotPosture.goToPosture("StandInit", 0.5)

    use_sensor_values = False
    current_pose = ALMotion.getRobotPosition(use_sensor_values)
    x, y, theta = current_pose[0], current_pose[1], current_pose[2]

    # Vector from current position to target
    dx = target_x - x
    dy = target_y - y

    if (dx**2 + dy**2) > 0.1:

        # Angle to face target (in world frame)
        angle_to_target = math.atan2(dy, dx)

        # Compute relative angle to rotate (difference between target angle and current orientation)
        relative_theta = angle_to_target - theta
        relative_theta = (relative_theta + math.pi) % (2 * math.pi) - math.pi

        # Distance to target
        distance = math.hypot(dx, dy)

        # Step 1: rotate in place to face target
        ALMotion.moveTo(0.0, 0.0, relative_theta)

        # Step 2: move forward to the target
        ALMotion.moveTo(distance, 0.0, 0.0)

    else:

        # If it doesn't move keep the same theta
        angle_to_target = theta

    if target_theta != None:

        if type(target_theta) == float:
            relative_target_theta = target_theta - angle_to_target
            relative_target_theta = (relative_target_theta + math.pi) % (2 * math.pi) - math.pi

        elif target_theta == "behind":
            relative_target_theta = -math.pi

        ALMotion.moveTo(0.0, 0.0, relative_target_theta)


def rotate(target_theta):

    manager = SessionManager()
    ALMotion = manager.session.service("ALMotion")

    use_sensor_values = False
    current_pose = ALMotion.getRobotPosition(use_sensor_values)
    theta = current_pose[2]

    if type(target_theta) == float:
        relative_target_theta = target_theta - theta
        relative_target_theta = (relative_target_theta + math.pi) % (2 * math.pi) - math.pi

    elif target_theta == "behind":
        relative_target_theta = -math.pi

    ALMotion.moveTo(0.0, 0.0, relative_target_theta)