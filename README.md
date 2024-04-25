# International Mathematical Modeling Contest Data Analyzer

This program allows a user to provide a valid .csv file containing data from the Math Modeling Contest. This contest allows teams to compete internationally to create the best mathematical models to explain one of a
set of assigned problems. This file must contain the necessary columns for both institution and team data, including the following: Institution, Team Number, City, State/Province, Country, Advisor, Problem, & Ranking.

Once a valid .csv file with the neccesary columns has been provided, two separate Pandas dataframes are created, one containing data concerning institutions and the other data concerning teams. A sample .csv file has been provided with this project, titled *2015.csv*. These dataframes are used to populate a SQLite database, which is then queried to answer several pieces of information:
- Average number of teams entered per institution
- Institutions that entered the most teams, including the number of teams that they entered
- Institutions whose team(s) earned 'Outstanding' rankings (ordered by institution name)
- US teams who received 'Meritorious' ranking or better

The anaswers to these questions are written to a .txt file (titled *results.txt*), which is placed in the root directory.

To run this program, first clone this project:
```
git clone https://github.com/rjohnson05/MathModelingDataPreparation
```

Make sure that you have Python installed on your machine (can be installed [here](https://www.python.org/downloads/)). Ensure that you are in the root directory of the cloned project and start the program with the following:
```
py main.py
```
