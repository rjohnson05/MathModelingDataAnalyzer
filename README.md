# International Mathematical Modeling Contest Data Preparation

This program allows a user to provide a valid .csv file containing data from the Math Modeling Contest. This contest allows teams to compete internationally to create the best mathematical models to explain one of a
set of assigned problems. This file must contain the necessary columns for both institution and team data, including the following: Institution, Team Number, City, State/Province, Country, Advisor, Problem, & Ranking.
Once a valid .csv file with the neccesary columns has been provided, two separate .csv files are created, one containing data concerning institutions (titled *Institutions.csv*) and the other data concerning teams (titled *Teams.csv*). These files are saved in the root level of this project. A sample .csv file has been provided within this project, titled *2015.csv*. 

To run this program, first clone this project with the command `git clone https://github.com/rjohnson05/MathModelingDataPreparation`.
Make sure that you have Python installed on your machine, which can be installed [here](https://www.python.org/downloads/). Ensure that you are in the root directory of the cloned project and start the program by running `py main.py`.
