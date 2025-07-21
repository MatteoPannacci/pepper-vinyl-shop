# pepper-vinyl-shop

Project developed for the modules of "Human-Robot Interaction" and "Robot Benchmarking and Competitions" within the course of "Elective in Artificial Intelligence" during the MSc in Artificial Intelligence and Robotics at Sapienza University of Rome, A.Y. 2024-2025.


# Summary

**Pepper Vinyl Shop Assistant** is an interactive robotic assistant built on the SoftBank Pepper platform for intelligent customer service in a vinyl music store. It combines multimodal interaction, including natural speech, gesture, tablet UI, and emotion-aware behavior, with personalized music recommendations using SQL logic and LightGCN collaborative filtering. The system recognizes returning users, adapts to their preferences, detects indecision, and physically assists by guiding or pointing to vinyl locations. 

Key features include emotion-driven music suggestions powered by a CNN, real-time dialog via ALDialog and MODIM, and a memory-driven recommendation system. Evaluated with strong performance metrics and ethical HRI principles, the project demonstrates a modular, deployable architecture for socially intelligent retail robotics.



# How to run


1. Clone the [hri_software repository](https://bitbucket.org/iocchi/hri_software/src/master/)

2. Follow the docker installation instructions

3. Run the docker container

    ```bash
    cd path/to//hri_software/docker
    ./run.bash vnc
    ```

4. Connect to the pepperhri docker and start a tmux session (from a new terminal)

    ```bash
    docker exec -it pepperhri tmux a
    ```

5. Start the choregraphe application (from window 1 of the tmux session)

    ```bash
    cd /opt/Aldebaran/choregraphe-suite-2.5.10.7-linux64
    ./choregraphe
    ```

6. Access to choregraphe from [http://localhost:3000](http://localhost:3000) and setup the instance:

    1. Activate pepper with the key from [here](https://aldebaran.com/en/support/kb/softwares/downloads-softwares/pepper-2-5-downloads/)
  
    2. Load pepper from "edit -> preferences -> virtual robot" and read its port
    
    3. Load the choregraphe layout provided in the repository from "view -> load layout"

    4. Load the choregraphe project present on the repository from "file -> open project"

    5. Connect to the robot with "connection -> Connect to virtual robot"

    6. Upload the project on the robot with "Upload to the robot and Play"

7. Start the modim web server (from window 3 of the tmux session)

    ```bash
    cd ~/src/modim/src/GUI
    export PEPPER_PORT=<port>
    python ws_server.py -robot pepper
    ```

8. Open the modim page (from a new terminal window)

    ```bash
    cd path/to/hri_software/docker
    ./run_nginx.bash path/to/pepper-vinyl-shop/tablet
    ```

9. Access to modim from [http://localhost:80](http://localhost:80)

10. Train the emotion classifier

    ```bash
    cd path/to/pepper-vinyl-shop
    python train_classifier.py
    ```

11. Start the program (from window 4 of the tmux session)

    ```bash
    cd path/to/pepper-vinyl-shop
    python main.py --pport $PEPPER_PORT
    ```
