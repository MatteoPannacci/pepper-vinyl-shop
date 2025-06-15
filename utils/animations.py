import qi
import sys
import time
import math
import wave

from session_manager import *


def reach_and_grab():
    manager = SessionManager()

    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]

    reach_angles = [ 0.0, -0.2, 1.2, 0.5, 0.0, 1.0]
    reach_times  = [ 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]

    ALMotion.angleInterpolation(names, reach_angles, reach_times, True)

    names = ["RWristYaw", "RHand"]
    reach_angles = [0.5, 0.0]
    reach_times = [0.5, 0.5]
    ALMotion.angleInterpolation(names, reach_angles, reach_times, True)

    ALRobotPosture.goToPosture("StandInit", 0.5)



def offer_item():
    manager = SessionManager()

    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    ALRobotPosture.goToPosture("StandInit", 0.5)

    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]

    offer_angles = [0.4, -0.3, 1.3, -1.0, 1.57, 1.0]
    offer_times  = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0]

    ALMotion.angleInterpolation(names, offer_angles, offer_times, True)

    time.sleep(2.0)

    ALRobotPosture.goToPosture("StandInit", 0.5)



def bow():
    manager = SessionManager()

    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    ALMotion.wakeUp()
    ALRobotPosture.goToPosture("StandInit", 0.5)

    joints = ["HipPitch", "LShoulderPitch", "RShoulderPitch"]
    ALMotion.stiffnessInterpolation(joints, 1.0, 1.0)

    bow_names = ["HipPitch", "LShoulderPitch", "RShoulderPitch"]
    bow_angles = [ -1, 1.5, 1.5 ]
    bow_times = [ 1.5, 1.5, 1.5 ]

    ALMotion.angleInterpolation(bow_names, bow_angles, bow_times, True)
    time.sleep(1.0)

    reset_angles = [ 0.0, 1.4, 1.4 ]
    reset_times = [ 1.5, 1.5, 1.5 ]

    ALMotion.angleInterpolation(bow_names, reset_angles, reset_times, True)

    ALMotion.stiffnessInterpolation(joints, 0.0, 1.0)


def dance_to_music(filepath=None):

    manager = SessionManager()
    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    ALMotion.wakeUp()
    ALRobotPosture.goToPosture("StandInit", 0.5)

    names = [
        "LShoulderPitch", "RShoulderPitch",
        "LShoulderRoll",  "RShoulderRoll",
        "HipRoll"
    ]

    dance_1 = [1.2, 1.2, 0.3, -0.3,  0.15]
    dance_2 = [1.4, 1.4, -0.2, 0.2, -0.15]
    dance_finish = [1.4, 1.4, -0.2, 0.2,  0.0]

    def get_wav_length(filepath):
        wav = wave.open(filepath, 'r')
        frames = wav.getnframes()
        rate = wav.getframerate()
        duration = frames / float(rate)
        wav.close()
        return duration

    if filepath:
        duration = get_wav_length(filepath)
        cycles = int(duration // 1.2)
    else:
        cycles=10

    for _ in range(cycles):
        ALMotion.angleInterpolation(names, dance_1, [0.6]*5, True)
        ALMotion.angleInterpolation(names, dance_2, [0.6]*5, True)

    ALMotion.angleInterpolation(names, dance_finish, [0.6]*5, True)

    ALRobotPosture.goToPosture("StandInit", 0.5)


def wait_animation(wait_time):

    manager = SessionManager()

    ALMotion = manager.session.service("ALMotion")

    ALMotion.wakeUp()
    ALMotion.setStiffnesses("Body", 1.0)
    ALMotion.setAngles("Body", [0.0]*25, 0.2)  # Hold neutral pose
    time.sleep(wait_time)  # Duration of the pause
    ALMotion.setStiffnesses("Body", 0.0)