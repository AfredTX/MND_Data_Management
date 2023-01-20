import client_directories_module as cdm
import data_collection_module as dcm
import data_manipulation_module as dmm
import fy_reports_module as frm
import V14_intake_module as im
from shared_libs.settings_RSS import Settings
import grant_reports_module as gr
import activity_posting_module as ap

settings = Settings()



def organize_data():
    """
    Collects and organizes data and creates reporting files.
    :return:
    """
    ap.automated_activity_updates()
    try:
        im.complete_intake_process(settings.fred_authorization,
                                   settings.directory_path,
                                   settings.processed_documents_path)
        dcm.collect_data()
    except KeyError:
        print("KeyError: We may have maxed out our allotted daily/monthly API calls. No new data will be exported.")
    while True:
        try:
            dmm.form_reporting_df()
            cdm.update_client_directories()
            frm.update_fy_reports()
            gr.write_grant_reports()
            break
        except PermissionError:
            run = input("File Permission Denied: Ensure that all necessary files "
                        "are closed. Enter 'run' to try again when files are closed.")
            if run.rstrip() == 'run':
                continue
    #jbw.scrape_jobs_to_google("Forklift")
    #jbw.scrape_jobs_to_google("CDL B")
    #jbw.scrape_jobs_to_google("Warehouse")

