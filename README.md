# pepper-vinyl-shop

Project developed for the modules of "Human-Robot Interaction" and "Robot Benchmarking and Competitions" within the course of "Elective in Artificial Intelligence" during the MSc in Artificial Intelligence and Robotics at Sapienza University of Rome, A.Y. 2024-2025.


# How to run

Requires hri_software (link repo)


--- RUN DOCKER CONTAINERS ---
cd .../hri_software/docker
./run.bash vnc

--- START DOCKER --- (on a new terminal)
docker exec -it pepperhri tmux a

on tmux 1: ./choregraphe
on tmux 3: export PEPPER_PORT=<port>
           python ws_server.py -robot pepper

on new terminal
cd .../hri_software/docker
./run_nginx.bash .../pepper-vinyl-shop/tablet



--- PEPPER ACTIVATION CHOREGRAPHE --- (link site)
654e-4564-153c-6518-2f44-7562-206e-4c60-5f47-5f45


access to choregraphe: http://localhost:3000

access to modim: http://localhost:80