import pandas as pd
import json
from settings_RSS import Settings
from client_directories_module import write_excel
import xlsxwriter

settings = Settings()

def write_grant_reports():
    df = pd.read_csv(settings.reporting_df_csv)

    grant_cycles = json.loads(settings.grant_cycles)
    for grant in grant_cycles:
        print(grant)
        for cycle in grant_cycles[f"{grant}"]:
            print(cycle)
            start_date = grant_cycles[f"{grant}"][f"{cycle}"]["start"]
            end_date = grant_cycles[f"{grant}"][f"{cycle}"]["end"]
            if grant == 'SNAP':
                cycle_df = df[
                    (df["Grant Fund"].str.contains(f"{grant}")) &
                    (pd.to_datetime(df["Initial Confirmation"], errors='coerce') >= pd.to_datetime(start_date)) &
                    (pd.to_datetime(df['Initial Confirmation'], errors='coerce') < pd.to_datetime(end_date))]
            elif grant == 'EARN':
                cycle_df = df[
                    (df["Grant Fund"].str.contains(f"{grant}")) &
                    (pd.to_datetime(df["Earn Entry"], errors='coerce') >= pd.to_datetime(start_date)) &
                    (pd.to_datetime(df['Earn Entry'], errors='coerce') < pd.to_datetime(end_date))]
            elif grant == 'CDBG':
                cycle_df = df[
                    (df['Fiscal Year'] == pd.to_datetime(end_date).year) &
                    (df["Grant Fund"].str.contains(f"{grant}"))
                ]
            else:
                cycle_df = df[
                    (df["Grant Fund"].str.contains(f"{grant}")) &
                    (pd.to_datetime(df["Original Intake Date"], errors='coerce') >= pd.to_datetime(start_date)) &
                    (pd.to_datetime(df['Original Intake Date'], errors='coerce') < pd.to_datetime(end_date))]
            print(f"{len(cycle_df)} clients in {grant}-{cycle}")
            filename = f"{settings.grant_reports_path}\\{grant}_{cycle}.xlsx"

            cycle_kpi_df = cycle_df[settings.kpi_columns].copy()
            cycle_employments = cycle_df[cycle_df['Gained Employment'] == 'Yes'][settings.kpi_employments].copy()
            cycle_certifications = cycle_df[cycle_df['Gained Certification'] == 'Yes'][settings.kpi_certifications].copy()
            while True:
                try:
                    write_excel(filename,'Data',cycle_df)
                    write_excel(filename,'KPIs', cycle_kpi_df)
                    write_excel(filename, 'Employments', cycle_employments)
                    write_excel(filename, 'Certifications', cycle_certifications)
                    break
                except FileNotFoundError:
                    print("File Doesn't Exist Yet, Let Me Make It!")
                    workbook = xlsxwriter.Workbook(filename)
                    workbook.add_worksheet('Data')
                    workbook.add_worksheet('KPIs')
                    workbook.add_worksheet('Employments')
                    workbook.add_worksheet('Certifications')
                    workbook.close()
                    print(f"{filename} created!")
                except KeyError:
                    print(f"Unknown Keyerror ocurred when updating {filename}")

            if settings.username == "Fred":
                print("Backing Up in OneDrive")
                filename = f"{settings.od_grant_reports_path}\\{grant}_{cycle}.xlsx"

                cycle_kpi_df = cycle_df[settings.kpi_columns].copy()
                cycle_employments = cycle_df[cycle_df['Gained Employment'] == 'Yes'][settings.kpi_employments].copy()
                cycle_certifications = cycle_df[cycle_df['Gained Certification'] == 'Yes'][
                    settings.kpi_certifications].copy()
                while True:
                    try:
                        write_excel(filename, 'Data', cycle_df)
                        write_excel(filename, 'KPIs', cycle_kpi_df)
                        write_excel(filename, 'Employments', cycle_employments)
                        write_excel(filename, 'Certifications', cycle_certifications)
                        break
                    except FileNotFoundError:
                        print("File Doesn't Exist Yet, Let Me Make It!")
                        workbook = xlsxwriter.Workbook(filename)
                        workbook.add_worksheet('Data')
                        workbook.add_worksheet('KPIs')
                        workbook.add_worksheet('Employments')
                        workbook.add_worksheet('Certifications')
                        workbook.close()
                        print(f"{filename} created!")
                    except KeyError:
                        print(f"Unknown Keyerror ocurred when updating {filename}")
