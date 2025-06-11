import qi
import sys
import time
import math

from session_manager import *


def reach_and_grab():
    manager = SessionManager()

    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    # Set arm stiffness
    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]

    # Slightly lower and more forward reach position
    reach_angles = [ 0.0, -0.2, 1.2, 0.5, 0.0, 1.0]
    reach_times  = [ 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]

    ALMotion.angleInterpolation(names, reach_angles, reach_times, True)

    # Simulate grab with wrist
    names = ["RWristYaw", "RHand"]
    reach_angles = [0.5, 0.0]
    reach_times = [0.5, 0.5]
    ALMotion.angleInterpolation(names, reach_angles, reach_times, True)

    # Remove stiffness and return home
    ALRobotPosture.goToPosture("StandInit", 0.5)



def offer_item():
    manager = SessionManager()

    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    # Set stiffness and assume initial posture
    ALRobotPosture.goToPosture("StandInit", 0.5)

    # Arm joints to move the hand forward, open, and palm-up
    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]

    # Angles:
    # - Arm extended forward at chest level
    # - Palm facing up: ElbowRoll negative, WristYaw at 0
    # - Hand open (value 1.0)
    offer_angles = [0.4, -0.3, 1.3, -1.0, 1.57, 1.0]
    offer_times  = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0]

    ALMotion.angleInterpolation(names, offer_angles, offer_times, True)

    # Pause for a moment to present the item
    time.sleep(2.0)

    # Return to initial posture
    ALRobotPosture.goToPosture("StandInit", 0.5)
