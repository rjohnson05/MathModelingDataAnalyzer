import pandas as pd

"""
Allows a user to provide a .csv file containing data about the Math Modeling Contest. This file must have the correct 
format before creating two new spreadsheets: one containing only data about the institutions and the other providing 
information about the participating teams.

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
    Checks whether a dataframe has the necessary columns for splitting it into an Institutions and Teams spreadsheet.

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
    Loops through a dataframe with the necessary columns and creates two spreadsheets: one containing only data about
    institutions and the other only containing information about participating teams.

    :param df: Pandas to be used when creating new spreadsheets
    """
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
        cleaned_institution = institution.split(",")[0].strip()
        lowercase_institution = cleaned_institution.lower()
        if lowercase_institution not in inst_ids.keys():
            inst_id_counter += 1
            inst_ids[lowercase_institution] = inst_id_counter
            row_institution = pd.DataFrame({'Institution ID': [inst_ids[lowercase_institution]],
                                            'Institution Name': [lowercase_institution.title()],
                                            'City': [row['City'].lower().title()],
                                            'State/Province': [row['State/Province'].lower().title() if type(row['State/Province']) is str else None],
                                            'Country': [row['Country'].lower().title() if type(row['Country']) is str else None]})
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

    # Generate institution and team .csv files using these created dataframes
    institutions_df.to_csv('Institutions.csv', index=False)
    teams_df.to_csv('Teams.csv', index=False)


if __name__ == "__main__":
    print("Welcome to the Math Modeling Contest spreadsheet preparer. To prepare a spreadsheet for a SQL database, "
          "enter the name of a valid .csv file.")
    df = get_input_dataframe()
    prepare_data(df)
    print("Institution & Team spreadsheets created")
