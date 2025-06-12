import qi
import argparse
import sys
import os
import sqlite3
import pandas as pd
import time
import random

from .motion import *
from .session_manager import *
from .animations import *


UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.dirname(UTILS_DIR)
AUDIO_DIR = os.path.join(MAIN_DIR, "audio")


def checkUsername():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 1 
        FROM clients 
        WHERE username = ?
        LIMIT 1
    ''', (username,))
    
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
    conn.close()

    for row in rows:
        print(" | ".join(str(item) if item is not None else "NULL" for item in row))


def checkFavourite():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fav_genre
        FROM clients 
        WHERE username = ?
    ''', (username,))

    result = cursor.fetchone()
    conn.close()

    has_favourite = "false" if result[0]==None else "true"
    ALMemory.raiseEvent("pepper-vinyl/has_favourite", has_favourite)

    if has_favourite == "true":
        favourite_genre = result[0][0]
        ALMemory.raiseEvent("pepper-vinyl/favourite_genre", favourite_genre)


def checkStorage():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    vinyl_name = ALMemory.getData("pepper-vinyl/vinyl_name")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT quantity
        FROM  vinyls
        WHERE vinyl = ?
    ''', (vinyl_name,))

    result = cursor.fetchone()
    conn.close()

    if result == None:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_found", "unknown")
    
    elif result[0] == 0:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_found", "out_of_stock")
    
    else:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_found", "available")


def orderVinyl():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")
    vinyl_name = ALMemory.getData("pepper-vinyl/vinyl_name")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (vinyl,client,status)
        VALUES (?, ?, ?)
    ''', (vinyl_name, username, "pending"))
    conn.commit()
    conn.close()


def guideClient():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")
    vinyl_name = ALMemory.getData("pepper-vinyl/vinyl_name")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT x, y
        FROM  vinyls
        WHERE vinyl = ?
    ''', (vinyl_name,))

    result = cursor.fetchone()

    move_to(result[0], result[1], None)
    offer_item()
    rotate("behind")

    cursor = conn.cursor()
    cursor.execute('''
        UPDATE vinyls
        SET quantity = quantity - 1
        WHERE vinyl = ?
    ''', (vinyl_name,))
    conn.commit()

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buys (client,vinyl)
        VALUES (?, ?)
    ''', (username, vinyl_name))
    conn.commit()

    conn.close()

    ALMemory.raiseEvent("pepper-vinyl/finish_wait", "true")


def takeAndGoBack():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')
    ALMotion = manager.session.service('ALMotion')

    username = ALMemory.getData("pepper-vinyl/username")
    vinyl_name = ALMemory.getData("pepper-vinyl/vinyl_name")

    current_pose = ALMotion.getRobotPosition(False)
    initial_x, initial_y = current_pose[0], current_pose[1]

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT x, y
        FROM  vinyls
        WHERE vinyl = ?
    ''', (vinyl_name,))

    result = cursor.fetchone()

    move_to(result[0], result[1], None)
    reach_and_grab()
    move_to(initial_x, initial_y, None)
    offer_item()

    cursor = conn.cursor()
    cursor.execute('''
        UPDATE vinyls
        SET quantity = quantity - 1
        WHERE vinyl = ?
    ''', (vinyl_name,))
    conn.commit()

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buys (client,vinyl)
        VALUES (?, ?)
    ''', (username, vinyl_name))
    conn.commit()

    conn.close()

    ALMemory.raiseEvent("pepper-vinyl/finish_wait", "true")


def setFavourite():
    
    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")
    favourite_genre = ALMemory.getData("pepper-vinyl/favourite_genre")
    
    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))

    if favourite_genre != "anything":

        cursor = conn.cursor()
        cursor.execute('''
            SELECT genre
            FROM vinyls
        ''')
        result = cursor.fetchall()
        all_genres = [str(i[0]) for i in result]

    if favourite_genre == "anything" or favourite_genre in all_genres:

        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (username,fav_genre)
            VALUES (?, ?)
        ''', (username, favourite_genre))
        conn.commit()

        ALMemory.raiseEvent("pepper-vinyl/genre_recognized", "true")
    
    else:
        ALMemory.raiseEvent("pepper-vinyl/genre_recognized", "false")

    conn.close()


def findSuggestion():
    
    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    favourite_genre = ALMemory.getData("pepper-vinyl/favourite_genre")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))

    if favourite_genre == "anything":
        
        # BASELINE
        cursor = conn.cursor()
        cursor.execute('''
            SELECT genre
            FROM vinyls
        ''')
        result = cursor.fetchall()
        selected_genre = random.choice(result)[0]

    else:
        selected_genre = favourite_genre

    ALMemory.raiseEvent("pepper-vinyl/selected_genre", selected_genre)

    cursor = conn.cursor()
    cursor.execute('''
        SELECT vinyl
        FROM vinyls 
        WHERE genre = ? AND quantity>0
        ORDER BY release_date DESC
    ''', (selected_genre,))

    # take the newest vinyl
    result = cursor.fetchone()
    conn.close()
    result = str(result[0])

    ALMemory.raiseEvent("pepper-vinyl/suggestion", result)
        

def playDemo():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')
    ALAudioPlayer = manager.session.service("ALAudioPlayer")

    file_name = "classical1.wav"
    file_path = os.path.join(AUDIO_DIR, file_name)
    #ALAudioPlayer.playFile(file_path)
    dance_to_music()

    ALMemory.raiseEvent("pepper-vinyl/finish_wait", "true")



def reset():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    bow()

    for key in ALMemory.getDataList("pepper-vinyl/"):
        ALMemory.insertData(key, "")
        print("Deleted: {}".format(key))

    move_to(0.0, 0.0, 0.0)


def pointToVinyl():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')
    ALTracker = manager.session.service('ALTracker')

    vinyl_name = ALMemory.getData("pepper-vinyl/vinyl_name")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT x, y
        FROM  vinyls
        WHERE vinyl = ?
    ''', (vinyl_name,))

    result = cursor.fetchone()
    conn.close()

    ALTracker.pointAt("RArm", [result[0], result[1], 1.0], 1, 1.0)
    ALTracker.lookAt([result[0], result[1], 1.0], 1, 1.0, True)


    ALMemory.raiseEvent("pepper-vinyl/finish_wait", "true")


def handleFunction(value):

    if value == "check_username":
        checkUsername()

    elif value == "check_favourite":
        checkFavourite()

    elif value == "check_storage":
        checkStorage()

    elif value == "order_vinyl":
        orderVinyl()

    elif value == "guide_client":
        guideClient()
    
    elif value == "take_and_go_back":
        takeAndGoBack()
    
    elif value == "set_favourite":
        setFavourite()
    
    elif value == "find_suggestion":
        findSuggestion()
    
    elif value == "play_demo":
        playDemo()

    elif value == "reset":
        reset()

    elif value == "point_to_vinyl":
        pointToVinyl()

    else:
        raise ValueError("handler not found for value {}".format(value))