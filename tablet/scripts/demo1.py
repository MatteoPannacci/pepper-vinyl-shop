import sys
import time
import os
import random
import qi
import argparse

try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print("Please set MODIM_HOME environment variable to MODIM folder.")
    sys.exit(1)

try:
    sys.path.insert(1, '/home/robot/playground/pepper-vinyl-shop')
except Exception as e:
    print("Please set HOME environment variable to plaground folder.")
    sys.exit(1)

import ws_client
from ws_client import *


SCRIPT_FOLDER = os.path.dirname(os.path.abspath(__file__))
TABLET_FOLDER = os.path.dirname(SCRIPT_FOLDER)
ACTIONS_FOLDER = os.path.join(TABLET_FOLDER, 'actions')



def init_client():
    im.init()


def create_dynamic_action(image, question, buttons=None, action_name='dynamic_action'):

    action_file_path = os.path.join(ACTIONS_FOLDER, action_name)

    action_content = """IMAGE
        <*,*,*,*>: img/{}
        ----
        TEXT
        <*,*,*,*>: {}
        ----
        TTS
        <*,*,*,*>: {}
        ----
        BUTTONS
    """.format(image, question, question)

    # WE CAN HAVE GESTURES
    # GESTURE <*,*,*,*>: animations/Stand/Emotions/Positive/Happy_4

    for button in buttons:
        action_content += "{}\n".format(button)
        action_content += "<*,*,*,*>: {}\n".format(button.capitalize())

    action_content += "----"

    action_content = action_content.replace('    ', '')

    try:
        f = open(action_file_path, 'w')
        f.write(action_content)
        f.close()
    except IOError as e:
        print("Error writing to action file: {}".format(e))
        sys.exit(1)



def main(mws):

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'], help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, required=True, help="Naoqi port number")
    args = parser.parse_args()

    # connect to the session
    try:
        connection_url = "tcp://{}:{}".format(args.pip, args.pport) 
        print("Connecting to {}".format(connection_url))
        app = qi.Application(["Memory Write", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Can't connect to Naoqi at ip {} on port {}.".format(args.pip, args.pport))
        sys.exit(1)
    app.start()
    session = app.session

    ALMemory = session.service('ALMemory')
    username = ALMemory.getData('username')

    mws.run_interaction(init_client)

    mws.cconnect()

    mws.csend("im.ask('welcome')")

    q = random.choice(['color'])

    a = mws.csend("im.ask('{}', timeout=999)".format(q))

    if a != 'timeout':
        mws.csend("im.execute('{}')".format(a))
        mws.csend("im.execute('goodbye')")

    create_dynamic_action(
        image = 'bear.jpg',
        question = 'This is a test for our function!! (hi {})'.format(username),
        buttons = ['yes', 'no', 'perhaps']
    )

    a = mws.csend("im.ask('dynamic_action')")

    print(a)


if __name__ == "__main__":

    mws = ModimWSClient()

    # local execution
    mws.setDemoPathAuto(__file__)
    # remote execution
    # mws.setDemoPath('<ABSOLUTE_DEMO_PATH_ON_REMOTE_SERVER>')

    main(mws)