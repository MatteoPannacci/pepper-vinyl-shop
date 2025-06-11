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

    # instantiate services
    ALDialog = manager.session.service('ALDialog')
    ALMemory = manager.session.service('ALMemory')

    # setup ALDialog
    topic_path = os.path.join(MAIN_DIR, "main.top")
    topf_path = topic_path.decode('utf-8')
    topic_name = ALDialog.loadTopic(topf_path.encode('utf-8'))
    ALDialog.activateTopic(topic_name)
    ALDialog.subscribe('pepper_vinyl_shop')

    # reset variables
    for key in ALMemory.getDataList("pepper-vinyl/"):
        ALMemory.insertData(key, "")
        print("Deleted: {}".format(key))

    # connect handlers
    function_sub = ALMemory.subscriber("pepper-vinyl/function")
    function_sub.signal.connect(handleFunction)

    # busy waiting
    print("Pepper is Running... use Ctrl+C to finish the execution.")
    while True:

        try:
            time.sleep(2)

        except KeyboardInterrupt:
            return graceful_close(ALDialog, topic_name)


# we can handle touching and events in general through the topics
# we can point at the vinyl location before going there



if __name__ == "__main__":
    main()