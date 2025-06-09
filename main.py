import qi
import argparse
import sys
import os
import sqlite3
import pandas as pd
import time
from MotionManager import *


def graceful_close(ALDialog, topic_name):
    print("\nTerminating...\n")
    ALDialog.unsubscribe('pepper_vinyl_shop')
    ALDialog.deactivateTopic(topic_name)
    ALDialog.unloadTopic(topic_name)
    return 0


def checkUsername():

    username = ALMemory.getData("pepper-vinyl/username")

    conn = sqlite3.connect(os.path.join(project_path, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM clients WHERE username = '{}' LIMIT 1".format(username))
    
    recognized = "true" if cursor.fetchone() else "false"
    ALMemory.raiseEvent("pepper-vinyl/recognized", recognized)

    if recognized == "false":
        cursor.execute('''
            INSERT INTO clients (username, fav_genre)
            VALUES (?, ?)
        ''', (username, None))
        conn.commit()

    cursor.execute('SELECT * FROM clients')
    rows = cursor.fetchall()

    for row in rows:
        print(" | ".join(str(item) if item is not None else "NULL" for item in row))

    conn.close()




def handleFunction(value):

    if value == "check_username":
        checkUsername()

    if value == 0:
        print("I received an event!!")

    if value == 1:

        conn = sqlite3.connect(os.path.join(project_path, "data/database.db"))
        cursor = conn.cursor()        

        cursor.execute("SELECT vinyl FROM vinyls")
        vinyl_list = [row[0] for row in cursor.fetchall()]

        conn.close()

        string = ""
        for vinyl in vinyl_list:
            print(vinyl)
            string += " {}".format(vinyl)

        ALMemory.raiseEvent("pepper-vinyl/say", "Damn")



def main():

    global project_path
    global ALMemory, ALDialog, tts_service

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'], help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, required=True, help="Naoqi port number")
    args = parser.parse_args()

    # find project path
    project_path = os.path.dirname(os.path.abspath(__file__))

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

    # initialize database
    clients_df = pd.read_csv(os.path.join(project_path, "data/clients.csv"))
    vinyls_df = pd.read_csv(os.path.join(project_path, "data/vinyls.csv"))
    conn = sqlite3.connect(os.path.join(project_path, "data/database.db"))
    clients_df.to_sql("clients", conn, if_exists="replace", index=False)
    vinyls_df.to_sql("vinyls", conn, if_exists="replace", index=False)
    conn.close()

    # delete dfs
    del clients_df
    del vinyls_df

    # create variables for services
    ALDialog = session.service('ALDialog')
    ALMemory = session.service('ALMemory')
    ALMotion = session.service("ALMotion")
    tts_service = session.service("ALTextToSpeech")

    # setup Motion
    #ALMotion.move(10, 0, 0)
    #time.sleep(10)
    #ALMotion.stopMove()

    # setup ALDialog
    topic_path = os.path.join(project_path, "main.top")
    topf_path = topic_path.decode('utf-8')
    topic_name = ALDialog.loadTopic(topf_path.encode('utf-8'))
    ALDialog.activateTopic(topic_name)
    ALDialog.subscribe('pepper_vinyl_shop')

    # connect variables
    function_sub = ALMemory.subscriber("pepper-vinyl/function")
    function_sub.signal.connect(handleFunction)

    ALMemory.insertData("pepper-vinyl/username", "")
    ALMemory.insertData("pepper-vinyl/function", "")
    ALMemory.insertData("pepper-vinyl/recognized", "false")
    ALMemory.insertData("pepper-vinyl/say", "")

    # busy waiting
    print("Pepper is Running... use Ctrl+C to finish the execution.")
    while True:

        try:
            time.sleep(2)

        except KeyboardInterrupt:
            return graceful_close(ALDialog, topic_name)


# we can handle touching and events in general through the topics



if __name__ == "__main__":
    main()