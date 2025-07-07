# pepper-vinyl-shop

Project developed for the modules of "Human-Robot Interaction" and "Robot Benchmarking and Competitions" within the course of "Elective in Artificial Intelligence" during the MSc in Artificial Intelligence and Robotics at Sapienza University of Rome, A.Y. 2024-2025.


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

6. Access to choregraphe from [http://localhost:3000](http://localhost:3000) and activate pepper with the key from [here](https://aldebaran.com/en/support/kb/softwares/downloads-softwares/pepper-2-5-downloads/)
  
7. Load pepper from "settings" and read its port, load the layout provided in the repository from "view"

8. Start the modim web server (from window 3 of the tmux session)

    ```bash
    cd ~/src/modim/src/GUI
    export PEPPER_PORT=<port>
    python ws_server.py -robot pepper
    ```

9.  Open the modim page (from a new terminal window)

    ```bash
    cd path/to/hri_software/docker
    ./run_nginx.bash path/to/pepper-vinyl-shop/tablet
    ```

10. Access to modim from [http://localhost:80](http://localhost:80)

11. Start the program (from window 4 of the tmux session)

    ```bash
    cd path/to/pepper-vinyl-shop
    python main.py
    ```
