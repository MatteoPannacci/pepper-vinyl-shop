import qi
import argparse
import sys
import os
import sqlite3
import pandas as pd
import time
import random
import string
import ast
from datetime import date

from .motion import *
from .session_manager import *
from .animations import *
from .tablet import create_dynamic_action
from .neural_recommendation import *
from .emotion_recognition import *


UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.dirname(UTILS_DIR)
AUDIO_DIR = os.path.join(MAIN_DIR, "audio")
EMOTIONS_DIR = os.path.join(MAIN_DIR, "data/emotions/test")


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
            INSERT INTO clients (username, fav_genre, fav_author, last_visit)
            VALUES (?, ?, ?, ?)
        ''', (username, None, None, None))
        conn.commit()
        print("new entry in CLIENTS: <{},{},{},{}>".format(username, None, None, None))

    conn.close()


def checkFavouriteGenre():

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

    has_favourite_genre = "false" if result==None else "true"
    ALMemory.raiseEvent("pepper-vinyl/has_favourite_genre", has_favourite_genre)

    if has_favourite_genre == "true":
        favourite_genre = result[0]
        ALMemory.raiseEvent("pepper-vinyl/favourite_genre", favourite_genre)


def checkFavouriteAuthor():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fav_author
        FROM clients 
        WHERE username = ?
    ''', (username,))

    result = cursor.fetchone()
    conn.close()

    has_favourite_author = "false" if result==None else "true"
    ALMemory.raiseEvent("pepper-vinyl/has_favourite_author", has_favourite_author)

    if has_favourite_author == "true":
        favourite_author = result[0]
        ALMemory.raiseEvent("pepper-vinyl/favourite_author", favourite_author)


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
        INSERT INTO buys (client,vinyl)
        VALUES (?, ?)
    ''', (username, vinyl_name))
    print("new entry in BUYS: <{},{}>".format(username, vinyl_name))


    cursor.execute('''
        INSERT INTO orders (vinyl,client,status)
        VALUES (?, ?, ?)
    ''', (vinyl_name, username, "pending"))
    print("new entry in ORDERS: <{},{}, {}>".format(username, vinyl_name, "pending"))


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
        SELECT x, y, quantity
        FROM  vinyls
        WHERE vinyl = ?
    ''', (vinyl_name,))

    result = cursor.fetchone()
    quantity = int(result[2])

    move_to(result[0], result[1], None)
    offer_item()
    rotate("behind")

    cursor = conn.cursor()
    cursor.execute('''
        UPDATE vinyls
        SET quantity = ?
        WHERE vinyl = ?
    ''', (quantity-1, vinyl_name))
    print("updated quantity in VINYLS entry {}: {}".format(vinyl_name, quantity-1))
    conn.commit()

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buys (client,vinyl)
        VALUES (?, ?)
    ''', (username, vinyl_name))
    print("new entry in BUYS: <{},{}>".format(username, vinyl_name))
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
        SELECT x, y, quantity
        FROM  vinyls
        WHERE vinyl = ?
    ''', (vinyl_name,))

    result = cursor.fetchone()
    quantity = int(result[2])

    move_to(result[0], result[1], None)
    reach_and_grab()
    move_to(initial_x, initial_y, None)
    offer_item()

    cursor = conn.cursor()
    cursor.execute('''
        UPDATE vinyls
        SET quantity = ?
        WHERE vinyl = ?
    ''', (quantity-1, vinyl_name))
    print("updated quantity in VINYLS entry {}: {}".format(vinyl_name, quantity-1))
    conn.commit()

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO buys (client,vinyl)
        VALUES (?, ?)
    ''', (username, vinyl_name))
    print("new entry in BUYS: <{},{}>".format(username, vinyl_name))
    conn.commit()

    conn.close()

    ALMemory.raiseEvent("pepper-vinyl/finish_wait", "true")


def setFavouriteGenre():
    
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
            UPDATE clients (username,fav_genre,fav_author)
            SET fav_genre = ?
            WHERE username = ?
        ''', (favourite_genre, username))
        print("updated fav_genre in CLIENTS entry {}: {}".format(username, favourite_genre))
        conn.commit()

        ALMemory.raiseEvent("pepper-vinyl/genre_recognized", "true")
    
    else:
        ALMemory.raiseEvent("pepper-vinyl/genre_recognized", "false")

    conn.close()


def setFavouriteAuthor():
    
    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")
    favourite_author = ALMemory.getData("pepper-vinyl/favourite_author")
    
    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))

    if favourite_author != "anything":

        cursor = conn.cursor()
        cursor.execute('''
            SELECT author
            FROM vinyls
        ''')
        result = cursor.fetchall()
        all_authors = [str(i[0]) for i in result]

    if favourite_author == "anything" or favourite_author in all_authors:

        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clients (username,fav_genre,fav_author)
            SET fav_author = ?
            WHERE username = ?
        ''', (favourite_author, username))
        print("updated fav_author in CLIENTS entry {}: {}".format(username, favourite_author))
        conn.commit()

        ALMemory.raiseEvent("pepper-vinyl/author_recognized", "true")
    
    else:
        ALMemory.raiseEvent("pepper-vinyl/author_recognized", "false")

    conn.close()


def findSuggestionGenre():
    
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


def findSuggestionAuthor():
    
    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    favourite_author = ALMemory.getData("pepper-vinyl/favourite_author")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))

    if favourite_author == "anything":
        
        # BASELINE
        cursor = conn.cursor()
        cursor.execute('''
            SELECT author
            FROM vinyls
        ''')
        result = cursor.fetchall()
        selected_author = random.choice(result)[0]

    else:
        selected_author = favourite_author

    ALMemory.raiseEvent("pepper-vinyl/selected_author", selected_author)

    cursor = conn.cursor()
    cursor.execute('''
        SELECT vinyl
        FROM vinyls 
        WHERE author = ? AND quantity>0
        ORDER BY release_date DESC
    ''', (selected_author,))

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

    reaction = random.choice(["happy", "neutral", "disgusted"])
    print("User reaction: {}".format(reaction))

    image_path = os.path.join(EMOTIONS_DIR, reaction, "im{}.png".format(random.randint(0,100)))
    print("Image chosen: {}".format(image_path))

    predicted = str(predict_emotion(image_path, "./models/classifier"))
    print("Predicted reaction: {}".format(predicted))

    ALMemory.raiseEvent("pepper-vinyl/reaction", predicted)
    ALMemory.raiseEvent("pepper-vinyl/true_reaction", reaction)
    ALMemory.raiseEvent("pepper-vinyl/finish_wait", "true")


def reset():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    ALMemory.raiseEvent("pepper-vinyl/counter", "0")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE clients
        SET last_visit = ?
        WHERE username = ?
    ''', (date.today(), username))
    print("updated last_visit in CLIENTS entry {}: {}".format(username, date.today()))
    conn.commit()

    conn.close()

    for key in ALMemory.getDataList("pepper-vinyl/"):
        ALMemory.insertData(key, "")
        print("Deleted: {}".format(key))

    move_to(0.0, 0.0, 0.0)

    ALMemory.raiseEvent("pepper-vinyl/finish_wait", "true")


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


def checkInteractions():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 1
        FROM  buys
        WHERE client = ?
    ''', (username,))

    result = cursor.fetchone()
    conn.close()

    has_interactions = "false" if result==None else "true"
    ALMemory.raiseEvent("pepper-vinyl/has_interactions", has_interactions)


def recommendations():
    
    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    train_model(
        hidden_dim=64,
        epochs=150, # changed for not making the user wait too much
        lr=0.01,
        num_samples=1024
    )

    recommendations = give_recommendations(username)
    rec_string = ""
    for i in recommendations:
        rec_string += " '{}',".format(i)
    rec_string = rec_string[:-1]

    ALMemory.raiseEvent("pepper-vinyl/recommendations", rec_string) 


def checkRecommendationRequest():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    request = ALMemory.getData("pepper-vinyl/request")

    recommendations = ALMemory.getData("pepper-vinyl/recommendations")
    recommendations = list(ast.literal_eval("(%s,)" % recommendations))

    # FILTER THE REQUEST?

    if request in recommendations:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_recognized", "true")
        ALMemory.raiseEvent("pepper-vinyl/vinyl_name", request)
    
    else:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_recognized", "false")


def checkTodayRequest():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    request = ALMemory.getData("pepper-vinyl/request")

    today_releases = ALMemory.getData("pepper-vinyl/today_releases")
    today_releases = list(ast.literal_eval("(%s,)" % today_releases))

    if request in today_releases:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_recognized", "true")
        ALMemory.raiseEvent("pepper-vinyl/vinyl_name", request)
    
    else:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_recognized", "false")


def checkAuthorRequest():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    request = ALMemory.getData("pepper-vinyl/request")

    author_releases = ALMemory.getData("pepper-vinyl/author_releases")
    author_releases = list(ast.literal_eval("(%s,)" % author_releases))

    if request in author_releases:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_recognized", "true")
        ALMemory.raiseEvent("pepper-vinyl/vinyl_name", request)
    
    else:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_recognized", "false")


def checkGenreRequest():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    request = ALMemory.getData("pepper-vinyl/request")

    genre_releases = ALMemory.getData("pepper-vinyl/genre_releases")
    genre_releases = list(ast.literal_eval("(%s,)" % genre_releases))

    if request in genre_releases:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_recognized", "true")
        ALMemory.raiseEvent("pepper-vinyl/vinyl_name", request)
    
    else:
        ALMemory.raiseEvent("pepper-vinyl/vinyl_recognized", "false")


def chitChat():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM clients
        WHERE username = ?
    ''', (username,))

    _, fav_genre, fav_author, last_visit = cursor.fetchone()

    ALMemory.raiseEvent("pepper-vinyl/favourite_genre", fav_genre)
    ALMemory.raiseEvent("pepper-vinyl/favourite_author", fav_author)
    ALMemory.raiseEvent("pepper-vinyl/last_visit", last_visit)

    today = date.today()

    # check arrived order
    cursor.execute('''
        SELECT *
        FROM orders
        WHERE client = ? AND status = 'arrived'
    ''', (username,))

    orders = cursor.fetchall()
    orders = [str(i[0]) for i in orders]
    
    if len(orders) > 0:

        orders_string = ""
        for i in orders:
            orders_string += " '{}',".format(i)
        orders_string = orders_string[:-1]
    
        ALMemory.raiseEvent("pepper-vinyl/orders", orders_string)
        ALMemory.raiseEvent("pepper-vinyl/chit_chat", "orders_arrived")
        conn.close()
        return

    extraction = []

    # check today release
    cursor.execute('''
        SELECT *
        FROM vinyls
        WHERE release_date = ? AND quantity > 0
        LIMIT 5
    ''', (today,))

    today_releases = cursor.fetchall()
    today_releases = [str(i[0]) for i in today_releases]

    if len(today_releases) > 0:

        today_releases_string = ""
        for i in today_releases:
            today_releases_string += " '{}',".format(i)
        today_releases_string = today_releases_string[:-1]

        extraction.append("today_releases")
        ALMemory.raiseEvent("pepper-vinyl/today_releases", today_releases_string)

    # check new from favourite author
    cursor.execute('''
        SELECT *
        FROM vinyls
        WHERE author = ? AND release_date > ? AND release_date <= ?
        LIMIT 5
    ''', (fav_author, last_visit, today))

    author_releases = cursor.fetchall()
    author_releases = [str(i[0]) for i in author_releases]

    if len(author_releases) > 0:

        author_releases_string = ""
        for i in author_releases:
            author_releases_string += " '{}',".format(i)
        author_releases_string = author_releases_string[:-1]

        extraction.append("author_releases")
        ALMemory.raiseEvent("pepper-vinyl/author_releases", author_releases_string)

    # check new from favourite genre
    cursor.execute('''
        SELECT *
        FROM vinyls
        WHERE genre = ? AND release_date > ? AND release_date <= ?
        LIMIT 5
    ''', (fav_genre, last_visit, today))

    genre_releases = cursor.fetchall()
    genre_releases = [str(i[0]) for i in genre_releases]

    if len(genre_releases) > 0:

        genre_releases_string = ""
        for i in genre_releases:
            genre_releases_string += " '{}',".format(i)
        genre_releases_string = genre_releases_string[:-1]

        extraction.append("genre_releases")
        ALMemory.raiseEvent("pepper-vinyl/genre_releases", genre_releases_string)

    if len(extraction) == 0:
        ALMemory.raiseEvent("pepper-vinyl/chit_chat", "nothing")
        conn.close()

    else:
        ALMemory.raiseEvent("pepper-vinyl/chit_chat", random.choice(extraction))
        conn.close()


def saveRating():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/rating")
    rating = ALMemory.getData("pepper-vinyl/username")

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ratings (username,rating)
        VALUES (?, ?)
    ''', (username, rating))
    print("new entry in RATINGS: <{},{}>".format(username, rating))
    conn.commit()


def checkCounter():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    counter = int(ALMemory.getData("pepper-vinyl/counter")) + 1
    ALMemory.raiseEvent("pepper-vinyl/counter", str(counter))

    if counter >= 3:
        ALMemory.raiseEvent("pepper-vinyl/undecided", "true")
    else:
        ALMemory.raiseEvent("pepper-vinyl/undecided", "false")


def userPassing():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')
    ALMemory.raiseEvent("pepper-vinyl/user_passing", "true")


def handleFunction(value):

    if value == "check_username":
        checkUsername()

    elif value == "check_favourite_genre":
        checkFavouriteGenre()

    elif value == "check_favourite_author":
        checkFavouriteAuthor()

    elif value == "check_storage":
        checkStorage()

    elif value == "order_vinyl":
        orderVinyl()

    elif value == "guide_client":
        guideClient()

    elif value == "take_and_go_back":
        takeAndGoBack()

    elif value == "set_favourite_genre":
        setFavouriteGenre()

    elif value == "set_favourite_author":
        setFavouriteAuthor()

    elif value == "find_suggestion_genre":
        findSuggestionGenre()

    elif value == "find_suggestion_author":
        findSuggestionAuthor()

    elif value == "play_demo":
        playDemo()

    elif value == "reset":
        reset()

    elif value == "point_to_vinyl":
        pointToVinyl()

    elif value == "check_interactions":
        checkInteractions()

    elif value == "recommendations":
        recommendations()

    elif value == "check_recommendation_request":
        checkRecommendationRequest()

    elif value == "chit_chat":
        chitChat()

    elif value == "check_today_request":
        checkTodayRequest()

    elif value == "check_author_request":
        checkAuthorRequest()

    elif value == "check_genre_request":
        checkGenreRequest()

    elif value == "greeting_animation":
        greeting_animation()

    elif value == "idle_animation_1":
        idle_animation_1()

    elif value == "idle_animation_2":
        idle_animation_2()
    
    elif value == "idle_animation_3":
        idle_animation_3()

    elif value == "thinking_animation":
        thinking_animation()

    elif value == "bow":
        bow()

    elif value == "reset_posture":
        reset_posture()

    elif value == "save_rating":
        saveRating()

    elif value == "check_counter":
        checkCounter()

    elif value == "user_passing":
        userPassing()

    else:
        raise ValueError("handler not found for value {}".format(value))

# TABLET STARTS HERE

def handleTablet(value, finish=True):

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    mode, action = value.split("_")

    if mode == "ask":
        answer = manager.ask_modim(action)
    
    elif mode == "execute":
        manager.execute_modim(action)
        answer = ""

    if finish:
        ALMemory.raiseEvent("pepper-vinyl/answer", answer)
        ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")

    return answer



def welcomeOldUser():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    create_dynamic_action(
        image = "welcome.png",
        text = "Hi {}! Welcome back to our shop!".format(username),
        action_name = "welcome-old"
    )

    handleTablet("execute_welcome-old")


def welcomeNewUser():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    username = ALMemory.getData("pepper-vinyl/username")

    create_dynamic_action(
        image = "welcome.png",
        text = "Hi {}! Nice to meet you!".format(username),
        action_name = "welcome-new"
    )

    handleTablet("execute_welcome-new")


def showVinyls():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    conn = sqlite3.connect(os.path.join(MAIN_DIR, "data/database.db"))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT vinyl
        FROM  vinyls
        ORDER BY vinyl
    ''')

    result = cursor.fetchall()
    conn.close()

    result = [str(i[0]) for i in result]

    vinyls_per_page = 6
    current = list(range(vinyls_per_page))
    finish = False

    while not finish:

        current_vinyls = [result[i] for i in current]
        buttons = ["<-"] + current_vinyls + ["->"]

        create_dynamic_action(
            image = "vinyls.png",
            text = "Here are the available vinyls:",
            buttons = buttons,
            action_name = "show-vinyls"
        )

        answer = handleTablet("ask_show-vinyls", finish=False)

        if answer == "<-":
            current = [(i-vinyls_per_page)%len(result) for i in current]
        elif answer == "->":
            current = [(i+vinyls_per_page)%len(result) for i in current]
        elif answer in current_vinyls:
            finish = True
        elif answer == "00":
            return

    ALMemory.raiseEvent("pepper-vinyl/answer", answer)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")


def nameFromKeyboard():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    letters = list(string.ascii_lowercase)
    buttons = letters + ["<=", "enter"]
    
    username = ""
    finish = False

    while not finish:

        create_dynamic_action(
            image = "name.png",
            text = "Your name is: {}".format(username),
            buttons = buttons,
            action_name = "ask-name"
        )

        answer = handleTablet("ask_ask-name", finish=False)
        
        if answer == "enter":
            finish = True
        elif answer == "<=":
            if len(username) > 0:
                username = str(username[:-1])
        elif answer in letters:
            username = username + answer
        elif answer == "00":
            return
        elif ALMemory.getData("pepper-vinyl/username") != "":
            return
    
    ALMemory.raiseEvent("pepper-vinyl/answer", username)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")


def orderVinyl():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    vinyl_name = ALMemory.getData("pepper-vinyl/vinyl_name")

    create_dynamic_action(
        image = "vinyl.png",
        text = "We don't have '{}' in storage right now. Do you want to order it?".format(vinyl_name),
        buttons = ["yes", "no"],
        action_name = "order-vinyl"
    )

    answer = handleTablet("ask_order-vinyl")

    ALMemory.raiseEvent("pepper-vinyl/answer", answer)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")


def showRecommendations():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    recommendations = ALMemory.getData("pepper-vinyl/recommendations")
    recommendations = list(ast.literal_eval("(%s,)" % recommendations))
    recommendations.append("back")

    create_dynamic_action(
        image = "vinyls.png",
        text = "Here are some recommendations:",
        buttons = recommendations,
        action_name = "show-recommendations"
    )

    answer = handleTablet("ask_show-recommendations")

    ALMemory.raiseEvent("pepper-vinyl/answer", answer)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")


def showTodayReleases():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    today_releases = ALMemory.getData("pepper-vinyl/today_releases")
    today_releases = list(ast.literal_eval("(%s,)" % today_releases))
    today_releases.append("back")

    create_dynamic_action(
        image = "vinyls.png",
        text = "Here are some releases from today:",
        buttons = today_releases,
        action_name = "show-today-releases"
    )

    answer = handleTablet("ask_show-today-releases")

    ALMemory.raiseEvent("pepper-vinyl/answer", answer)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")


def showAuthorReleases():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    fav_author = ALMemory.getData("pepper-vinyl/favourite_author")

    author_releases = ALMemory.getData("pepper-vinyl/author_releases")
    author_releases = list(ast.literal_eval("(%s,)" % author_releases))
    author_releases.append("back")

    create_dynamic_action(
        image = "vinyls.png",
        text = "Here are some recent releases from {}:".format(fav_author),
        buttons = author_releases,
        action_name = "show-author-releases"
    )

    answer = handleTablet("ask_show-author-releases")

    ALMemory.raiseEvent("pepper-vinyl/answer", answer)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")



def showGenreReleases():
    
    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    fav_genre = ALMemory.getData("pepper-vinyl/favourite_genre")

    genre_releases = ALMemory.getData("pepper-vinyl/genre_releases")
    genre_releases = list(ast.literal_eval("(%s,)" % genre_releases))
    genre_releases.append("back")

    create_dynamic_action(
        image = "vinyls.png",
        text = "Here are some recent releases in the genre of {}:".format(fav_genre),
        buttons = genre_releases,
        action_name = "show-genre-releases"
    )

    answer = handleTablet("ask_show-genre-releases")

    ALMemory.raiseEvent("pepper-vinyl/answer", answer)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")


def showSuggestionGenre():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    selected_genre = ALMemory.getData("pepper-vinyl/selected_genre")
    suggestion = ALMemory.getData("pepper-vinyl/suggestion")

    create_dynamic_action(
        image = "vinyl.png",
        text = "Here is the newest vinyl from {}: '{}'. Do you want to listen to a demo?".format(selected_genre, suggestion),
        buttons = ["yes", "no"],
        action_name = "show-suggestion"
    )    

    answer = handleTablet("ask_show-suggestion")

    ALMemory.raiseEvent("pepper-vinyl/answer", answer)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")


def showSuggestionAuthor():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    selected_author = ALMemory.getData("pepper-vinyl/selected_author")
    suggestion = ALMemory.getData("pepper-vinyl/suggestion")

    create_dynamic_action(
        image = "vinyl.png",
        text = "Here is the newest vinyl from {}: '{}'. Do you want to listen to a demo?".format(selected_author, suggestion),
        buttons = ["yes", "no"],
        action_name = "show-suggestion"
    )

    answer = handleTablet("ask_show-suggestion")

    ALMemory.raiseEvent("pepper-vinyl/answer", answer)
    ALMemory.raiseEvent("pepper-vinyl/tablet_finish", "true")


def playingMusic():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    vinyl_name = ALMemory.getData("pepper-vinyl/vinyl_name")

    create_dynamic_action(
        image = "music.png",
        text = "Playing the demo of '{}' !".format(vinyl_name),
        action_name = "play-music"
    )

    answer = handleTablet("execute_play-music")


def showOrders():

    manager = SessionManager()
    ALMemory = manager.session.service('ALMemory')

    orders = ALMemory.getData("pepper-vinyl/orders")    

    create_dynamic_action(
        image = "vinyls.png",
        text = "Some of your orders arrived: {} ! You can get them from the cashier.".format(orders),
        action_name = "show-orders"
    )

    answer = handleTablet("execute_show-orders")


def handleTabletDynamic(value):

    if value == "welcome_old_user":
        welcomeOldUser()
    
    elif value == "welcome_new_user":
        welcomeNewUser()

    elif value == "show_vinyls":
        showVinyls()
    
    elif value == "name_from_keyboard":
        nameFromKeyboard()

    elif value == "order_vinyl":
        orderVinyl()

    elif value == "show_recommendations":
        showRecommendations()

    elif value == "show_today_releases":
        showTodayReleases()

    elif value == "show_author_releases":
        showAuthorReleases()

    elif value == "show_genre_releases":
        showGenreReleases()

    elif value == "show_suggestion_genre":
        showSuggestionGenre()

    elif value == "show_suggestion_author":
        showSuggestionAuthor()

    elif value == "playing_music":
        playingMusic()

    elif value == "show_orders":
        showOrders()

    else:
        raise ValueError("handler not found for value {}".format(value))