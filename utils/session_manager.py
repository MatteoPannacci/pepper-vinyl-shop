import qi
import sys
import os
import sqlite3
import pandas as pd
import os
import sys
import io
import contextlib

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
        ratings_df = pd.read_csv(os.path.join(MAIN_DIR, "data/ratings.csv"))

        conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))

        clients_df.to_sql("clients_csv", conn, if_exists="replace", index=False)
        vinyls_df.to_sql("vinyls_csv", conn, if_exists="replace", index=False)
        orders_df.to_sql("orders_csv", conn, if_exists="replace", index=False)
        buys_df.to_sql("buys_csv", conn, if_exists="replace", index=False)
        ratings_df.to_sql("ratings_csv", conn, if_exists="replace", index=False)

        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS orders;")
        cursor.execute("DROP TABLE IF EXISTS buys;")
        cursor.execute("DROP TABLE IF EXISTS ratings;")
        cursor.execute("DROP TABLE IF EXISTS clients;")
        cursor.execute("DROP TABLE IF EXISTS vinyls;")

        cursor.execute("""
        CREATE TABLE vinyls (
            vinyl TEXT PRIMARY KEY,
            author TEXT,
            genre TEXT,
            release_date TEXT,
            quantity INTEGER,
            x REAL,
            y REAL
        );
        """)

        cursor.execute("""
            INSERT INTO vinyls 
            SELECT * FROM vinyls_csv;
        """)
        cursor.execute("DROP TABLE vinyls_csv;")

        cursor.execute("""
        CREATE TABLE clients (
            username TEXT PRIMARY KEY,
            fav_genre TEXT,
            fav_author TEXT,
            last_visit TEXT
        );
        """)

        cursor.execute("""
            INSERT INTO clients 
            SELECT * FROM clients_csv;
        """)
        cursor.execute("DROP TABLE clients_csv;")

        cursor.execute("""
        CREATE TABLE buys (
            client TEXT,
            vinyl TEXT,
            date TEXT,
            FOREIGN KEY (vinyl) REFERENCES vinyls(vinyl),
            FOREIGN KEY (client) REFERENCES clients(username)
        );
        """)

        cursor.execute("""
            INSERT INTO buys 
            SELECT * FROM buys_csv;
        """)
        cursor.execute("DROP TABLE buys_csv;")

        cursor.execute("""
        CREATE TABLE orders (
            vinyl TEXT,
            client TEXT,
            status TEXT,
            FOREIGN KEY (vinyl) REFERENCES vinyls(vinyl),
            FOREIGN KEY (client) REFERENCES clients(username)
        );
        """)

        cursor.execute("""
            INSERT INTO orders 
            SELECT * FROM orders_csv;
        """)
        cursor.execute("DROP TABLE orders_csv;")

        cursor.execute("""
        CREATE TABLE ratings (
            username TEXT,
            rating INTEGER,
            FOREIGN KEY (username) REFERENCES clients(username)
        );
        """)

        cursor.execute("""
            INSERT INTO ratings 
            SELECT * FROM ratings_csv;
        """)
        cursor.execute("DROP TABLE ratings_csv;")

        conn.commit()
        conn.close()

    
    def initialize_tablet(self):
    
        with filtered_print(filter):
            self.mws = ModimWSClient()
            path = os.path.join(TABLET_DIR, "scripts/placeholder")
            self.mws.setDemoPathAuto(path)
            self.mws.run_interaction(init_client)
            self.mws.cconnect()


    def ask_modim(self, action, timeout=999):
        with filtered_print(filter):
            self.msw
            return self.mws.csend("im.ask('{}', timeout={})".format(action, timeout))


    def execute_modim(self, action):
        with filtered_print(filter):
            self.mws.csend("im.executeModality('BUTTONS', [])")
            return self.mws.csend("im.execute('{}')".format(action))



import sys
import os
from contextlib import contextmanager
from io import StringIO

class FilteredStdout:
    def __init__(self, filter_func, original_stdout):
        self.filter_func = filter_func
        self.original_stdout = original_stdout
        self.buffer = ''

    def write(self, s):
        # Accumulate in buffer, but flush lines on newline
        self.buffer += s
        while '\n' in self.buffer:
            line, self.buffer = self.buffer.split('\n', 1)
            # Apply filter
            if self.filter_func(line):
                self.original_stdout.write(line + '\n')

    def flush(self):
        # Flush any remaining content
        if self.buffer:
            if self.filter_func(self.buffer):
                self.original_stdout.write(self.buffer)
            self.buffer = ''
        self.original_stdout.flush()


def filter(text):
    allowed = True
    for t in ["WS client::", "ModimWSClient::", "Reply:", "im.init()", "setDemoPathAuto", "qi.eventloop"]:
        if t in text:
            allowed = False
    return allowed


@contextmanager
def filtered_print(filter_func):
    original_stdout = sys.stdout
    sys.stdout = FilteredStdout(filter_func, original_stdout)
    try:
        yield
    finally:
        sys.stdout.flush()
        sys.stdout = original_stdout
