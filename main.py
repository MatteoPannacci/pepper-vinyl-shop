import qi
import argparse
import sys
import os


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

    # find project path
    project_path = os.path.dirname(os.path.abspath(__file__))

    #Starting application
    try:
        connection_url = "tcp://{}:{}".format(args.pip, args.pport) 
        print("Connecting to {}".format(connection_url))
        app = qi.Application(["Memory Write", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Can't connect to Naoqi at ip {} on port {}.".format(args.pip, args.pport))
        sys.exit(1)

    app.start()
    session = app.session

    # create variables for services
    ALDialog = session.service('ALDialog')
    ALMemory = session.service('ALMemory')
    ALMotion = session.service("ALMotion")
    tts_service = session.service("ALTextToSpeech")
    
    # setup ALDialog
    topic_path = os.path.join(project_path, "main.top")
    topf_path = topic_path.decode('utf-8')
    topic_name = ALDialog.loadTopic(topf_path.encode('utf-8'))
    
    tts_service.say("Hello! I'm LUIGI.\nI'm here to inform and help you.\nYou can talk with me or interact by clicking the tablet."+" "*5, _async=True)

    
    ALDialog.activateTopic(topic_name)
    ALDialog.subscribe('pepper_vinyl_shop')

    while True:

        try:

            user_input = raw_input("Pepper is Running...\nwrite \"stop\" or use Ctrl+C to finish the execution: ")

        except KeyboardInterrupt:
            return graceful_close(ALDialog, topic_name)
        
        if user_input == "stop":
            return graceful_close(ALDialog, topic_name)



if __name__ == "__main__":
    main()