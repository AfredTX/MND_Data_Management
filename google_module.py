import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from settings_RSS import Settings

settings = Settings()


def get_data_google_sheets(sample_spreadsheet_id, tab_index):
    """
    A function for reading and authenticating Google Sheets.
    :param sample_spreadsheet_id: ID string from the spreadsheet's url.
    :param tab_index: Index to begin pulling data from.
    :return: Dataframe made from data in spreadsheet.
    """
    # Link to authenticate
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

    # Read the .json file and authenticate with the links.
    credentials = Credentials.from_service_account_file(settings.google_creds,scopes=scopes)

    # Request the authorization and open the selected spreadsheet.
    gc = gspread.authorize(credentials).open_by_key(sample_spreadsheet_id)

    # Prompts for all spreadsheet values.
    values = gc.get_worksheet(tab_index).get_all_values()

    # Turns the return into a dataframe.
    df = pd.DataFrame(values)
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)

    return df

def write_to_google_sheet(sample_spreadsheet_id, df,job_type):
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

    # Read the .json file and authenticate with the links.
    credentials = Credentials.from_service_account_file(<CREDENTIALS>,
                                                        scopes=scopes)

    # Request the authorization and open the selected spreadsheet.
    gc = gspread.authorize(credentials).open_by_key(sample_spreadsheet_id)


    sheet = gc.worksheet(f"{job_type}")
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
