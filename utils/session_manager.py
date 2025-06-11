import qi
import sys
import os
import sqlite3
import pandas as pd


UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.dirname(UTILS_DIR)


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
        conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
        clients_df.to_sql("clients", conn, if_exists="replace", index=False)
        vinyls_df.to_sql("vinyls", conn, if_exists="replace", index=False)
        orders_df.to_sql("orders", conn, if_exists="replace", index=False)
        conn.close()