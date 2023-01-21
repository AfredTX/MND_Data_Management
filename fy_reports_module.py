import pandas as pd
from datetime import date
import data_manipulation_module as dmm
import xlsxwriter
import client_directories_module as cdm
import numpy as np
from settings_RSS import Settings

settings = Settings()


def get_ytd_dataframes(year):
    """
    Produce dataframes that only contain accounts and activities recorded during a specified fiscal year.
    :param year: The fiscal year on report.
    :return: activities_df and accounts_df for the specific fiscal year.
    """

    # noinspection PyTypeChecker
    beginning = pd.Timestamp(date(year - 1, 7, 1))
    ending = pd.Timestamp(date(year, 7, 1))

    activities_df = pd.read_csv(settings.activities_csv)

    activities_df = activities_df[pd.to_datetime(activities_df['createddate']) >= beginning].copy()

    accounts_df = pd.read_csv(settings.accounts_csv)

    reporting_df = pd.read_csv(settings.reporting_df_csv)

    reporting_df['id'] = reporting_df['Account Id']

    accounts_df = pd.merge(accounts_df, reporting_df[['id', 'Original Intake Date','Original Training Program',
                                                      'Enrollment Satisfied', 'Cohort Date']], how='left', on='id')

    accounts_df['enrollment_date'] = np.where(
        ((accounts_df['Enrollment Satisfied'] == 'Yes') &
         accounts_df['Original Training Program'].str.contains('CTC|MTDL|CF')), accounts_df['Cohort Date'],
        accounts_df['Original Intake Date'])

    accounts_df = accounts_df[
        (pd.to_datetime(accounts_df['enrollment_date'], errors='coerce') >= beginning) &
        (pd.to_datetime(accounts_df['enrollment_date'], errors='coerce') < ending)].copy()

    del accounts_df['Original Intake Date']
    del accounts_df['Original Training Program']
    del accounts_df['Enrollment Satisfied']
    del accounts_df['Cohort Date']
    del accounts_df['enrollment_date']

    return activities_df, accounts_df


def build_ytd_report(year):
    """
    Build a reporting_df for the specific fiscal year.
    :param year: Fiscal year
    :return:
    """
    activities_df, accounts_df = get_ytd_dataframes(year)
    reporting_df = dmm.initiate_reporting_df(accounts_df)
    #reporting_df = dmm.apply_returning_client_data(reporting_df, activities_df)
    reporting_df = dmm.assign_job_coach_initials(reporting_df)
    reporting_df = dmm.apply_employment_data(reporting_df, activities_df)
    reporting_df = dmm.apply_retention_data(reporting_df, activities_df)
    reporting_df = dmm.apply_cohort_data(reporting_df, activities_df)
    reporting_df = dmm.apply_certification_data(reporting_df, activities_df)
    reporting_df = dmm.apply_training_status_data(reporting_df, activities_df)
    reporting_df = dmm.apply_inactive_data(reporting_df, activities_df)
    reporting_df = dmm.apply_snap_fee_data(reporting_df, activities_df)
    reporting_df = dmm.apply_grant_id_df("SNAP ID", reporting_df, activities_df)
    reporting_df = dmm.apply_grant_id_df("EARN ID", reporting_df, activities_df)
    reporting_df = dmm.apply_dol_wage_records(reporting_df)
    reporting_df = dmm.format_demographics(reporting_df)
    reporting_df = dmm.assign_fiscal_quarter(reporting_df)
    reporting_df = dmm.assign_fiscal_year(reporting_df)
    reporting_df = dmm.assign_intake_quarter(reporting_df)
    reporting_df = dmm.assign_intake_fy(reporting_df)
    reporting_df = dmm.format_reporting_df(reporting_df)
    reporting_df = dmm.format_grant_fund(reporting_df)
    reporting_df = dmm.coerce_to_datetime(reporting_df,'Original Intake Date','Cohort Date')
    current_fy_reports = [f"\FY {year} Report.xlsx", f"\FY {year} Performance Report.xlsx"]
    if (year == pd.Timestamp('now').year) | (year == pd.Timestamp('now').year +1):
        for report_name in current_fy_reports:
            filename = settings.ytd_reports + report_name
            try:
                cdm.write_excel(filename, 'Data', reporting_df)
                cdm.write_excel(filename, 'KPIs', reporting_df[settings.kpi_columns])
                cdm.write_excel(filename, 'Employments',
                                reporting_df[reporting_df['Gained Employment'] == 'Yes'][settings.kpi_employments])
                cdm.write_excel(filename, 'Certifications',
                                reporting_df[reporting_df['Gained Certification'] == 'Yes'][settings.kpi_certifications])
            except FileNotFoundError:
                print("File Doesn't Exist Yet, Let Me Make It!")
                workbook = xlsxwriter.Workbook(filename)
                workbook.add_worksheet('Data')
                workbook.add_worksheet('KPIs')
                workbook.add_worksheet('Employments')
                workbook.add_worksheet('Certifications')
                workbook.close()
                cdm.write_excel(filename, 'Data', reporting_df)
                cdm.write_excel(filename, 'KPIs', reporting_df[settings.kpi_columns])
                cdm.write_excel(filename, 'Employments', reporting_df[reporting_df['Gained Employment'] == 'Yes'][settings.kpi_employments])
                cdm.write_excel(filename, 'Certifications', reporting_df[reporting_df['Gained Certification'] == 'Yes'][settings.kpi_certifications]) #todo this could be a while loop


# noinspection PyTypeChecker
def calculate_fiscal_year():
    """
    Calculate the fiscal year based on today's date.
    :return: fiscal year
    """
    year = pd.Timestamp('now').year
    month = pd.Timestamp('now').month

    if month >= 7:
        year += 1
    return year


def update_fy_reports():
    """
    Updates fiscal year reports dating back to FY2020
    :return:
    """
    fiscal_year = calculate_fiscal_year()
    years = [i for i in range(2020, (fiscal_year + 1))]

    for year in years:
        build_ytd_report(year)
