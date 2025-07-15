import sys
import os
import qi

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


UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.dirname(UTILS_DIR)
TABLET_FOLDER = os.path.join(MAIN_DIR, 'tablet')
ACTIONS_FOLDER = os.path.join(TABLET_FOLDER, 'actions')


def init_client():
    im.init()


def create_dynamic_action(image=None, text=None, speech=None, buttons=None, gesture=None, action_name='dynamic-action'):

    action_file_path = os.path.join(ACTIONS_FOLDER, action_name)

    action_content = ""

    if image != None:
        action_content += """IMAGE
            <*,*,*,*>: img/{}
            ----
        """.format(image)
    
    if text != None:
        action_content += """TEXT
            <*,*,*,*>: {}
            ----
        """.format(text)

    if speech != None:
        action_content +=  """TTS
            <*,*,*,*>: {}
            ----
        """
    
    if buttons != None:
        action_content += "BUTTONS\n"
        for button in buttons:
            action_content += "{}\n".format(button)
            action_content += "<*,*,*,*>: {}\n".format(button.capitalize())
        action_content += "----"

    else:
        action_content += "BUTTONS\n"
        action_content += "----"

    if gesture != None:
        action_content += """
            GESTURE <*,*,*,*>: {}
            ----      
        """.format(gesture)

    action_content = action_content.replace('    ', '')

    try:
        f = open(action_file_path, 'w')
        f.write(action_content)
        f.close()
    except IOError as e:
        print("Error writing to action file: {}".format(e))
        sys.exit(1)
