import qi
import sys
import os


class SessionManager(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance


    def connect(self, pip, pport):

        try:
            connection_url = "tcp://{}:{}".format(pip, pport) 
            print("Connecting to {}".format(connection_url))
            self.app = qi.Application(["Memory Write", "--qi-url=" + connection_url])
        except RuntimeError:
            print("Can't connect to Naoqi at ip {} on port {}.".format(pip, pport))
            sys.exit(1)

        self.app.start()
        self.session = self.app.session