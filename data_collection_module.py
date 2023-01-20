import json

import pandas as pd
import requests

from settings_RSS import Settings
from datetime import datetime as dt

settings = Settings()

# todo create classes for each API

def get_last_call_date():
    """
    Retrieve the last call date from the call history file.
    :return: Date of last recorded api call.
    """
    with open(settings.call_history) as f:
        decoded = json.load(f)
    return decoded['Last Call Date']


def set_request_parameters(parameters, field, condition, expression=''):
    """
    Define a set of parameters to apply to an API request.
    :param parameters: Parameters included in API request.
    :param field: Data field that condition is applied to.
    :param condition: The condition that is applied to the data field.
    :param expression: The expression that measures the condition.
    :return: Set of parameters to be included in the API request.
    """
    parameters[field] = condition if expression == '' else {expression: condition}
    return parameters


def set_parameters_by_record_type(record_type, field, last_call_date, expression, activity_type):
    """
    Formats request parameters based on record type.
    :param record_type: Accounts or Activities
    :param field: Data field to build API call parameters around.
    :param last_call_date: Date of most recent API call date.
    :param expression: Expression that measures condition applied to data field.
    :param activity_type: Activity type requested if the record_type is activity.
    :return:
    """
    parameters = {}
    if record_type == settings.accounts_url:
        parameters = set_request_parameters(parameters, field, last_call_date, expression)
    else:
        parameters = set_request_parameters(parameters, field, last_call_date, expression)
        parameters = set_request_parameters(parameters, "type", activity_type)
    parameters = json.dumps(parameters)
    return parameters


def check_created_records(last_call_date, record_type, activity_type=''):
    """
    Check how many accounts have been modified since last update.
    :param last_call_date: Date of most recent API call date.
    :param record_type: Accounts or Activities
    :param activity_type: Type of activity requested if record type is activity.
    :return: The number of records that have been created since the last API call date.
    """
    parameters = set_parameters_by_record_type(record_type, "createddate", last_call_date, "$gte", activity_type)
    url = record_type + f"?q={parameters}"
    r = requests.get(url, headers=settings.fred_authorization).json()
    records_created = r['metadata']['total_count']
    print(f"-{records_created} Records Have Been Created.")
    return records_created


def pagination_loop(record_type, parameter=''):
    """
    Loops through url pages of records until there are none left.
    :param record_type: Accounts or Activities
    :param parameter: Parameters applied API request if any. Default=''
    :return: Dataframe comprised of requested data.
    """
    try:
        page = 1
        frames = []
        print("\nLooping Through API URL Pages")
        while True:
            if parameter == '':
                url = record_type + f"?limit=100&page={page}"
            else:
                url = record_type + f"?q={parameter}&limit=100&page" \
                                    f"={page}"
            r = requests.get(
                url, headers=settings.fred_authorization).json()
            record_list = [i['record'] for i in r['list']]
            df = pd.DataFrame(record_list)
            frames.append(df)
            page += 1
            print(f"{page}", end=" ")
            if not r['metadata']['has_more']:
                break
        df = pd.concat(frames)
        print(f"\nDataframe contains {len(df)} records.\n")
        return df
    except KeyError:
        print(f"A Key Error Occurred While Looping Through {parameter} records.")
        print("Check API Usage")


def update_created_records(record_type, last_call_date, activity_type=''):
    """
    Update the records for all accounts that had been modified since the last call date.
    :param record_type: Accounts or  Activities
    :param last_call_date: Date of last recorded API call.
    :param activity_type: The type of activity requested if record_type is activities. Default=''
    :return:
    """
    if record_type == settings.accounts_url:
        csv_file = settings.accounts_csv
    else:
        csv_file = settings.activities_csv
    parameters = set_parameters_by_record_type(
        record_type, "createddate", last_call_date, "$gte", activity_type)
    created_accounts_df = pagination_loop(
        record_type, parameter=parameters)
    previous_accounts_df = pd.read_csv(csv_file)
    df_list = [previous_accounts_df, created_accounts_df]
    updated_df = pd.concat(df_list)
    updated_df.to_csv(csv_file, index=False)


def check_modified_records(last_call_date, record_type, activity_type=''):
    """
    Check how many accounts have been modified since last update.
    :param last_call_date: Date of last recorded API call.
    :param record_type: Accounts or Activities
    :param activity_type: Type of activity requested if record type is Activity. Default=''
    :return: The number of records modified since the last API call.
    """
    parameters = set_parameters_by_record_type(
        record_type, "modifieddate", last_call_date, "$gte", activity_type)
    url = record_type + f"?q={parameters}"
    r = requests.get(url, headers=settings.fred_authorization).json()
    records_modified = r['metadata']['total_count']
    print(f"-{records_modified} Records Have Been Modified.")
    return records_modified


def drop_outdated_rows(df, column, condition_list):
    """
    Drop row based on specific column and value.
    :param df: Dataframe containing existing reporting_df and df containing recently modified accounts/activities.
    :param column: Account ID column.
    :param condition_list: List of Account ID's that have been modified and merged into reporting_df
    :return: Dataframe where modified accounts/activities have replaced existing records.
    """
    index_names = df[df[column].isin(condition_list)].index
    return df.drop(index_names)


def update_modified_records(record_type, last_call_date, activity_type=''):
    """
    Update the records for all accounts that had been modified since the last call date.
    :param record_type: Accounts or Activities
    :param last_call_date: Date of last recorded API call.
    :param activity_type: Type of activity requested if record type is Activities. Default=''
    :return:
    """
    if record_type == settings.accounts_url:
        csv_file = settings.accounts_csv
    else:
        csv_file = settings.activities_csv
    parameters = set_parameters_by_record_type(record_type, "modifieddate", last_call_date, "$gte", activity_type)
    modified_accounts_df = pagination_loop(record_type, parameter=parameters)
    previous_accounts_df = pd.read_csv(csv_file)
    modified_id_list = list(modified_accounts_df['id'])
    unmodified_accounts_df = drop_outdated_rows(
        previous_accounts_df, 'id', modified_id_list)
    df_list = [unmodified_accounts_df, modified_accounts_df]
    updated_df = pd.concat(df_list)
    updated_df.to_csv(csv_file, index=False)


def update_accounts_df(last_call_date):
    """
    Updates all account data from RSS.
    :param last_call_date: Date of last recorded API call.
    :return:
    """
    created_records = check_created_records(last_call_date,
                                            settings.accounts_url)
    if int(created_records) > 0:
        update_created_records(settings.accounts_url, last_call_date)
    modified_records = check_modified_records(
        last_call_date, settings.accounts_url)
    print(modified_records)
    if int(modified_records) > 0:
        update_modified_records(settings.accounts_url, last_call_date)


def update_activities_df(last_call_date):
    """
    Update all records for all activities.
    :param last_call_date: Date of last recorded API call
    :return:
    """
    for i in settings.activity_types:
        print(f"\nChecking {i} Records:")
        created_records = check_created_records(
            last_call_date, settings.activities_url, i)
        if int(created_records) > 0:
            update_created_records(settings.activities_url, last_call_date, activity_type=i)
        modified_records = check_modified_records(
            last_call_date, settings.activities_url, i)
        if int(modified_records) > 0:
            update_modified_records(
                settings.activities_url, last_call_date, activity_type=i)


def update_last_call_date():
    """
    Update the last call date in api_call_history.json
    :return:
    """
    with open(settings.call_history) as f:
        decoded = json.load(f)
    decoded['Last Call Date'] = str(dt.now())
    with open(settings.call_history, 'w') as f:
        json.dump(decoded, f)
    print(f"Last Call Date Updated: {decoded['Last Call Date']}")


def collect_data():
    """
    Updates all accounts and activities since the last call date before updating the last call date.
    :return:
    """
    last_call_date = get_last_call_date()
    while True:
        try:
            update_accounts_df(last_call_date)
            update_activities_df(last_call_date)
            break
        except PermissionError:
            run = input("Unable to access file, please close any open files related to reported and enter: 'run' ")
            if input == 'run':
                continue
    update_last_call_date()
