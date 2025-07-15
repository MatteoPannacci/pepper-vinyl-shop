import qi
import argparse
import sys
import os
import time
import warnings
import logging

from utils import *


MAIN_DIR = os.path.dirname(os.path.abspath(__file__))


# mute tensorflow deprecation warnings and ws_client logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=UserWarning)
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('ws_client').setLevel(logging.CRITICAL + 1)



def graceful_close(ALDialog, topic_name, manager):
    print("\nTerminating...\n")
    ALDialog.unsubscribe('pepper_vinyl_shop')
    ALDialog.deactivateTopic(topic_name)
    ALDialog.unloadTopic(topic_name)
    manager.mws.cclose()
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
    ALMemory.raiseEvent("pepper-vinyl/counter", "0")

    # connect handlers
    function_sub = ALMemory.subscriber("pepper-vinyl/function")
    function_sub.signal.connect(handleFunction)
    tablet_sub = ALMemory.subscriber("pepper-vinyl/tablet")
    tablet_sub.signal.connect(handleTablet)
    tablet_dyn_sub = ALMemory.subscriber("pepper-vinyl/tablet_dyn")
    tablet_dyn_sub.signal.connect(handleTabletDynamic)

    ALAnimatedSpeech = manager.session.service("ALAnimatedSpeech")
    ALAnimatedSpeech.setBodyLanguageMode(2)

    print("Pepper is Running... use Ctrl+C to finish the execution.")
    ALMemory.raiseEvent("pepper-vinyl/tablet", "ask_welcome")

    # busy waiting
    while True:

        try:

            command = raw_input()

            if command == "passing_by":
                ALMemory.raiseEvent("pepper-vinyl/function", "user_passing")

        except KeyboardInterrupt:
            return graceful_close(ALDialog, topic_name, manager)


# database vinyl-description + interaction "tell me more about it"


if __name__ == "__main__":
    main()