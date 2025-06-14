import sys
import os
import random
import qi
import argparse

try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print("Please set MODIM_HOME environment variable to MODIM folder.")
    sys.exit(1)

from ws_client import *
from utils import *


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
    try:
        username = ALMemory.getData('username')
    except:
        username = None

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
        text = 'This is a test for our function!! (hi {})'.format(username),
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