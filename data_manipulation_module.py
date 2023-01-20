import numpy as np
import pandas as pd

from settings_RSS import Settings

settings = Settings()
pd.set_option('mode.chained_assignment', None)


def get_accounts_activities_dataframes(accounts_path, activities_path):
    """
    Produces dataframes from the accounts and activities csv files.
    :param accounts_path: Path to accounts.csv
    :param activities_path: Path to activities.csv
    :return: accounts and activities dataframes
    """
    accounts_df = pd.read_csv(accounts_path)
    activities_df = pd.read_csv(activities_path)
    return accounts_df, activities_df


def initiate_reporting_df(accounts_df):
    """
    Create the reporting dataframe using accounts.csv as the source.
    :param accounts_df: Dataframe pulled from accounts.csv
    :return: Dataframe where accountid field is formatted to match activities dataframe.
    """
    return accounts_df.rename(columns={'id': 'accountid'})


def incorporate_returning_client_df(df, activities_df):
    """
    Prepare returning client.csv data to be merged into reporting_df.
    :param df: reporting_df created from accounts.csv
    :param activities_df: dataframe created from activities.csv
    :return: reporting_df with returning client activities merged.
    """
    returning_client_df = activities_df[activities_df['type'] == 'Returning Client'].rename(
        columns={'date': 'returning_date', 'trainingprogram': 'returning_training_program'})
    returning_client_df = returning_client_df[returning_client_df['returning_date'] == returning_client_df.groupby(
        'accountid').returning_date.transform('max')]
    if returning_client_df.empty:
        print("No Returning Client Data to Manipulate")
    else:
        returning_client_df['returning_client'] = "Yes"
        cols = ['accountid', 'returning_date', 'returning_training_program', 'returning_client']
        returning_client_df = returning_client_df.reindex(cols, axis='columns')
        df = pd.merge(df, returning_client_df, how='left',
                      on='accountid')
        df = df.drop_duplicates(subset=['accountid'])
    return df


def coerce_to_datetime(df, *column_names):
    """
    Coerce date related columns to datetime format.
    :param df: Dataframe containing columns that need to be converted to datetime.
    :param column_names: Columns that need to be converted to datetime.
    :return: Dataframe with appropriate datetime formatted columns.
    """
    for i in column_names:
        df[i] = pd.to_datetime(df[i].dropna(), errors='coerce').copy()
    return df


def identify_current_intake_program(df):
    """
    Create columns that identify the clients' most recent training program and intake date.
    :param df: reporting_df
    :return: Dataframe featuring columns that identify most recent client intake dates.
    """
    try:
        df['originalintakedate'] = np.where(df['returning_client'] != "Yes", df['originalintakedate'],
                                             df['returning_date'])
        df['originaltrainingprogram'] = np.where(df['returning_client'] != "Yes", df['originaltrainingprogram'],
                                         df['returning_training_program'])
    except:
        print("No Returning Client Data To Manipulate")
    return df


def assign_job_coach_initials(df):
    """
    Create a column that identifies the case manager by their ID.
    :param df: reporting_df
    :return: Dataframe featuring column that identifies job coach initials.
    """

    owner_ids = [df['ownerid'] == 36971, df['ownerid'] == 31833, df['ownerid'] == 20431, df['ownerid'] == 36966,
                 df['ownerid'] == 36970, df['ownerid'] == 36972, df['ownerid'] == 36949, df['ownerid'] == 19501,
                 df['ownerid'] == 20433, df['ownerid'] == 20435, df['ownerid'] == 23869, df['ownerid'] == 31835,
                 df['ownerid'] == 36943, df['ownerid'] == 36947, df['ownerid'] == 36953, df['ownerid'] == 36955,
                 df['ownerid'] == 36959, df['ownerid'] == 36961, df['ownerid'] == 36963, df['ownerid'] == 36973,
                 df['ownerid'] == 36974, df['ownerid'] == 36975, df['ownerid'] == 36976, df['ownerid'] == 36978]

    coach_initials = ['CH', 'RV', 'SH', 'KD', 'RG', 'ML', 'VOID', 'MND', 'ST', 'MR', 'KH', 'MD', 'JE', 'JB', 'AH',
                      'SBT', 'JC', 'DH', 'MG', 'RSS Support', 'RB', 'MM', 'MS', 'VF'] #todo create job coach id dictionary

    df['case_manager'] = np.select(owner_ids, coach_initials, default=np.nan)
    return df


def assign_fiscal_quarter(df):
    """
    Create a column that identifies the fiscal year quarter of each client.
    :param df: reporting_df
    :return: Dataframe tht includes the fiscal quarter of each clients most recent intake.
    """
    coerce_to_datetime(df,'originalintakedate','cohort_date')
    df['month'] = np.where(
        ((df['enrollment_satisfied'] == 'Yes') & df['originaltrainingprogram'].str.contains('CTC|MTDL|CF')),
        pd.DatetimeIndex(df['cohort_date']).month,
        pd.DatetimeIndex(df['originalintakedate']).month)

    q_conditions = [
        (df['month'] <= 3.0),
        ((df['month'] > 3.0) & (df['month'] < 7.0)),
        ((df['month'] > 6.0) & (df['month'] < 10.0)),
        (df['month'] >= 10.0)
    ]

    q_values = ['Quarter 3', 'Quarter 4', 'Quarter 1', 'Quarter 2']

    df['quarter'] = np.select(q_conditions, q_values, default=np.nan)
    return df

def assign_intake_quarter(df):
    coerce_to_datetime(df, 'originalintakedate', 'cohort_date')
    df['intake_month'] = pd.DatetimeIndex(df['originalintakedate']).month

    q_conditions = [
        (df['intake_month'] <= 3.0),
        ((df['intake_month'] > 3.0) & (df['intake_month'] < 7.0)),
        ((df['intake_month'] > 6.0) & (df['intake_month'] < 10.0)),
        (df['intake_month'] >= 10.0)
    ]

    q_values = ['Quarter 3', 'Quarter 4', 'Quarter 1', 'Quarter 2']

    df['intake_quarter'] = np.select(q_conditions, q_values, default=np.nan)
    return df

def assign_intake_fy(df):
    df['intake_fy'] = pd.DatetimeIndex(df['originalintakedate']).year
    df['intake_fy'] = np.where((df['intake_month'] > 6.0), (df['intake_fy'] + 1.0), df['intake_fy'])
    df['intake_fy'] = df['intake_fy'].fillna(0.0).astype(int)

    return df


def assign_fiscal_year(df):
    """
    Create a column that identifies the client's fiscal year.
    :param df: reporting_df
    :return: Dataframe where the fiscal year of the client's intake date is calculated.
    """
    df['year'] = np.where(
        ((df['enrollment_satisfied'] == 'Yes') & df['originaltrainingprogram'].str.contains('CTC|MTDL|CF')),
        pd.DatetimeIndex(df['cohort_date']).year,
        pd.DatetimeIndex(df['originalintakedate']).year)
    df['fiscal_year'] = np.where((df['month'] > 6.0), (df['year'] + 1.0), df['year'])
    df['fiscal_year'] = df['fiscal_year'].fillna(0.0).astype(int)

    return df


def apply_returning_client_data(df, activities_df):
    """
    Manipulate and apply returning client data to the aggregated reporting df.
    :param df: reporting_df
    :param activities_df: Dataframe created from activities.csv
    :return: Dataframe that includes columns related to returning clients, fiscal year, and fiscal quarter.
    """
    df = incorporate_returning_client_df(df, activities_df)
    df = identify_current_intake_program(df)
    df = coerce_to_datetime(df, 'originalintakedate', 'returning_date', 'dob', 'originalintakedate')
    df = assign_job_coach_initials(df)
    df = assign_fiscal_quarter(df)
    df = assign_fiscal_year(df)

    return df


def parse_placement_retention(df):
    """
    Parse data from the placementretention column and create columns to represent each individual detail.
    :param df: Dataframe of employment records in activities.csv
    :return: Dataframe of employment details featuring a column for each item in settings.employment_details.
    """
    for i in settings.employment_details:
        df.loc[:, f'{i}'] = np.where(df['placementretention'].str.contains(f'{i}'), "Yes", "No")

    return df


def format_client_became_employed_df(activities_df):
    """
    Properly format employment data to be introduced to the reporting df.
    :param activities_df: Dataframe created from activities.csv
    :return: Dataframe made up of entirely employment records.
    """
    employment_df = activities_df[activities_df['type'] == 'Client Became Employed']
    employment_df.loc[:, 'placement_type'] = np.where(
        employment_df['placementretention'].str.contains('Initial Placement'), 'Initial Placement',
        'Secondary Placement')
    employment_df = parse_placement_retention(employment_df)
    return employment_df


def rename_columns(prefix, df):
    """
    Rename multiple columns in a dataframe.
    :param prefix: Prefix to be added to the beginning of column names.
    :param df: employment_df
    :return: Dataframe where all columns except accountid contain selected prefix.
    """
    new_names = [(i, prefix + i) for i in df.columns if i not in ['accountid']]
    df = df.rename(columns=dict(new_names), inplace=True)
    return df


def incorporate_tiered_placement_data(employment_df, reporting_df, grouping, prefix):
    """
    Format a dataframe of Initial Placement data and merge it into the aggregated reporting df
    :param employment_df: employment_df
    :param reporting_df: reporting_df
    :param grouping: min or max
    :param prefix: initial or current placement
    :return: Updated reporting_df that features initial and current employment details for each client.
    """
    df = coerce_to_datetime(employment_df, 'startdate')
    df = df[df['startdate'] == df.groupby('accountid').startdate.transform(grouping)]
    df = df[['accountid', 'startdate', 'placement_type', 'employer', 'position', 'wage', 'hours', 'Full Time',
             'Benefits', 'Temporary', 'MND Lead', 'Industry Related']]
    rename_columns(prefix, df)
    reporting_df = pd.merge(reporting_df, df, how='left', on='accountid')
    reporting_df = reporting_df.drop_duplicates(subset=['accountid'])
    return reporting_df


def incorporate_job_hopping_data(employment_df, reporting_df):
    """
    Format a dataframe of Job Hopping data and merge it into the aggregated reporting df.
    :param employment_df: employment_df
    :param reporting_df: reporting_df
    :return: Modified reporting_df featuring columns identifier job hoppers and their most recent job hop.
    """
    df = coerce_to_datetime(employment_df, 'startdate')
    df = df[df['Job Hopping'] == 'Yes']
    df = df[df['startdate'] == df.groupby('accountid').startdate.transform('max')].rename(
        columns={'startdate': 'last_job_hop'})
    df = df[['accountid', 'Job Hopping', 'last_job_hop']]
    reporting_df = pd.merge(reporting_df, df, how='left', on='accountid')
    reporting_df = reporting_df.drop_duplicates(subset=['accountid'])
    return reporting_df


def apply_employment_data(df, activities_df):
    """
    Manipulate and apply client became employed data to the aggregated reporting df.
    :param df: reporting_df
    :param activities_df: Dataframe created from accounts.csv
    :return: Modified reporting_df featuring columns for all relevant employment data
    """
    employment_df = format_client_became_employed_df(activities_df)
    df = incorporate_tiered_placement_data(employment_df, df, 'min', 'initial_')
    df = incorporate_tiered_placement_data(employment_df, df, 'max', 'current_')
    df = incorporate_job_hopping_data(employment_df, df)
    df = coerce_to_datetime(df, 'last_job_hop', 'current_startdate', 'initial_startdate')

    return df


def format_retention_df(activities_df):
    """
    Properly format retention data to be integrated to the reporting df.
    :param activities_df: Dataframe created from activities.csv
    :return: Dataframe made up exclusively of retention records.
    """
    df = activities_df[activities_df['type'] == 'Retention']
    df.loc[:, 'advancement'] = np.where(df['placementretention'].str.contains('Retention and Advancement'), 'Yes', 'No')
    df['retained'] = np.where(df['placementretention'].str.contains('Job Retained'), 'Yes', 'No')
    return df


def incorporate_advancements(retention_df, reporting_df):
    """
    Properly format and incorporate career advancements.
    :param retention_df: retention_df
    :param reporting_df: reporting_df
    :return: Modified reporting_df featuring column identifying clients that achieved career advancement.
    """
    advanced_df = retention_df[
        retention_df['advancement'] == 'Yes']
    reporting_df = pd.merge(reporting_df, advanced_df[['accountid', 'advancement']], how='left', on='accountid')
    reporting_df = reporting_df.drop_duplicates(subset=['accountid'])
    return reporting_df


def incorporate_last_retention_data(retention_df, reporting_df):
    """
    Create a dataframe made up of only the most recent retention updates per account.
    :param retention_df: retention_df
    :param reporting_df: reporting_df
    :return: Modified reporting_df featuring status and date of most recent retention update.
    """
    df = coerce_to_datetime(retention_df, 'date')
    df = df[df['date'] == df.groupby('accountid').date.transform('max')].rename(
        columns={'date': 'last_retention_update', 'placementretention': 'last_retention_status'})
    df = df[['accountid', 'last_retention_update', 'last_retention_status']]
    reporting_df = pd.merge(reporting_df, df, how='left', on='accountid')
    reporting_df = reporting_df.drop_duplicates(subset=['accountid'])
    return reporting_df


def incorporate_last_date_retained(retention_df, reporting_df):
    """
    Identify the last date a job was retained and include column in aggregated reporting df.
    :param retention_df: retention_df
    :param reporting_df: reporting_df
    :return: Modified reporting_df the features column identifying the last date where client retained job.
    """
    df = coerce_to_datetime(retention_df, 'date')
    df = df[(df['retained'] == 'Yes')]
    df = df[df['date'] == df.groupby('accountid').date.transform('max')].rename(columns={'date': 'last_date_retained'})
    df = df[['accountid', 'last_date_retained']]
    reporting_df = pd.merge(reporting_df, df, how='left', on='accountid')
    reporting_df = reporting_df.drop_duplicates(subset=['accountid'])
    return reporting_df


def identify_milestones(df):
    """
    Calculate each client's retention/employment milestones.
    :param df: reporting_df
    :return: Modified reporting_df featuring columns identifying retention and employment milestones.
    """
    coerce_to_datetime(df,'last_date_retained', 'last_job_hop', 'initial_startdate','originalintakedate',
                       'last_retention_update')
    retention_since_job_hop = (df['last_date_retained'] - df['last_job_hop'])
    retained_since_startdate = (df['last_date_retained'] - df['initial_startdate'])
    retained_since_intake = (df['last_date_retained'] - df['originalintakedate'])
    update_since_intake = (df['last_retention_update'] - df['originalintakedate'])
    update_since_startdate = (df['last_retention_update'] - df['initial_startdate'])
    time_since_startdate = settings.now - df['initial_startdate']

    df['incumbent_worker'] = np.where(((df['howlongjobless'] == 'Currently employed') |
                                       (df['howlongjobless'] == 'Still Working')), 'Yes', 'No')
    df['nonincumbent_retention_milestone'] = np.where((df['last_job_hop'].isnull()) |
                                                      (retention_since_job_hop <= settings.zero_days),
                                                      retained_since_startdate.dt.days, retention_since_job_hop.dt.days)
    df['incumbent_retention_milestone'] = np.where((df['incumbent_worker'] == "Yes") & (df['last_job_hop'].isnull()) |
                                                   (retention_since_job_hop <= settings.zero_days),
                                                   retained_since_intake.dt.days, retention_since_job_hop.dt.days)
    df['retention_milestone'] = np.where(df['incumbent_worker'] == 'Yes', df['incumbent_retention_milestone'],
                                         df['nonincumbent_retention_milestone'])
    df['employment_milestone'] = np.where(df['incumbent_worker'] == 'Yes', retained_since_intake.dt.days,
                                          retained_since_startdate.dt.days)
    df['contact_milestone'] = np.where(df['incumbent_worker'] == 'Yes', update_since_intake.dt.days,
                                       update_since_startdate.dt.days)
    df['call due'] = np.where(
        (df['initial_placement_type'].notnull() & df['last_retention_status'].isnull()) |
        ((time_since_startdate > settings.thirty_days) & (update_since_startdate < settings.thirty_days)) |
        ((time_since_startdate > settings.ninety_days) & (update_since_startdate < settings.ninety_days)) |
        ((time_since_startdate > settings.one_eighty_days) & (update_since_startdate < settings.one_eighty_days)) |
        ((time_since_startdate > settings.one_year) & (update_since_startdate < settings.one_year)) |
        ((time_since_startdate > settings.two_year) & (update_since_startdate < settings.two_year)), "Yes", "No")
    return df


def apply_retention_data(df, activities_df):
    """
    Manipulate and apply retention data to the aggregated reporting df.
    :param df: reporting_df
    :param activities_df: Dataframe created from activities.csv
    :return: Modified reporting_df that features all relevant retention information.
    """
    retention_df = format_retention_df(activities_df)
    df = incorporate_advancements(retention_df, df)
    df = incorporate_last_retention_data(retention_df, df)
    df = incorporate_last_date_retained(retention_df, df)
    df = coerce_to_datetime(df, 'last_date_retained', 'last_retention_update', )
    df = identify_milestones(df)

    return df


def format_cohort_df(activities_df):
    """
    Properly format cohort data to be incorporated into the reporting df.
    :param activities_df: activities_df
    :return: Dataframe made up of Cohort records.
    """
    df = activities_df.rename(columns={'startdate': 'cohort_date'})
    df = df[df['type'] == 'Cohort']
    coerce_to_datetime(df, 'date')
    df = df[df['date'] == df.groupby('accountid').date.transform('max')]
    df = df[['accountid', 'cohort_date']].copy()
    return df


def apply_cohort_data(df, activities_df):
    """
    Manipulate and apply cohort data to the aggregated reporting df.
    :param df: reporting_df
    :param activities_df: activities_df
    :return: Modified reporting_df featuring Cohort data
    """
    cohort_df = format_cohort_df(activities_df)
    df = pd.merge(df, cohort_df, how='left', on='accountid')
    df = coerce_to_datetime(df, 'cohort_date')
    df = df.drop_duplicates(subset='accountid')
    return df


def format_certification_df(df):
    """
    Format certification df to be incorporated into reporting df.
    :param df: activities_df
    :return: Dataframe containing certification status and accountid.
    """
    df.loc[:, 'gained_certification'] = 'Yes'
    df = df.drop_duplicates(subset=['accountid']).copy()
    df = df[['accountid', 'gained_certification']].copy()
    return df


def create_certification_columns(df, reporting_df):
    """
    Create a column for each certification type, indicating if the client has gained said type.
    :param df: certification_df
    :param reporting_df: reporting_df
    :return: Modified reporting_df featuring columns of date and type for each type of certification.
    """
    certification_df = df.dropna(subset=['certification'])
    for i in settings.certification_types:
        certification_df[f"{i}"] = np.where(certification_df['certification'].str.contains(f"{i}"), 'Yes', 'No')
        df = certification_df[certification_df[f"{i}"] == 'Yes'].rename(columns={'date': f"{i}_date"})
        df = coerce_to_datetime(df, f"{i}_date")
        df = df[['accountid', f"{i}", f"{i}_date"]]
        reporting_df = pd.merge(reporting_df, df, how='left', on='accountid')
        reporting_df = reporting_df.drop_duplicates(subset=['accountid'])
    return reporting_df


def apply_certification_data(reporting_df, activities_df):
    """
    Manipulate and apply certification data to reporting df.
    :param reporting_df: reporting_df
    :param activities_df: activities_df
    :return: Modified reporting_df featuring all relevant certification columns
    """
    certification_df = activities_df[activities_df['type'] == 'Certification']
    df = create_certification_columns(certification_df, reporting_df)
    if len(certification_df) > 0:
        certification_df = format_certification_df(certification_df)
        df = pd.merge(df, certification_df, how='left', on='accountid')
    else:
        df['gained_certification'] = "No"
    return df


def format_training_status_df(activities_df):
    """
    Produce a dataframe of each client's training status.
    :param activities_df: activities_df
    :return: Dataframe containing the training status for each accountid.
    """
    df = activities_df[activities_df['type'] == 'Training Status']
    df = df[df['trainingstatus'] == "Complete"]
    df = df.rename(columns={'trainingstatus': 'training_status'})
    df = df[['accountid', 'training_status']]
    return df


def apply_training_status_data(reporting_df, activities_df):
    """
    Manipulate and apply training status data to reporting df.
    :param reporting_df: reporting_df
    :param activities_df: activities_df
    :return: Modified reporting_df featuring each client's training status.
    """
    training_status_df = format_training_status_df(activities_df)
    df = pd.merge(reporting_df, training_status_df, how='left', on='accountid')
    df = df.drop_duplicates(subset=['accountid'])
    return df


def format_inactive_df(activities_df):
    """
    Format Inactive dataframe to be incorporated into the reporting df.
    :param activities_df: activities_df
    :return: Dataframe the consists of accountid's and inactive status.
    """
    df = activities_df[(activities_df['type'] == 'Active') | (activities_df['type'] == 'Inactive')].copy()

    coerce_to_datetime(df, 'date')
    df = df[df['date'] == df.groupby('accountid').date.transform('max')]

    df.loc[:, 'inactive'] = np.where(df['type'] == "Inactive","Yes","No")
    df = df[['accountid', 'inactive']]
    return df


def apply_inactive_data(reporting_df, activities_df):
    """
    Manipulate and apply inactive data to the reporting df.
    :param reporting_df: reporting_df
    :param activities_df: activities_df
    :return: Modified reporting_df that features inactive status.
    """
    inactive_df = format_inactive_df(activities_df)
    df = pd.merge(reporting_df, inactive_df, how='left', on='accountid')
    df = df.drop_duplicates(subset=['accountid'])

    return df


def format_snap_fee_confirmed_df(activities_df):
    """
    Properly format SNAP FEE DF to be incorporated in reporting df.
    :param activities_df: activities_df
    :return: Dataframe featuring columns of SNAP confirmed clients and their eligibility month.
    """
    df = activities_df[activities_df['type'] == 'SNAP FEE Confirmed'].drop_duplicates('accountid')
    coerce_to_datetime(df, 'date')
    df = df[df['date'] == df.groupby('accountid').date.transform('min')]
    df['initial_confirmation'] = pd.DatetimeIndex(df['date']).strftime('%m-%Y')
    df['eligible_period'] = pd.DatetimeIndex(df['date']).month
    return df


def apply_eligible_month_columns(snap_df, reporting_df):
    """
    Write a column for each month that SNAP Client is Found Eligible.
    :param snap_df: Dataframe of SNAP eligible clients.
    :param reporting_df: reporting_df
    :return: Modified reporting_df that features a column for each month a client is SNAP eligible.
    """
    df1 = snap_df[['accountid', 'initial_confirmation' ,'eligible_period', 'type']].copy()
    df2 = snap_df[['accountid', 'initial_confirmation','eligible_period']].drop_duplicates(subset=['accountid'])
    for i in range(1, 13):
        df1[f"SNAP {settings.months[i - 1]}"] = np.where(df1['eligible_period'] == i, 'E', '')
        df3 = df1[df1[f"SNAP {settings.months[i - 1]}"] == 'E']
        df2 = pd.merge(df2, df3[['accountid', f"SNAP {settings.months[i - 1]}"]], how='left', on='accountid')
    df2 = df2.fillna('')
    df2 = df2.drop_duplicates(subset=['accountid'])
    reporting_df = pd.merge(reporting_df, df2, how='left', on='accountid')
    return reporting_df


def apply_snap_fee_data(reporting_df, activities_df):
    """
    Manipulate and Apply SNAP FEE data to reporting df.
    :param reporting_df: reporting_df
    :param activities_df: activities_df
    :return: Modified reporting_df featuring all relevant SNAP data.
    """
    snap_fee_df = format_snap_fee_confirmed_df(activities_df)
    return apply_eligible_month_columns(snap_fee_df, reporting_df)

def format_earn_entry_df(activities_df):
    """
    Create a dataframe made up of earn entry activities
    :param activities_df: activities_df
    :return:
    """
    df = activities_df[activities_df['type'] == 'EARN Entry'].drop_duplicates('accountid')
    coerce_to_datetime(df, 'startdate')
    df = df[df['startdate'] == df.groupby('accountid').startdate.transform('max')]
    df['earn_entry'] = df['startdate']
    return df

def format_earn_exit_df(activities_df):
    """
    Create a dataframe made up of earn entry activities
    :param activities_df: activities_df
    :return:
    """
    df = activities_df[activities_df['type'] == 'EARN Exit'].drop_duplicates('accountid')
    coerce_to_datetime(df, 'startdate') #todo remove redundant function for df creation
    df = df[df['startdate'] == df.groupby('accountid').startdate.transform('max')]
    df['earn_exit'] = df['startdate']
    return df

def apply_earn_entry_exit_data(reporting_df, activities_df):
    """
    Manipulate and Apply EARN Entry/Exit data to reporting df
    :param reporting_df: reporting_df
    :param activities_df: activities_df
    :return:
    """
    earn_entry_df = format_earn_entry_df(activities_df)
    earn_exit_df = format_earn_exit_df(activities_df)
    earn_df = pd.merge(earn_entry_df[['accountid','earn_entry']], earn_exit_df[['accountid', 'earn_exit']], how='left',
                  on='accountid')
    return pd.merge(reporting_df, earn_df, how='left', on='accountid')

def apply_grant_id_df(grant, reporting_df, activities_df):
    """
    Properly format snap/earn id df to be incorporated in reporting df.
    :param grant: SNAP or EARN
    :param reporting_df: reporting_df
    :param activities_df: activities_df
    :return: Modified reporting_df that features a column for SNAP/EARN ID
    """
    df = activities_df[activities_df['type'] == grant]
    df.loc[:, f"{grant}"] = df['description'].copy()
    df = df[['accountid', f"{grant}"]]
    reporting_df = pd.merge(reporting_df, df, how='left', on='accountid')
    reporting_df = reporting_df.drop_duplicates(subset=['accountid'])

    return reporting_df

def apply_dol_wage_records(reporting_df):
    df = pd.read_excel(settings.dol_wage_record)
    reporting_df = pd.merge(reporting_df, df, how='left', on= 'accountid')
    return reporting_df

# noinspection PyTypeChecker
def calculate_client_age(df):
    """
    Calculate client age and convert to integer.
    :param df: reporting_df
    :return: Modified reporting_df with caluclated client age.
    """
    coerce_to_datetime(df,'dob')
    df['dob'] = df['dob'].where(df['dob'] < pd.Timestamp('now'), df['dob'] - np.timedelta64(100, 'Y'))
    df['age'] = (pd.Timestamp('now') - df['dob']).astype('<m8[Y]').fillna(0.0).astype(int)
    return df


def identify_cdbg(df):
    """
    Determine CDBG Eligibility
    :param df: reporting_df
    :return:
    """
    print("Identifying CDB") #todo identify redundant actions
    df['bc_resident'] = np.where(
        df['addresspostcode/zip'].fillna(0).replace({'-': ''}, regex=True).astype('int64').isin(settings.bc_zips), "Yes", "No") # todo clean up this function!
    df['CDBG'] = np.where((df['addresscity'].str.contains('altimor')) &
                          (df['incomecategory'] != '') &
                          (df['incomecategory'].notnull()) &
                          (df['race'].notnull()) &
                          (df['race'] != '') &
                          (df['bc_resident'] == 'Yes'), "CDBG", "")
    return df


def kpi_statistics(df):
    """
    Create Columns for the KPI data points.
    :param df: reporting_df
    :return: Modified reporting_df featuring columns that track client KPI's
    """
    df['program_completion'] = np.where(
        (df['training_status'] == 'Complete') |
        (df['gained_certification'] == 'Yes') |
        df['initial_placement_type'].notnull(), 'Yes', 'No')
    df['gained_employment'] = np.where(
        df['initial_placement_type'].notnull(), 'Yes', 'No')
    df['enrollment_satisfied'] = np.where(
        (df['originaltrainingprogram'] == 'OOO') |
        (df['cohort_date'].notnull()), 'Yes', 'No')
    df['enrollment_pending'] = np.where(
        ((df['originaltrainingprogram'].notnull()) &
         (df['enrollment_satisfied'] != 'Yes') &
         (df['inactive'] != 'Yes')), 'Yes', 'No')
    df['currently_employed'] = np.where(
        ((df['gained_employment'] == 'Yes') |
         (df['incumbent_worker'] == 'Yes')) &
        (df['last_retention_status'] != 'Job Not Retained'),
        'Yes', 'No')
    df['active'] = np.where(
        ((df['currently_employed'] != 'Yes') | (df['incumbent_worker'] == 'Yes')) &
        ((df['gained_employment'] != "Yes") | (df['last_retention_status'].str.contains("Job Not Retained"))) &
        (df['inactive'] != 'Yes') &
        (df['originaltrainingprogram'].notnull()), 'Yes', 'No')
    df['status_unknown'] = np.where(
        (df['originaltrainingprogram'].notnull()) &
        (df['inactive'] != 'Yes') &
        (df['active'] != 'Yes') &
        (df['currently_employed'] != 'Yes'),
        'Yes', '')
    df['days_to_employment'] = (df['initial_startdate'] - df['originalintakedate']).dt.days
    df['completed_without_employment'] = np.where((df['program_completion'] == 'Yes') &
                                                  (df['gained_employment'] != 'Yes') &
                                                  (df['inactive'] != 'Yes'),"Yes","No")
    df['in_active_training'] = np.where(
        (df['cohort_date'] == df['cohort_date'].max()) &
        (pd.to_datetime('today') <= (pd.to_datetime(df['cohort_date'],errors='coerce') + pd.to_timedelta('21 days'))),
        "Yes","No")

    df['incumbent_wage_increase'] = np.where(
        (((df['previouswagehr'].notnull()) & (df['previouswagehr'] != '') & ((df['previouswagehr'] != ' ') &
                                                                              (df['previouswagehr'] != 0))) &
         (df['previouswagehr'] < df['current_wage'])) & (df['incumbent_worker'] == 'Yes'), 'Yes', 'No')

    df['incumbent_hours_increase'] = np.where(
        (((df['previoushoursworked'].notnull()) & (df['previoushoursworked'] != '') & ((df['previoushoursworked'] != ' ') &
                                                                             (df['previoushoursworked'] != 0))) &
         (df['previoushoursworked'].fillna(0).astype(int) < df['current_hours'].fillna(0).astype('int64'))) &
        (df['incumbent_worker'] == 'Yes'), 'Yes', 'No')

    df['unreported_placement'] = np.where(
        ((df['gained_employment'] != "Yes") & (df['dol_confirmed'] == 'Y')), "Yes", "No"
    )

    return df


def gained_new_employment(df):
    """
    Create a column in the dataframe that identifies if client has gained NEW employment since most recent intake date
    :param df:
    :return:
    """
    df['Gained New Employment'] = np.where(df['current_startdate'].notnull() &
                                           (df['originalintakedate'] <= df['current_startdate']), "Yes", "No")

    df['incumbent_advancement'] = np.where(((df['incumbent_wage_increase'] == 'Yes') |
                                           (df['incumbent_hours_increase'] == 'Yes') &
                                            (df['Gained New Employment'] == 'No')), 'Yes', 'No')
    return df


def format_demographics(df):
    """
    Format Demographic Data Appropriately.
    :param df: reporting_df
    :return: Modified reporting_df that features columns of information derived from demographic data and activities.
    """
    df = calculate_client_age(df)
    # Convert numeric columns
    df[settings.numeric_cols] = df[settings.numeric_cols].apply(
        pd.to_numeric, errors='coerce', axis=1)
    df = identify_cdbg(df)
    df = kpi_statistics(df)
    df = gained_new_employment(df)
    df['call due'] = np.where(df['inactive'] == "Yes","No",df['call due'])
    return df


def format_reporting_df(df):
    """
    Format the reporting df.
    :param df: reporting_df
    :return: Modified reporting_df with capitalized lettering etc.
    """
    df = df.sort_values(by=['name'])
    df = df.rename(
        columns={"accountid": "Account ID", "addresscity": "city", "maritalstatus": "Marital Status",
                 "validdriverslicense": "Valid DL", "workingvehicle": "Vehicle", "femalehh": "Female HH",
                 "latino": "Ethnicity", "transhome": "Transitional Home", "incomesources": "Income Source",
                 "howlongjobless": "Time Unemployed", "incomecategory": "Income Category",
                 "criminalconviction": "Criminal Conviction", "highesteducation": "Highest Education",
                 "tickettowork": "TTW", "substanceabusehistory": "Substance Abuse History", "grantfund": "Grant Fund",
                 "nationalorigin": "National Origin", 'addresscounty/state': 'State', 'addresspostcode/zip': 'Zip',
                 'originalintakedate': 'Original Intake Date', 'phone2': 'Phone 2', 'previouswagehr': 'Last Wage',
                 'otherincome': 'Other Income', 'monthlyhhincome': 'Monthly HH Income',
                 'mentalabusehistory': 'Mental Abuse History', 'originaltrainingprogram': 'Original Training Program'})

    df = df.drop(['secondaryintake', 'certifications', 'createddate', 'modifieddate', 'ownerid'], axis=1)

    df.columns = df.columns.str.replace('_', ' ').str.title()

    df = format_date_columns(df)

    return df


def format_date_columns(df):
    """
    Format all date columns for easy reading.
    :param df: reporting_df
    :return: Modified reporting_df with appropriately formatted date columns.
    """
    for i in settings.date_columns:
        df[f'{i}'] = pd.to_datetime(df[f'{i}']).dt.strftime('%m/%d/%Y')
    return df


def format_grant_fund(df):
    """
    Incorporate the CDBG, SNAP ID, & EARN ID columns to modify Grant Fund column to include those grants if applicable.
    :param df: reporting_df
    :return: Modified reporting_df
    """
    df['Grant Fund'] = df['Grant Fund'].fillna('')
    df['Grant Fund'] = np.where((df['Cdbg'] == 'CDBG') & (df['Grant Fund'].str.contains('CDBG') == False),
                                (df['Grant Fund'] + '; CDBG'), df['Grant Fund'])
    df['Grant Fund'] = np.where((df['Snap Id'].notnull() & (df['Grant Fund'].str.contains('SNAP') == False)),
                                (df['Grant Fund'] + '; SNAP'), df['Grant Fund'])
    df['Grant Fund'] = np.where((df['Earn Id'].notnull() & (df['Grant Fund'].str.contains('EARN') == False)),
                                (df['Grant Fund'] + '; EARN'), df['Grant Fund'])
    df['Grant Fund'] = df['Grant Fund'].str.lstrip(";")
    return df



def form_reporting_df():
    """
    Combine pertinent information from csv documents to develop an aggregated dataframe of RSS data.
    :return: Final reporting_df
    """
    accounts_df, activities_df = get_accounts_activities_dataframes(settings.accounts_csv, settings.activities_csv)
    reporting_df = initiate_reporting_df(accounts_df)
    #reporting_df = apply_returning_client_data(reporting_df, activities_df)
    reporting_df = assign_job_coach_initials(reporting_df)
    reporting_df = apply_employment_data(reporting_df, activities_df)
    reporting_df = apply_retention_data(reporting_df, activities_df)
    reporting_df = apply_cohort_data(reporting_df, activities_df)
    reporting_df = apply_certification_data(reporting_df, activities_df)
    reporting_df = apply_training_status_data(reporting_df, activities_df)
    reporting_df = apply_inactive_data(reporting_df, activities_df)
    reporting_df = apply_snap_fee_data(reporting_df, activities_df)
    reporting_df = apply_earn_entry_exit_data(reporting_df, activities_df)
    reporting_df = apply_grant_id_df("SNAP ID", reporting_df, activities_df)
    reporting_df = apply_grant_id_df("EARN ID", reporting_df, activities_df)
    reporting_df = apply_dol_wage_records(reporting_df)
    reporting_df = format_demographics(reporting_df)
    reporting_df = assign_fiscal_quarter(reporting_df)
    reporting_df = assign_fiscal_year(reporting_df)
    reporting_df = assign_intake_quarter(reporting_df)
    reporting_df = assign_intake_fy(reporting_df)
    reporting_df = format_reporting_df(reporting_df)
    reporting_df = format_grant_fund(reporting_df)
    reporting_df.to_csv(settings.reporting_df_csv)
    return reporting_df
