import pandas as pd
import google_module as gm
from settings_RSS import Settings
import requests
import json

settings = Settings()

def verify_new_event(id_list, activity_type, identifier=""):
    reporting_df = pd.read_csv(settings.reporting_df_csv)
    if identifier != "":
        df = reporting_df[reporting_df[f'{activity_type}'] == f'{identifier}']
    else:
        df = reporting_df[reporting_df[f'{activity_type}'].notnull()]
    existing_id_list = list(df['Account Id'])

    return [x for x in id_list if x not in existing_id_list]

def get_new_completer_list(attendance_df):
    completers_df = attendance_df[attendance_df['Passed Training'] == 'Passed']
    completer_id_list = list(completers_df['Account ID'].astype(int))

    new_completer_list = verify_new_event(completer_id_list, "Training Status", "Complete")

    return completers_df, new_completer_list

def format_training_status_activity_dict(completers_df, new_completer_list):
    new_completer_df = completers_df[completers_df['Account ID'].astype(int).isin(new_completer_list)]
    new_completer_df.loc[:,'Training Status'] = "Complete"
    new_completer_df.loc[:,'type'] = "Training Status"
    new_completer_df = new_completer_df.rename(
        columns= {'Account ID': 'accountid', 'Program': 'trainingprogram','Cohort Date': 'startdate',
                  'Training Status': 'trainingstatus'})
    return new_completer_df[['accountid', 'type', 'trainingprogram', 'startdate', 'trainingstatus']].to_dict('index')

def post_dictionary_activities(dict):
    failed_posts = 0
    for total_requests, (k, v) in enumerate(dict.items(), start=1):
        v['date'] = str(pd.Timestamp.today())
        json_string = json.dumps(v)
        url = f"{settings.activities_url}"
        r = requests.post(url,data=json_string,headers=settings.posting_headers)
        print(r.status_code)
        if r.status_code != 201:
            print(f"Activity type: {v['type']} for client ID: {v['accountid']} failed to post")
            print(r.status_code)
            failed_posts += 1
        if total_requests > 0:
            successful_posts = total_requests - failed_posts
    print(f"{successful_posts}/{total_requests} {v['type']} Activities were successfully posted to RSS.")


def update_new_completers(df):
    while True:
        completers_df, new_completer_list = get_new_completer_list(df)
        if len(new_completer_list) == 0:
            print("No new completers to report!")
            break
        print(f"{len(new_completer_list)} new completers to report!")
        dict = format_training_status_activity_dict(completers_df, new_completer_list)
        post_dictionary_activities(dict)
        break

def format_cohort_activity_dict(enrollment_satisfied_df, new_enrollment_list):
    enrollment_satisfied_df = enrollment_satisfied_df[enrollment_satisfied_df['Account ID'] != '']
    new_enrollee_df = enrollment_satisfied_df[enrollment_satisfied_df['Account ID'].astype(int).isin(new_enrollment_list)]
    new_enrollee_df.loc[:, 'type'] = "Cohort"
    new_enrollee_df = new_enrollee_df.rename(
        columns={'Account ID': 'accountid', 'Program': 'trainingprogram',
                 'Cohort Date': 'startdate'})
    return new_enrollee_df[['accountid', 'type', 'trainingprogram', 'startdate']].to_dict('index')

def update_new_enrollees(df):

    while True:
        df['Classes Attended'] = df['Classes Attended'].fillna(0).replace("",0).astype(int)
        enrollment_satisfied_df = df[df['Classes Attended'] >= 3]
        enrollment_satisfied_id_list = list(
            enrollment_satisfied_df[enrollment_satisfied_df['Account ID'] != '']['Account ID'].astype(int))

        new_enrollment_list = verify_new_event(enrollment_satisfied_id_list,"Enrollment Satisfied", identifier="Yes")

        if len(new_enrollment_list) == 0:
            print("No new enrollees to report!")
            break
        else:
            try:

                print(f"{len(new_enrollment_list)} new enrollees to report!")
                print(f"Account ID's: {new_enrollment_list}")
                dict = format_cohort_activity_dict(enrollment_satisfied_df, new_enrollment_list)
                post_dictionary_activities(dict)
                break
            except ValueError:
                print("Faulty Data Formatting in Attendance Sheet. Cannot perform analysis.")
                break





def automated_activity_updates():
    attendance_df = gm.get_data_google_sheets(settings.fy23_training_attendance, 0) # todo automatically identify FY attendance sheet, by year or other solution
    update_new_completers(attendance_df)
    update_new_enrollees(attendance_df)

