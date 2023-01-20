import datetime
import json
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
import pandas as pd

from data_collection_module import pagination_loop
from google_module import get_data_google_sheets
from settings_RSS import Settings

settings = Settings()


# todo create a class for an email
# todo create a class for each report

def get_day_of_week():
    """
    Returns the current day of the week.
    :return: weekday
    """
    return datetime.datetime.today().weekday()


def format_accounts_df(reporting_df, period):
    """
    Format the dataframe made up of newly created accounts.
    :param period: daily or weekly period
    :param reporting_df: backed up reporting_df
    :return: merged dataframe of reporting_df and accounts.csv
    """
    df = pd.read_csv(settings.accounts_csv)
    df = df[
        pd.to_datetime(df['createddate']) >= period]
    df = pd.merge(
        df, reporting_df[['id', 'Case Manager']], how='left',
        on='id')
    return df


def format_activities_df(reporting_df, period):
    """
    Format the dataframe that hold all daily activities.
    :param period: daily or weekly period
    :param reporting_df: backed up reporting_df
    :return: merged dataframe of reporting_df and activities.csv
    """
    df = pd.read_csv(settings.activities_csv)
    df = pd.merge(
        df, reporting_df[['accountid', 'Case Manager']], how='left',
        on='accountid')
    df['Case Manager'] = np.where(
        ((df['type'] == 'Training Status') |
         (df['type'] == 'Cohort')), 'FR', df['Case Manager'])
    df = df[
        pd.to_datetime(df['createddate']) >= period]
    return df


def format_inquiry_df(period):
    """
    Format inquiry df from google sheets.
    :param period: daily or weekly period
    :return: dataframe pulled from google sheets
    """
    df = get_data_google_sheets(
        '10RFz4iH8d9zwrNfnH1cAw_2RLWeKF0z4xJOi5sZJg0M', 0)
    df = df[pd.to_datetime(
        df.iloc[:, 0]) >= period]
    df = df.replace(to_replace='', value='(blank)')
    return df


def format_info_session_df(period):
    """
    Format df from info_session tracker.
    :param period: daily or weekly period
    :return: dataframe pulled from google sheets
    """
    df = get_data_google_sheets(
        '1yp09eMrb3wfB6HslJ0yPriuKwosNjvbZlvyQB-tAHkw', 0)
    df = df[
        pd.to_datetime(
            df['Date'], errors='coerce') >= period]
    df = df.replace(to_replace='', value='(blank)')
    return df


def write_accounts_created_body(df, body):
    """
    Write the message body that informs team of the accounts that were created that day.
    :param df: dataframe of accounts created today.
    :param body: body of text in the email
    :return: altered body of text
    """
    accounts_created = len(df)
    clients_processed = list(df['name'])
    programs = list(df['originaltrainingprogram'])
    coaches_assigned = list(df['Case Manager'])
    client_sources = list(df['source'])

    if accounts_created > 0:
        indicative = 'were'
        subject = 'clients'
        if accounts_created == 1:
            indicative = 'was'
            subject = 'client'
        accounts_created_body = (
            f"\n\nThere {indicative} {accounts_created} {subject} "
            "processed in RSS: ")
        body += accounts_created_body
        for i in range(len(clients_processed)):
            client_body = (f"\n- {clients_processed[i]} "
                           f"\n     - Coach: {coaches_assigned[i]} "
                           f"\n     - Program: {programs[i]} "
                           f"\n     - Source: {client_sources[i]}")
            body += client_body
    else:
        body += '\nThere were no new clients processed in RSS.\n'
    return body


def write_daily_reporting_activities_body(df, body):
    """
    Write the message body that informs team of the accounts that were created today.
    :param df: dataframe of daily activities recorded
    :param body: existing body of email text
    :return: altered body of email text
    """
    activities_recorded = len(df)
    if activities_recorded > 0:
        indicative = 'were'
        subject = 'activities'
        if activities_recorded == 1:
            indicative = 'was'
            subject = 'activity'
        activities_body = f"\n\nThere {indicative} {activities_recorded} {subject} related to our reporting outcomes " \
                          f"recorded in RSS:"
        for i in settings.activity_types:
            times_recorded = len(df[df['type'] == f"{i}"])
            coach_counts = df[
                df['type'] == f"{i}"]['Case Manager'].value_counts()
            if times_recorded > 0:
                activity_string = (f"\n- {i}: {times_recorded}"
                                   f"\n{coach_counts.to_string(index=True)}")
                activities_body += activity_string
    else:
        activities_body = (
            '\n\nNo activities related to reporting outcomes were recorded. \n'
        )

    body += activities_body
    return body


def write_inquiry_body(df, body):
    """
    Write the message body that informs team members about inquiries.
    :param df: dataframe of daily inquiries
    :param body: existing body of email text
    :return: altered body of email text
    """

    total_inquiries = len(df)
    source_count = df['How did you hear about MND?'].value_counts()
    if_other = len(df[(df['If other, let us know where you heard about us.'] != '') &
                      (df['If other, let us know where you heard about us.'] != 'None')])
    if_other_count = df['If other, let us know where you heard about us.'].value_counts()

    if total_inquiries > 0:
        inquiries_body = received_inquiries_body(
            total_inquiries, source_count, if_other, if_other_count
        )

    else:
        inquiries_body = "\nNo inquiries were recorded in Google " \
                         "Drive.\n"
    body += inquiries_body
    return body


def received_inquiries_body(total_inquiries, source_count, if_other, if_other_count):
    indicative = 'were'
    subject = 'inquiries'
    if total_inquiries == 1:
        indicative = 'was'
        subject = 'inquiry'
    result = (
        f"\n\nThere {indicative} {total_inquiries} {subject} recorded in Google Drive. Here's how "
        f"they heard about us:"
    )

    source_string = f"\n{source_count.to_string(index=True)}"
    result += source_string

    if if_other > 0:
        if_other_body = (f"\nFor those that marked 'Other':"
                         f"\n{if_other_count.to_string(index=True)}")
        result += if_other_body
    return result


def write_info_session_report_body(df, body):
    """
    Write message that alerts team about how info_session went.
    :param df: Dataframe containing daily/weekly info session attendance data.
    :param body: Existing body of email text.
    :return: Altered body of email text.
    """

    total_attendees = len(df)
    info_session_coach_count = df[
        'Coach Breakout Room'].value_counts()
    info_session_outcome_count = df['Outcome'].value_counts()
    info_session_program_count = df['Program'].value_counts()

    if total_attendees > 0:
        indicative = 'were'
        subject = 'attendees'
        if total_attendees == 1:
            indicative = 'was'
            subject = 'attendee'
        info_session_body = (f"\n\nThere {indicative} {total_attendees} {subject} at the Info Session. Here is a"
                             f"breakdown of their programs of interest, outcomes, and which coaches engaged with"
                             f"them."
                             f"\n\nProgram of Interest: "
                             f"\n{info_session_program_count.to_string(index=True)}"
                             f"\n\nOutcomes: "
                             f"\n{info_session_outcome_count.to_string(index=True)}"
                             f"\n\nCoaches: "
                             f"\n{info_session_coach_count.to_string(index=True)}")
    else:
        info_session_body = "\n\nThere were no new entries in the Info Session Tracker."
    body += info_session_body
    return body


def write_daily_activities_body(body, reporting_df, period):
    """
    Write body that informs team members of all activities recorded.
    :param period: daily or weekly period
    :param body: Existing body of email text.
    :param reporting_df: reporting_df.csv
    :return: Altered body of email text containing daily grant related activities.
    """
    parameters = json.dumps({'createddate': {'$gte': f'{period}'}})
    df = pagination_loop(settings.activities_url, parameter=parameters)
    if len(df) > 0:
        df = pd.merge(
            df, reporting_df[['accountid', 'Case Manager']])
        df['Case Manager'] = np.where(
            ((df['type'] == 'SNAP FEE Confirmed') |
             (df['type'] == 'SNAP ID') |
             (df['type'] == 'EARN ID') |
             (df['type'] == 'Training Status') |
             (df['type'] == 'Cohort')), 'FR', df['Case Manager'])
        total_activities = len(df)
        indicative = 'were'
        subject = 'activities'
        if total_activities == 1:
            indicative = 'was'
            subject = 'activity'
        activity_body = (f"\n\nThere {indicative} {total_activities} general"
                         f" {subject} recorded in RSS. "
                         "\nHere's how many activities were recorded "
                         "by each active coach:\n"
                         f"{df['Case Manager'].value_counts().to_string(index=True)}"
                         "\nHere's the types of activities that were"
                         " recorded:\n"
                         f"{df['type'].value_counts().to_string(index=True)}\n")
        body += activity_body

        support_services_df = df[(df['supportservices'] != '') &
                                 (df['supportservices'].notnull())]
        total_support_services = len(support_services_df)
        if total_support_services > 0:
            indicative = 'were'
            subject = 'support services'
            if total_support_services == 1:
                indicative = 'was'
                subject = 'support service'
            support_services_body = (
                f"\n\nThere {indicative} {total_support_services} {subject} "
                f"recorded in RSS. "
                "\nHere's how many were recorded by"
                " each active coach:\n"
                f"{support_services_df['Case Manager'].value_counts().to_string(index=True)}"
                "\nHere's the types of support services that were"
                " recorded:\n"
                f"{support_services_df['supportservices'].value_counts().to_string(index=True)}")
        else:
            support_services_body = "\nThere were no support " \
                                    "services recorded in RSS."
        body += support_services_body
    else:
        activity_body = "\nThere were no activities or support " \
                        "services recorded in RSS.\n"
        body += activity_body
    return body


def construct_whole_message_body(reporting_df, period):
    """
    Construct the message that will be emailed to team.
    :param period: daily or weekly period
    :param reporting_df: reporting_df.csv
    :return: Complete body of email text.
    """
    phrase = "this week!" if period == settings.current_week else "today!"
    body = (f"Hello,\n\nThis is an automated message. Here is a "
            f" breakdown of all the data entered into RSS and Google Drive {phrase}\n")

    info_session_df = format_info_session_df(period)
    body = write_info_session_report_body(info_session_df, body)

    daily_accounts_df = format_accounts_df(reporting_df, period)
    body = write_accounts_created_body(daily_accounts_df, body)

    daily_reporting_activities_df = format_activities_df(
        reporting_df, period)
    body = write_daily_reporting_activities_body(
        daily_reporting_activities_df, body)

    body = write_daily_activities_body(body, reporting_df, period)

    inquiry_df = format_inquiry_df(period)
    body = write_inquiry_body(inquiry_df, body)

    sign_out_body = ("\n\nThis has been your daily data report."
                     "\nFred's Data Bot, "
                     "\nSigning Out")
    body += sign_out_body
    return body


def get_daily_report_subscriber_list(period):
    """
    Produces a list of subscriber emails to distribute daily report.
    :return: List of daily/weekly subscriber email addresses.
    """
    report_type = 'Weekly Report' if period == settings.current_week else 'Daily Report'
    df = get_data_google_sheets(
        '1ZgPSQdiXBglvqylHgY40eBdO6aP8BWmVRwU3JOWB9U4', 0)
    subscriber_list = list(df[report_type])
    subscriber_list = list(filter(None, subscriber_list))
    return subscriber_list


def execute_daily_operations_report(reporting_df, password, period):
    """
    Runs and sends report detailing daily operations and data recorded.
    :param period: daily or weekly period
    :param reporting_df: reporting_df.csv
    :param password: Email password.
    :return:
    """
    body = construct_whole_message_body(reporting_df, period)
    subject = "Daily Operations Report"
    subscriber_list = get_daily_report_subscriber_list(period)
    for i in subscriber_list:
        send_email(subject, i, body, password)
        print(f"Daily Report Sent To {i}\n")


def send_email(subject, receiver_email, body, password):
    """
    Sends email from frandall@mdnewdirections.org
    :param subject: Email subject title
    :param receiver_email: Recipient email address
    :param body: Body of text included in email.
    :param password: Password to sender email account.
    :return:
    """
    sender_email = settings.user_email

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


def send_attachment_email(subject, body, receiver_email, filename, password):
    """
    Send an email with an attachment from settings.user_email
    :param subject: Subject of email.
    :param body: Body of text included in email.
    :param receiver_email: Recipient email address.
    :param filename: Path of file to be attached
    :param password: Sender email password.
    :return:
    """
    sender_email = settings.user_email

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Open PDF file in binary mode
    open_file = False
    while not open_file:
        try:
            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this
                # automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            open_file = True
        except PermissionError:
            close = input("Close Excel File and enter 'run' to "
                          "continue: ")
            if close == 'run':
                open_file = False

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


def organize_reports():
    """
    Organize all of the reports that will be created and
    distributed.
    :return:
    """
    weekday = get_day_of_week()
    period = settings.current_week if weekday == 4 else settings.today
    reporting_df = pd.read_csv(settings.reporting_df_csv)
    reporting_df['id'] = reporting_df['Account Id']
    reporting_df['accountid'] = reporting_df['Account Id']
    password = settings.passcode
    execute_daily_operations_report(reporting_df, password, period)
