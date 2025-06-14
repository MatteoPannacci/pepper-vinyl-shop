import qi
import argparse
import sys
import os
import sqlite3
import pandas as pd
import time

from utils import *


MAIN_DIR = os.path.dirname(os.path.abspath(__file__))


def graceful_close(ALDialog, topic_name):
    print("\nTerminating...\n")
    ALDialog.unsubscribe('pepper_vinyl_shop')
    ALDialog.deactivateTopic(topic_name)
    ALDialog.unloadTopic(topic_name)
    return 0



def main():

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'], help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, required=True, help="Naoqi port number")
    args = parser.parse_args()

    # connect to the session
    manager = SessionManager()
    manager.connect(args.pip, args.pport)

    # initialize database
    manager.initialize_database()

    # initialize tablet
    manager.initialize_tablet()

    # instantiate services
    ALDialog = manager.session.service('ALDialog')
    ALMemory = manager.session.service('ALMemory')
    ALRobotPosture = manager.session.service('ALRobotPosture')

    # setup ALDialog
    topic_path = os.path.join(MAIN_DIR, "main.top")
    topf_path = topic_path.decode('utf-8')
    topic_name = ALDialog.loadTopic(topf_path.encode('utf-8'))
    ALDialog.activateTopic(topic_name)
    ALDialog.subscribe('pepper_vinyl_shop')

    ALRobotPosture.goToPosture("StandInit", 0.5)

    # reset variables
    for key in ALMemory.getDataList("pepper-vinyl/"):
        ALMemory.insertData(key, "")
        print("Deleted: {}".format(key))

    # connect handlers
    function_sub = ALMemory.subscriber("pepper-vinyl/function")
    function_sub.signal.connect(handleFunction)
    tablet_sub = ALMemory.subscriber("pepper-vinyl/tablet")
    tablet_sub.signal.connect(handleTablet)
    tablet_dyn_sub = ALMemory.subscriber("pepper-vinyl/tablet_dyn")
    tablet_dyn_sub.signal.connect(handleTabletDynamic)


    print("Pepper is Running... use Ctrl+C to finish the execution.")
    handleTablet("ask_welcome")

    # busy waiting
    while True:

        try:
            time.sleep(2)

        except KeyboardInterrupt:
            return graceful_close(ALDialog, topic_name)


# we can handle touching and events in general through the topics
# we can use a finish_wait variable to synchronize the modim stuff
# can we use the tablet to play music?
# database vinyl-description + interaction "tell me more about it"


if __name__ == "__main__":
    main()