# gt-bds-f22-team5
GT CS6220 Fall 2022 - Group 5 Project

## PROJECT NAME
Analyzing Player and Team Chemistry/Performance in Soccer


## GROUP

### GROUP NUMBER
GROUP 5

### TEAM MEMBERS
1. Tusheet Sidharth Goli
2. Tejas Pradeep
3. Aman Jain
4. Akshay Pramod
5. Jeffrey Chang


## PACKAGE

### DESCRIPTION
The package contains two folders, the DOC and the CODE folders. The DOC folder contains the pdf copy of our team's final report which includes a detailed document specifying our project's integral aspects much similar to a research paper. It also contains a pdf copy of our team's poster presentation that we all used to make our presentation videos.

The CODE folder contains the entire codebase of our project (apart from a local copy of the dataset we used). Some of the files include the base requirements to run this project and the SQL database credentials that are hosted on a Heroku server. The src folder contains the backed data (API and SQL queries) and model (Graph Neural Network implementation) code. An important file here is the server.py file which is our Flask server that connects to the Heroku hosted database and orchestrates the API calls that the front end makes. We also have some local training files for the dataset that we use to pre-load our visualization tool. The viz directory contains our HTML files that are used to power and render the frontend. The important file here is the main.html file which must be run on localhost to launch the visualization tool.

We have not included the dataset in the CODE folder due to its large size, but here is a link to the dataset if you would like to see it (MySQL file) - https://drive.google.com/file/d/1MKyEEn-iP5vvZrH7LlYa-wBI4WApKytj/view?usp=sharing

### INSTALLATION
The necessary requirements for this project are outlined in our requirements.txt file. To install the requirements, we would suggest running it on an anaconda prompt (miniconda3) and installing the requirements by running "pip install -r requirements.txt" from the root directory. That should include most of the requirements you might need to run our server. If you run across any ModuleNotFoundErrors when trying to run the Flask server, you can manually install those dependencies by running "pip install {package-name}". This should help install all the requirements and dependencies you might need to run our project code.

### EXECUTION
The execution step can be divided into two steps, (1) running the Flask server and (2) starting the localhost connection to visualize the UI. Firstly, open two separate anaconda prompt (miniconda3) terminals. By this point, you should have installed all the dependencies from the previous step.

1. On the first miniconda3 terminal, cd into the src directory and run "python server.py" to start the Flask server. As mentioned previously, if you run across any ModuleNotFoundErrors when trying to run the Flask server, you can manually install those dependencies by running "pip install {package-name}". Once the server is up, you can proceed to step 2.

2. On the other miniconda3 terminal, cd into the src directory and run "python -m http.server" to start the Flask server. Now go to your browser and search "http://localhost:8000/". From the screen, select "viz" and then select "main.html". This should render our visualization that is backed by our Flask server to connect to the database.

From here on, most of the UI features are very intuitive.

* You can pre-load a team from the change team search bar. Once you select an option, hit the "Change Team" button. (Some teams might not be able to pre-load due to the lack of data/players. In that case, nothing will load on the screen and you can try to pick another team.)
* Calculate the performance score of a team, hit the "Get Performance" button on the right-hand side. (For a pre-existing team, the performance score should appear almost instantaneously. For a custom team (when you change players), it might take about 20-30seconds due to some complex calculations and speed-limit issues due to the Heroku hosted database. You can see the progress being made on the miniconda3 terminal running the server.)
* To replace a player, first click on any of the existing players on the screen. After that, you can use the filer options under "Replace a Player" to find the player you are looking for. You don't have to select an option for each filter as it will default to everything for that filter type. After that, hit "Apply Filter". You can select a player from the dropdown list and hit "Change Player" to replace the selected player. This might take a few seconds.
* To recalculate any scores, hit the "Get Performance" button on the right-hand side. As mentioned previously, it might take about 20-30seconds for a custom team.

## DEMO VIDEO
Link - https://youtu.be/igk_jDorMGQ
