import qi
import sys
import os
import sqlite3
import pandas as pd
import os
import sys

from .tablet import init_client

try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print("Please set MODIM_HOME environment variable to MODIM folder.")
    sys.exit(1)

from ws_client import *

UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.dirname(UTILS_DIR)
TABLET_DIR = os.path.join(MAIN_DIR, 'tablet')


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


    def initialize_database(self):

        clients_df = pd.read_csv(os.path.join(MAIN_DIR, "data/clients.csv"))
        vinyls_df = pd.read_csv(os.path.join(MAIN_DIR, "data/vinyls.csv"))
        orders_df = pd.read_csv(os.path.join(MAIN_DIR, "data/orders.csv"))
        buys_df = pd.read_csv(os.path.join(MAIN_DIR, "data/buys.csv"))
        conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
        clients_df.to_sql("clients", conn, if_exists="replace", index=False)
        vinyls_df.to_sql("vinyls", conn, if_exists="replace", index=False)
        orders_df.to_sql("orders", conn, if_exists="replace", index=False)
        buys_df.to_sql("buys", conn, if_exists="replace", index=False)
        conn.close()

    
    def initialize_tablet(self):

        with suppress_output():        
            self.mws = ModimWSClient()
            path = os.path.join(TABLET_DIR, "scripts/placeholder")
            self.mws.setDemoPathAuto(path)
            self.mws.run_interaction(init_client)
            self.mws.cconnect()


    def ask_modim(self, action, timeout=999):
        with suppress_output():
            return self.mws.csend("im.ask('{}', timeout={})".format(action, timeout))


    def execute_modim(self, action):
        with suppress_output():
            return self.mws.csend("im.execute('{}')".format(action))



class suppress_output(object):
    def __enter__(self):
        # Open a null file
        self.null_fds = [os.open(os.devnull, os.O_RDWR)]
        # Save the current stdout and stderr
        self.save_fds = [os.dup(1), os.dup(2)]
        # Redirect stdout and stderr to devnull
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[0], 2)

    def __exit__(self, *_):
        # Restore stdout and stderr
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)