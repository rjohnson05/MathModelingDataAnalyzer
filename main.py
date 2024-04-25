import sqlite3
import pandas as pd

"""
Allows a user to provide a .csv file containing data about the Math Modeling Contest and view the answers to several
analytical questions, creating a SQLite database to do so. The provided .csv file must have the correct format before 
creating two new spreadsheets: one containing only data about the institutions and the other providing information about 
the participating teams.

Author: Ryan Johnson
"""


def get_input_dataframe():
    """
    Prompts the user for the name of a .csv file. The provided name is then checked to ensure that it is a .csv file
    before checking that the file has the necessary columns. The provided name must be the valid location of a file. If
    any of these checks fail, an error is displayed and the user is prompted for another file name.

    :return: Pandas dataframe, having been validated for the correct column names
    """
    valid_file = False
    while not valid_file:
        file_name = input("Enter file name: ")
        # File must be a .csv file to be read by pandas
        while not file_name.endswith(".csv"):
            print("You must specify a valid .csv file")
            file_name = input("Enter file name: ")

        # Ensure the specified .csv file is a valid file
        try:
            df = pd.read_csv(file_name)
            # Ensure the file has the required columns
            if validate_dataframe(df):
                return df
        except FileNotFoundError:
            print(f"{file_name} couldn't be found")


def validate_dataframe(df):
    """
    Checks whether a dataframe has the necessary columns for splitting it into an Institutions and Teams dataframe.

    :param df: Pandas dataframe to be checked
    :return: True if the dataframe has the necessary columns; False otherwise
    """
    required_columns = ["Institution", "City", "State/Province", "Country"]
    columns_not_contained = []
    for title in required_columns:
        # Spreadsheet provided has junk in the Institution title, so accepts any column with 'Institution' contained
        # within the column title
        if title == "Institution":
            institution_found = False
            for column_title in df.columns:
                if "Institution" in column_title:
                    institution_found = True
                    break
            if not institution_found:
                columns_not_contained.append(title)
        elif title not in df.columns:
            columns_not_contained.append(title)
    if len(columns_not_contained) > 0:
        print(f"File doesn't contain the following required columns: {columns_not_contained}")
        return False
    return True


def prepare_data(df):
    """
    Loops through a dataframe with the necessary columns and creates two dataframes: one containing only data about
    institutions and the other only containing information about participating teams.

    :param df: Pandas dataframe to be used when creating new spreadsheets
    :return: Two Pandas dataframes: one containing only data about institutions and the other only data about teams
    """
    print("Preparing data for the database...")
    # Rename the institutions column if it has junk in the column name
    for column_name in df.columns:
        if "Institution" in column_name:
            df.rename(columns={column_name: "Institution"}, inplace=True)

    # Holds the unique ID numbers for institutions
    inst_id_counter = 0
    inst_ids = {}

    institutions_df = pd.DataFrame()
    teams_df = pd.DataFrame(columns=["Team Number", "Advisor", "Problem", "Ranking", "Institution ID"])
    for index, row in df.iterrows():
        # Add institution data from the row, cleaning the data before entering it into the new spreadsheet
        institution = row["Institution"]
        cleaned_institution = institution.split(", - ( )")[0].strip()
        lowercase_institution = cleaned_institution.lower()
        if lowercase_institution not in inst_ids.keys():
            inst_id_counter += 1
            inst_ids[lowercase_institution] = inst_id_counter
            row_institution = pd.DataFrame({'Institution ID': [inst_ids[lowercase_institution]],
                                            'Institution Name': [lowercase_institution.title()],
                                            'City': [row['City'].lower().title()],
                                            'State/Province': [row['State/Province'].lower().title() if type(
                                                row['State/Province']) is str else None],
                                            'Country': [row['Country'].lower().title() if type(
                                                row['Country']) is str else None]})
            institutions_df = pd.concat([institutions_df, row_institution], ignore_index=True)
            institutions_df = institutions_df.reset_index(drop=True)

        # Add team data from the row if the team isn't already present
        if not teams_df['Team Number'].isin([row['Team Number']]).any():
            row_team = pd.DataFrame({'Team Number': [row['Team Number']],
                                     'Advisor': [row['Advisor'].lower().title()],
                                     'Problem': [row['Problem'].capitalize() if type(row['Problem']) == str else None],
                                     'Ranking': [row['Ranking'].lower().title()],
                                     'Institution ID': [inst_ids[lowercase_institution]]})
            teams_df = pd.concat([teams_df, row_team], ignore_index=True)
            teams_df = teams_df.reset_index(drop=True)

    return institutions_df, teams_df


def populate_db(inst_df, teams_df):
    """
    Populates a SQLite database with the two cleaned dataframes. One dataframe contains institution data, and the other
    contains team data. Within the database, a table is created from each of the two dataframes. This database is later
    queried to produce a .txt file containing a few statistics.

    :param inst_df: Pandas dataframe containing data about the institutions participating in the competition
    :param teams_df: Pandas dataframe containing data about the teams participating in the competition
    """
    print("Populating the database...")
    conn = sqlite3.connect('math_competition.db')
    cursor = conn.cursor()

    # Populate the Institutions table
    cursor.execute("CREATE TABLE IF NOT EXISTS institutions (id INTEGER PRIMARY KEY, name VARCHAR, city VARCHAR, "
                   "state_province VARCHAR, country VARCHAR)")
    for index, row in inst_df.iterrows():
        name = row['Institution Name']
        cursor.execute("SELECT id FROM institutions WHERE name=?", (name,))
        # Ensure that no duplicate entries are placed into the DB
        if cursor.fetchone() is not None:
            print(f"Didn't put duplicate institution into the DB ({name})")
            continue

        inst_id = row['Institution ID']
        city = row['City']
        state_province = row['State/Province']
        country = row['Country']
        cursor.execute("INSERT INTO institutions (id, name, city, state_province, country) VALUES (?, ?, ?, ?, ?)",
                       (inst_id, name, city, state_province, country))

    # Populate the Teams table
    cursor.execute("CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY, advisor VARCHAR, problem VARCHAR, "
                   "ranking VARCHAR, institution_id INTEGER, FOREIGN KEY (institution_id) REFERENCES institutions(id))")
    for index, row in teams_df.iterrows():
        team_id = row['Team Number']
        cursor.execute("SELECT id FROM teams WHERE id=?", (team_id,))
        # Ensure that no duplicate entries are placed into the DB
        if cursor.fetchone() is not None:
            print(f"Didn't put duplicate team into the DB (#{team_id})")
            continue

        advisor = row['Advisor']
        problem = row['Problem']
        ranking = row['Ranking']
        inst_id = row['Institution ID']
        cursor.execute("INSERT INTO teams (id, advisor, problem, ranking, institution_id) VALUES (?, ?, ?, ?, ?)",
                       (team_id, advisor, problem, ranking, inst_id))

    conn.commit()
    conn.close()


def make_queries():
    """
    Queries the database to find the following pieces of information from the data:
      - Average number of teams entered per institution
      - Institutions that entered the most teams, including the number of teams that they entered
      - Institutions whose team(s) earned 'Outstanding' rankings (ordered by institution name)
      - US teams who received 'Meritorious' ranking or better

    :return: Results from each of the queries, each separate query result being contained in a list
    """
    conn = sqlite3.connect('math_competition.db')
    cursor = conn.cursor()

    # Determine average number of teams entered per institution
    cursor.execute("SELECT COUNT(*) FROM teams")
    num_teams = cursor.fetchall()[0][0]
    cursor.execute("SELECT COUNT(*) FROM institutions")
    num_insts = cursor.fetchall()[0][0]
    mean_num_teams = num_teams / num_insts

    # Determine the institutions that entered the most teams, including the number of teams that they entered
    cursor.execute("SELECT i.name, COUNT(*) "
                   "AS num_teams "
                   "FROM teams t "
                   "INNER JOIN institutions i ON i.id = t.institution_id "
                   "GROUP BY institution_id "
                   "ORDER BY num_teams DESC")
    ordered_insts = cursor.fetchall()

    # Determine the institutions whose team(s) earned 'Outstanding' rankings (ordered by institution name)
    cursor.execute("SELECT name "
                   "FROM institutions "
                   "WHERE id IN (SELECT institution_id FROM teams WHERE ranking='Outstanding Winner') "
                   "ORDER BY name")
    outstanding_insts = cursor.fetchall()

    # Determine the US teams who received 'Meritorious' ranking or better
    cursor.execute("SELECT t.id "
                   "FROM teams t "
                   "INNER JOIN institutions i ON t.institution_id=i.id "
                   "WHERE t.ranking IN ('Outstanding Winner', 'Finalist', 'Meritorious') AND i.country='Usa'")
    usa_meritorious_teams = cursor.fetchall()

    return mean_num_teams, ordered_insts, outstanding_insts, usa_meritorious_teams


def create_output_file(result1, result2, result3, result4):
    """
    Creates a .txt file that displays the following information from the database:
      - Average number of teams entered per institution
      - Institutions that entered the most teams, including the number of teams that they entered
      - Institutions whose team(s) earned 'Outstanding' rankings (ordered by institution name)
      - US teams who received 'Meritorious' ranking or better

    :param result1: List containing average number of teams entered per institution
    :param result2: List of tuples, the first element being the name of an institution and the second
                    element being the number of teams entered from the institution
    :param result3: List of all institutions that had at least one team with a ranking of 'Outstanding Winner'
    :param result4: List of ID numbers for all US teams that received ranking of 'Meritorious' or better
    """
    with open("results.txt", "w") as f:
        f.write(f"Average Number of Teams per Institution: {round(result1, 2)} teams\n")

        f.write("\nInstitutions Ordered by Number of Teams:\n")
        for inst in result2:
            f.write(f"  - {inst[0]}: {inst[1]} team(s)\n")

        f.write("\nInstitutions with Outstanding Winner(s):\n")
        for inst in result3:
            f.write(f"  - {str(inst[0])}\n")

        f.write("\nUS Teams Receiving Ranking of Meritorious or Better:\n")
        for inst in result4:
            f.write(f"  - {str(inst[0])}\n")


if __name__ == "__main__":
    print("Welcome to the Math Modeling Contest spreadsheet analyzer. To analyze data from a year's contest, "
          "enter the name of a valid .csv file.")
    df = get_input_dataframe()
    if not validate_dataframe(df):
        exit(1)

    inst_df, teams_df = prepare_data(df)
    populate_db(inst_df, teams_df)
    result1, result2, result3, result4 = make_queries()
    create_output_file(result1, result2, result3, result4)

    print("Your results file has been created and titled 'results.txt'")
