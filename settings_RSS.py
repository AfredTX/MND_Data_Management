import pandas as pd
import os


class Settings:
    """A class to store the settings of RSS Database."""

    def __init__(self):
        """Initialize settings object and its attributes."""

        # User settings
        self.user_email = "frandall@mdnewdirections.org"

        # Set authorization settings
        #todo move credentials and alter filepath
        with open(fr'C:\Users\fredr\PycharmProjects\MND_Data_Management(2)\Credentials\auth.txt', 'r') as file:
            auth = file.read()
        self.fred_authorization = {'Authorization': f'{auth}'}
        self.posting_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'{auth}'}

        # Set url settings
        self.accounts_url = 'https://apiv4.reallysimplesystems.com/accounts'
        self.activities_url = 'https://apiv4.reallysimplesystems.com/activities'
        self.documents_url = 'https://apiv4.reallysimplesystems.com/documents'
        self.info_survey_url = 'https://forms.office.com/r/bhQvpTTyqk'

        # Set google sheets id's
        # todo move credentials and alter filepath
        self.google_creds = fr"C:\Users\fredr\PycharmProjects\MND_Data_Management(2)\sheets-network-f964f31e5bf1.json"
        self.info_session_tracker = '1yp09eMrb3wfB6HslJ0yPriuKwosNjvbZlvyQB-tAHkw'
        self.info_session_registration = '1ooiRYTu9Jd2BgheprId8IOI1wZ88IqlGrGcav0WlLKY'
        self.fy22_training_attendance = '1RKjwFXC4xvrSmEM3w5bwkHn4JphWHmF5nbwFMA2gH9I'
        self.fy23_training_attendance = '1oHAwdaho-O3mhfNADSQ0Q6MzfxKcCNIYNdvBIrAwSjM'

        # Set url add ons
        self.record_limit = '?limit=100'
        self.starting_page = 1
        self.page_setting = f'&page={self.starting_page}'

        # Set file settings
        self.directory_path = os.getcwd()
        self.data_management_path = fr"C:\Users\fredr\OneDrive - Maryland New Directions\Data Management"
        self.client_directory_path = fr"{self.directory_path}\client_directories"
        self.call_history = fr"{self.directory_path}\rss_data\api_call_history.json"
        self.accounts_csv = fr"{self.directory_path}\rss_data\accounts.csv"
        self.activities_csv = fr"{self.directory_path}\rss_data\Activities.csv"
        self.reporting_df_csv = fr"{self.directory_path}\rss_data\reporting_df.csv"
        self.processed_documents_path = fr"{self.directory_path}\Processed Documents"
        self.ch_client_directory = fr"{self.client_directory_path}\CH Client Directory 2.0.xlsx"
        self.ml_client_directory = fr"{self.client_directory_path}\ML Client Directory 2.0.xlsx"
        self.rb_client_directory = fr"{self.client_directory_path}\RB Client Directory 2.0.xlsx"
        self.rv_client_directory = fr"{self.client_directory_path}\RV Client Directory 2.0.xlsx"
        self.sh_client_directory = fr"{self.client_directory_path}\SH Client Directory 2.0.xlsx"
        self.ms_client_directory = fr"{self.client_directory_path}\MS Client Directory 2.0.xlsx"
        self.vf_client_directory = fr"{self.client_directory_path}\VF Client Directory 2.0.xlsx"
        self.complete_client_directory = fr"{self.client_directory_path}\Complete Client Directory 2.0.xlsx"
        self.ytd_reports = fr"{self.directory_path}\ytd_reports"
        self.grant_reports_path = fr"{self.directory_path}\grant_reports"
        self.dol_wage_record = fr"{self.directory_path}\dol_wages.xlsx"

        # Set Activity Types Settings
        self.activity_types = ["Client Became Employed", "Retention",
                               "Certification", "Training Status", "Cohort",
                               "Returning Client", "Inactive", "SNAP Fee Confirmed",
                               "SNAP ID", 'EARN ID', 'EARN Entry', 'EARN Exit', 'Active', 'Train Up Activity']
        self.coach_activities = ["Client Became Employed", "Retention",
                                 "Certification", "Returning Client",
                                 "Inactive"]
        self.week_end_activities = ["Client Became Employed", "Retention",
                                    "Certification", "Inactive"]

        # Set Employment Detail Settings
        self.employment_details = ['Full Time', 'Benefits', 'Temporary',
                                   'MND Lead', 'Industry Related', 'Job Hopping']

        # Set Certification Types
        self.certification_types = ['Forklift', 'CGSP', 'DOT', 'BTWT', 'CDL-A','CDL-B',
                                    'CCS', 'CLP', 'TWIC']

        # Set Column Format Types
        self.numeric_cols = ['children', 'initial_wage', 'current_wage',
                             'previouswagehr', 'monthlyhhincome']

        # Set Date Settings
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                       'Oct', 'Nov', 'Dec']
        self.date_columns = ['Original Intake Date', 'Dob', 'Initial Startdate',
                             'Current Startdate', 'Last Retention Update',
                             'Last Date Retained', 'Cohort Date',
                             'Forklift Date', 'Cgsp Date', 'Dot Date',
                             'Btwt Date', 'Ccs Date', 'Clp Date', 'Cdl-A Date','Cdl-B Date','Twic Date']
        # Set Program Settings
        self.programs = ["MTDL", "CF", "CTC", "OOO"]

        # Set Grant Settings
        self.accepted_grants = ['CDBG', 'DOL Opioid', 'EARN', 'Grads2Careers', 'MOED Opioid','OWIF', 'OWIF-W', 'SNAP',
                                'WIOA']
        # todo alter filepath
        with open(fr'C:\Users\fredr\PycharmProjects\MND_Data_Management(2)\grant_cycles.json', 'r') as file:
            self.grant_cycles = file.read()

        # Set Job Coach Settings
        self.coach_initials = ['CH', 'ML', 'RB', 'RV', 'SH', 'MS', 'VF']
        self.coach_directories = [
            self.ch_client_directory, self.ml_client_directory,
            self.rb_client_directory, self.rv_client_directory,
            self.sh_client_directory, self.ms_client_directory, self.vf_client_directory]

        self.coach_contact = {'CH': 'churt@mdnewdirections.org', 'ML': 'mlewis@mdnewdirections.org',
                              'RV': 'rvallance@mdnewdirections.org', 'RB': 'rbaker@mdnewdirections.org',
                              'SH': 'sgibbs@mdnewdirections.org', 'MS': 'mshearn@mdnewdirections.org',
                              'VF': 'vfrierson@mdnewdirections'}

        # Set Time Settings
        # noinspection PyUnresolvedReferences
        self.today = pd.to_datetime("today").normalize()
        self.current_week = self.today - pd.Timedelta(6, unit='d')
        self.one_year_ago = self.today - pd.Timedelta(365, unit='d')
        self.two_years = self.today - pd.Timedelta(730, unit='d')
        self.zero_days = pd.to_timedelta('0 days')
        self.now = pd.Timestamp.now()
        self.thirty_days = pd.to_timedelta('30 days')
        self.ninety_days = pd.to_timedelta('90 days')
        self.one_eighty_days = pd.to_timedelta('180 days')
        self.one_year = pd.to_timedelta('365 days')
        self.two_year = pd.to_timedelta('730 days')

        # pw settings
        # todo move credentials and alter filepath
        with open(fr'C:\Users\fredr\PycharmProjects\MND_Data_Management(2)\Credentials\pw.txt', 'r') as file:
            pw = file.read()
        self.passcode = pw

        # Set KPI columns
        self.kpi_columns = ['Account Id', 'Name', 'Grant Fund', 'Case Manager','Original Intake Date',
                            'Original Training Program',
                            'Cohort Date', 'Quarter', 'Fiscal Year', 'Active', 'Enrollment Satisfied',
                            'Enrollment Pending', 'Program Completion', 'Gained Employment', 'Currently Employed',
                            'Gained Certification', 'Retention Milestone', 'Employment Milestone', 'Contact Milestone',
                            'Last Retention Update', 'Last Retention Status', 'Last Date Retained', 'Last Job Hop',
                            'Advancement', 'Initial Startdate', 'Initial Employer', 'Initial Position', 'Initial Wage',
                            'Initial Hours', 'Initial Benefits', 'Initial Temporary', 'Initial Mnd Lead',
                            'Initial Industry Related', 'Current Startdate', 'Current Employer', 'Current Position',
                            'Current Wage', 'Current Hours', 'Current Benefits', 'Current Temporary',
                            'Current Mnd Lead', 'Current Industry Related', 'Call Due',  'Forklift', 'Forklift Date',
                            'Cgsp', 'Cgsp Date', 'Dot', 'Dot Date', 'Btwt', 'Btwt Date', 'Cdl-A', 'Cdl-A Date','Cdl-B',
                            'Cdl-B Date', 'Clp', 'Clp Date', 'Twic', 'Twic Date', 'Snap Id', 'Earn Id',
                            'Days To Employment']

        self.kpi_employments = ['Name', 'Grant Fund', 'Case Manager', 'Original Training Program',
                            'Cohort Date', 'Quarter', 'Fiscal Year', 'Gained Certification','Initial Startdate',
                            'Initial Employer', 'Initial Position', 'Initial Wage',
                            'Initial Hours', 'Initial Benefits', 'Initial Temporary', 'Initial Mnd Lead',
                            'Initial Industry Related', 'Current Startdate', 'Current Employer', 'Current Position',
                            'Current Wage', 'Current Hours', 'Current Benefits', 'Current Temporary',
                            'Current Mnd Lead', 'Current Industry Related', 'Retention Milestone',
                            'Employment Milestone', 'Contact Milestone',
                            'Last Retention Update', 'Last Retention Status', 'Last Date Retained', 'Last Job Hop',
                            'Advancement', 'Call Due']

        self.kpi_certifications = ['Name', 'Grant Fund', 'Case Manager', 'Original Training Program',
                            'Cohort Date', 'Quarter', 'Fiscal Year', 'Gained Employment', 'Forklift', 'Forklift Date',
                            'Cgsp', 'Cgsp Date', 'Dot', 'Dot Date', 'Btwt', 'Btwt Date', 'Cdl-A', 'Cdl-A Date', 'Cdl-B',
                                   'Cdl-B Date', 'Clp', 'Clp Date', 'Twic', 'Twic Date']

        # Intake document settings
        self.income_categories = ['Extremely Low Income','Low Income', 'Moderate Income']
        self.income_sources = ['Alimony', 'Salary/Wages', 'Child Support', 'SSI', 'SSDI', 'Cash Assistance/TCA',
                               'Unemployment', 'Social Security', 'SNAP/Food Stamp', 'Other Sources', 'No Income']
        self.races = ['Black/African American', 'White', 'Asian', 'Black/African American and White',
                      'American Indian/Alaskan Native and Black/African American', 'Other Multi-Racial Category',
                      'American Indian/Alaskan Native and White', 'Asian and White', 'American Indian/Alaskan Native',
                      'Native Hawaiian/Other Pacific Islander']
        self.barriers = ['Age', 'Appearance', 'Childcare', 'Criminal Background', 'Communication Skills', 'Disability',
                         'Education', 'Employment History', 'Family Circumstances', 'Health', 'Homeless', 'Illiteracy',
                         'Lack Job Search/Application Skills', 'Lack of Consistent Phone Number', 'Lack of Network',
                         'Resume', 'Self Esteem', 'Transportation']
        self.covid_effects = ['Business Closed', 'Laid Off', 'Credit Score Damage', 'Decrease In Work Hours',
                              'Food Insecurity', 'Health Physical or Mental', 'Inability To Pay Rent', 'Lost Child Care',
                              'Left Labor Force', 'Own Business Closed', 'Youth Adverse Experience',
                              'Covid Other Check']
        self.incumbent_details = ['incumbent_start_date','incumbent_employer', 'incumbent_position', 'hourly_wage',
                                  'hours_per_week']
        self.incumbent_benefits = ['Medical', 'Dental', 'Retirement', 'Stock Options', 'Profit Sharing', 'Wellness']
        self.rem_list = ['Contact 1 Phone', 'Contact 2 Phone', 'parole meeting', 'Last Job', 'Reason For Leaving',
                         'in custody', 'dependants in house', 'benefits received', 'total hh size', 'disabled',
                         'sixty-two plus', 'ft student', 'chargedate', 'crime', 'marylandid', 'children <18',
                         'client_childcare', 'homeowner', 'facingeviction', 'benefits', 'healthinsurance',
                         'confidentialityname', 'confidentialitydate', 'photoreleasename', 'photoreleasedate',
                         'cdbghhincomename', 'cdbghhincomeaddress', 'cdbghhincomezip', 'cdbghhincomedate',
                         'cdbghhincomestaffname', 'cdbghhincomestaffdate', 'cdbghhincomestafftitle', 'cdbgracename',
                         'cdbgracedate', 'cdbgracestaffname', 'cdbgracestafftitle', 'cdbgracestaffdate',
                         'not female hh', 'First Name', 'MI', 'Last Name', 'othersources', 'paroleprobation',
                         'not_latino', 'eligibletowork', 'Suffix', 'client_age', 'mentalabusenote', 'owner',
                         'snapincome', 'returning_client']
        self.v14_rem_list = ['Contact 1 Phone', 'parole meeting',
                         'in custody', 'total hh size', 'disabled',
                         'sixty-two plus', 'ft student', 'marylandid', 'children <18',
                         'client_childcare', 'homeowner', 'facingeviction',
                         'confidentialityname', 'confidentialitydate', 'photoreleasename', 'photoreleasedate',
                         'cdbghhincomename', 'cdbghhincomeaddress', 'cdbghhincomezip', 'cdbghhincomedate',
                         'cdbghhincomestaffname', 'cdbghhincomestaffdate', 'cdbghhincomestafftitle', 'cdbgracename',
                         'cdbgracedate', 'cdbgracestaffname', 'cdbgracestafftitle', 'cdbgracestaffdate',
                         'not female hh', 'First Name', 'MI', 'Last Name', 'othersources', 'paroleprobation',
                         'not_latino', 'eligibletowork', 'Suffix', 'owner', 'covid_other']

        self.cdbg_income_fields = ['ELI1','ELI2','ELI3','ELI4','ELI5','ELI6','ELI7','ELI8','LI1','LI2','LI3','LI4','LI5','LI6',
                            'LI7','LI8','MI1','MI2','MI3','MI4','MI5','MI6','MI7','MI8','01','02','03','04','05','06',
                            '07','08','cdbghhincomename','cdbghhincomeaddress','cdbghhincomezip','cdbghhincomedate',
                            'cdbghhincomestaffname','cdbghhincomestaffdate','cdbghhincomestafftitle']
        self.cdbg_race_fields = ['cdbgracename','cdbgracedate','cdbgracestaffname','cdbgracestafftitle',
                                 'cdbgracestaffdate','latino','not_latino','Black/African American','White','Asian',
                                 'Black/African American and White',
                                 'American Indian/Alaskan Native and Black/African American',
                                 'Other Multi-Racial Category',
                                 'American Indian/Alaskan Native and White','Asian and White',
                                 'American Indian/Alaskan Native','Native Hawaiian/Other Pacific Islander','femalehh',
                                 'not female hh','total hh size','disabled','sixty-two plus','ft student',
                                 'children <18']






        self.required_categories = 38

        # Exit Call Settings
        self.exit_call_columns = ['Account Id', 'Name', 'Phone', 'Phone 2', 'Email', 'Original Intake Date',
                                  'Case Manager', 'Original Training Program', 'Program Completion', 'Currently Employed',
                                  'Current Employer', 'Current Wage']
        self.exit_call_product_columns = ['Account Id', 'Name']
        self.exit_call_survey_questions = ['Contact', 'Currently Employed?', 'Start Date', 'End Date', 'Employer',
                                           'Position', 'Wage', 'Full Time', 'Temporary', 'Temporary', 'MND Lead',
                                           'Industry Related', 'Benefits' ,'Received Raise in Benefits/Hours/Wage',
                                           'Enroll For Further Services?', 'Notes']
        self.exit_call_path = f"{self.directory_path}\\Exit Calls"

        self.file_extensions = ['.pdf', '.docx', '.doc' ,'.jpeg', '.jpg', '.tif', '.JPG','.JPEG','PDF']

        with open(fr'C:\Users\fredr\PycharmProjects\MND_Data_Management(2)\train_up_activity_index.json', 'r') as file:
            self.train_up_json = file.read()

        self.bc_zips = [21215, 21206, 21224, 21218, 21207, 21229, 21217, 21225, 21212, 21230, 21213, 21239, 21216,
                        21209, 21223, 21214, 21202, 21201, 21205, 21211, 21210, 21231, 21226, 21287, 21251, 21278,
                        21290, 21203, 21264, 21263, 21273, 21270, 21275, 21274, 21279, 21281, 21280, 21283, 21289,
                        21288, 21297, 21298, 21233, 21265]

        # todo create dictionary of baltimore cities>counties>zips


        # One Drive backup
        with open(fr'C:\Users\fredr\PycharmProjects\MND_Data_Management(2)\username.txt', 'r') as file:
            self.username = file.read()
        if self.username == "Fred":
            self.data_management_path = fr"C:\Users\fredr\OneDrive - Maryland New Directions\Data Management"
            self.od_client_directory_path = fr"{self.data_management_path}\Client Directories"
            self.od_ch_client_directory = fr"{self.od_client_directory_path}\CH Client Directory 2.0.xlsx"
            self.od_ml_client_directory = fr"{self.od_client_directory_path}\ML Client Directory 2.0.xlsx"
            self.od_rb_client_directory = fr"{self.od_client_directory_path}\RB Client Directory 2.0.xlsx"
            self.od_rv_client_directory = fr"{self.od_client_directory_path}\RV Client Directory 2.0.xlsx"
            self.od_sh_client_directory = fr"{self.od_client_directory_path}\SH Client Directory 2.0.xlsx"
            self.od_ms_client_directory = fr"{self.od_client_directory_path}\MS Client Directory 2.0.xlsx"
            self.od_vf_client_directory = fr"{self.od_client_directory_path}\VF Client Directory 2.0.xlsx"
            self.od_complete_client_directory = fr"{self.od_client_directory_path}\Complete Client Directory 2.0.xlsx"
            self.od_ytd_reports = fr"{self.data_management_path}\YTD Reports"
            self.od_grant_reports_path = fr"{self.data_management_path}\Grant Reports"

            self.od_coach_directories = [
                self.od_ch_client_directory, self.od_ml_client_directory,
                self.od_rb_client_directory, self.od_rv_client_directory,
                self.od_sh_client_directory, self.od_ms_client_directory, self.od_vf_client_directory]


