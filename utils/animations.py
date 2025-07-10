import qi
import sys
import time
import math
import wave
import numpy as np

from session_manager import *


def reset_posture():
    manager = SessionManager()

    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    ALRobotPosture.goToPosture("StandInit", 0.5)


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


def idle_animation_1():
    manager = SessionManager()
    ALMotion = manager.session.service("ALMotion")
    ALMotion.wakeUp()

    # Joint groups
    left_joints = ["LShoulderPitch", "LElbowRoll", "LWristYaw"]
    right_joints = ["RShoulderPitch", "RElbowRoll", "RWristYaw"]
    head_joints = ["HeadYaw", "HeadPitch"]

    freq = 0.5  # Hz (1 cycle = 1 second)
    duration = 1.5  # seconds
    amplitude = {
        "LShoulderPitch": 0.2,
        "LElbowRoll": 0.3,
        "LWristYaw": 0.5,
        "RShoulderPitch": 0.2,
        "RElbowRoll": 0.3,
        "RWristYaw": 0.5,
        "HeadYaw": 0.3,
        "HeadPitch": 0.1,
    }

    base_pose = {
        "LShoulderPitch": 1.3,
        "LElbowRoll": -0.6,
        "LWristYaw": 0.0,
        "RShoulderPitch": 1.3,
        "RElbowRoll": 0.6,
        "RWristYaw": 0.0,
        "HeadYaw": 0.0,
        "HeadPitch": -0.1,
    }

    t_start = time.time()
    while (time.time() - t_start) < duration:
        t = time.time() - t_start
        phase = 2 * math.pi * freq * t

        # Sinusoidal modulation
        left_targets = [
            base_pose["LShoulderPitch"] + amplitude["LShoulderPitch"] * math.sin(phase),
            base_pose["LElbowRoll"] + amplitude["LElbowRoll"] * math.sin(phase + math.pi / 3),
            base_pose["LWristYaw"] + amplitude["LWristYaw"] * math.sin(phase + math.pi / 2),
        ]
        right_targets = [
            base_pose["RShoulderPitch"] + amplitude["RShoulderPitch"] * math.sin(phase + math.pi),
            base_pose["RElbowRoll"] + amplitude["RElbowRoll"] * math.sin(phase + math.pi + math.pi / 3),
            base_pose["RWristYaw"] + amplitude["RWristYaw"] * math.sin(phase + math.pi + math.pi / 2),
        ]
        head_targets = [
            base_pose["HeadYaw"] + amplitude["HeadYaw"] * math.sin(phase / 2),
            base_pose["HeadPitch"] + amplitude["HeadPitch"] * math.sin(phase / 2 + math.pi / 4)
        ]

        # Send non-blocking commands
        ALMotion.setAngles(left_joints, left_targets, 0.3)
        ALMotion.setAngles(right_joints, right_targets, 0.3)
        ALMotion.setAngles(head_joints, head_targets, 0.2)

        time.sleep(0.05)  # 20 Hz

    # Return to neutral pose
    ALMotion.angleInterpolationWithSpeed(
        left_joints + right_joints + head_joints,
        [
            base_pose["LShoulderPitch"], base_pose["LElbowRoll"], base_pose["LWristYaw"],
            base_pose["RShoulderPitch"], base_pose["RElbowRoll"], base_pose["RWristYaw"],
            base_pose["HeadYaw"], base_pose["HeadPitch"]
        ],
        0.3
    )


def idle_animation_2():
    manager = SessionManager()
    ALMotion = manager.session.service("ALMotion")
    ALMotion.wakeUp()

    # Relevant joints
    right_joints = ["RShoulderPitch", "RElbowYaw", "RElbowRoll", "RWristYaw"]
    head_joints = ["HeadYaw", "HeadPitch"]

    # Duration of the full gesture
    duration = 1.5
    t_start = time.time()

    # Keyframes for gesture: subtle expressive arc with head attention
    keyframes = {
        "RShoulderPitch": [1.1, 0.8, 1.1],
        "RElbowYaw": [1.2, 1.6, 1.2],
        "RElbowRoll": [0.7, 1.1, 0.7],
        "RWristYaw": [0.0, 0.3, 0.0],
        "HeadYaw": [-0.2, 0.0, -0.2],
        "HeadPitch": [-0.1, 0.1, -0.1],
    }

    # Time points for keyframes (expressive motion, short pause, return)
    t_norm = [0.0, 0.75, 1.5]  # normalized times

    while (time.time() - t_start) < duration:
        t = time.time() - t_start

        # Compute interpolated values for each joint
        def interp(joint):
            return np.interp(t, t_norm, keyframes[joint])

        right_targets = [interp(j) for j in right_joints]
        head_targets = [interp(j) for j in head_joints]

        # Send to robot
        ALMotion.setAngles(right_joints, right_targets, 0.2)
        ALMotion.setAngles(head_joints, head_targets, 0.15)

        time.sleep(0.05)

    # Final clean reset
    ALMotion.angleInterpolationWithSpeed(
        right_joints + head_joints,
        [
            keyframes["RShoulderPitch"][0], keyframes["RElbowYaw"][0],
            keyframes["RElbowRoll"][0], keyframes["RWristYaw"][0],
            keyframes["HeadYaw"][0], keyframes["HeadPitch"][0]
        ],
        0.3
    )


def idle_animation_3():
    manager = SessionManager()
    ALMotion = manager.session.service("ALMotion")
    ALMotion.wakeUp()

    left_joints = ["LShoulderRoll", "LElbowRoll"]
    right_joints = ["RShoulderRoll", "RElbowRoll"]
    head_joints = ["HeadYaw"]

    freq = 0.4
    duration = 1.5
    amplitude = {
        "LShoulderRoll": 0.3,
        "LElbowRoll": 0.25,
        "RShoulderRoll": 0.3,
        "RElbowRoll": 0.25,
        "HeadYaw": 0.25,
    }

    base_pose = {
        "LShoulderRoll": 0.2,
        "LElbowRoll": -0.4,
        "RShoulderRoll": -0.2,
        "RElbowRoll": 0.4,
        "HeadYaw": 0.0,
    }

    t_start = time.time()
    while (time.time() - t_start) < duration:
        t = time.time() - t_start
        phase = 2 * math.pi * freq * t

        left_targets = [
            base_pose["LShoulderRoll"] + amplitude["LShoulderRoll"] * math.sin(phase),
            base_pose["LElbowRoll"] + amplitude["LElbowRoll"] * math.sin(phase),
        ]
        right_targets = [
            base_pose["RShoulderRoll"] + amplitude["RShoulderRoll"] * math.sin(phase),
            base_pose["RElbowRoll"] + amplitude["RElbowRoll"] * math.sin(phase),
        ]
        head_targets = [
            base_pose["HeadYaw"] + amplitude["HeadYaw"] * math.sin(phase / 2)
        ]

        ALMotion.setAngles(left_joints, left_targets, 0.3)
        ALMotion.setAngles(right_joints, right_targets, 0.3)
        ALMotion.setAngles(head_joints, head_targets, 0.2)
        time.sleep(0.05)

    ALMotion.angleInterpolationWithSpeed(
        left_joints + right_joints + head_joints,
        [
            base_pose["LShoulderRoll"], base_pose["LElbowRoll"],
            base_pose["RShoulderRoll"], base_pose["RElbowRoll"],
            base_pose["HeadYaw"]
        ],
        0.3
    )

def thinking_animation():
    manager = SessionManager()
    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    # Wake up and stand in a neutral position
    ALMotion.wakeUp()
    ALRobotPosture.goToPosture("StandInit", 0.3)

    right_arm = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
    right_pose = [0.6, -0.2, 1.8, 1.5, 0.3, 0.8]  # Closer to face, more bent at elbow

    # Move arm near chin
    ALMotion.angleInterpolation(right_arm, right_pose, [0.6] * len(right_arm), True)

    # Tilt head gently (thinking expression)
    ALMotion.angleInterpolation(["HeadYaw", "HeadPitch"], [0.25, 0.3], [0.4, 0.4], True)

    # Pause as if pondering
    time.sleep(1.5)

    # Slight nod (idea moment)
    ALMotion.angleInterpolation(["HeadPitch"], [0.0], [0.3], True)

    # Lower arm to relaxed pose
    rest_pose = [1.4, -0.1, 1.0, 0.3, 0.0, 1.0]
    ALMotion.angleInterpolation(right_arm, rest_pose, [0.5] * len(right_arm), True)

    # Re-center head
    ALMotion.angleInterpolation(["HeadYaw", "HeadPitch"], [0.0, 0.0], [0.3, 0.3], True)

    # Return to neutral standing pose
    ALRobotPosture.goToPosture("StandInit", 0.4)


def greeting_animation():
    manager = SessionManager()

    ALMotion = manager.session.service("ALMotion")
    ALRobotPosture = manager.session.service("ALRobotPosture")

    # Wake up and go to neutral posture
    ALMotion.wakeUp()
    ALRobotPosture.goToPosture("StandInit", 0.3)

    # Raise right arm higher and faster
    names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
    angles = [0.7, -0.1, 1.5, 1.3, 0.0, 1.0]  # High and bent
    times = [0.6] * len(names)  # Faster movement
    ALMotion.angleInterpolation(names, angles, times, True)

    # Quick wrist wave
    wave_names = ["RWristYaw"]
    wave_1 = [0.6]
    wave_2 = [-0.6]
    wave_time = [0.2]  # Faster wave

    for _ in range(3):
        ALMotion.angleInterpolation(wave_names, wave_1, wave_time, True)
        ALMotion.angleInterpolation(wave_names, wave_2, wave_time, True)

    # Return to neutral posture
    ALRobotPosture.goToPosture("StandInit", 0.4)