from rpy2.robjects import pandas2ri
import rpy2.robjects as robjects
from r_code.r_code import r_code
import pandas as pd
import json, os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

robjects.r('library(dplyr)')
robjects.r('library(restriktor)')
robjects.r('library(tidyr)')
pandas2ri.activate()

def convert_to_r_dataframe(data_frame):
    return pandas2ri.py2rpy(data_frame)

def run_r_analysis(merged_data, v_values):
    robjects.r(r_code)
    r_function = robjects.globalenv['perform_analysis']
    result = r_function(merged_data, v_values)
    return result

def convert_to_pandas_dataframe(result):
    total_revenue = pd.DataFrame(result)
    return total_revenue.values.flatten().tolist()

def perform_analysis_with_r_integration(data, enumerator_name):
    merged_data = pd.DataFrame(data)
    directory = "/home/ubuntu/apps/real_estate_property_tax_app/real_estate_property_tax_app/Array_for_R_code"
    if not os.path.exists(directory):
        os.makedirs(directory)
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_filename = os.path.join(directory, f"{enumerator_name}_{current_datetime}.json")
    merged_data.to_json(json_filename, orient='records', indent=2)
    v_values = pd.read_csv("v_values_v4.csv")
    pandas2ri.deactivate()
    pandas2ri.activate()

    merged_data_r = convert_to_r_dataframe(merged_data)
    v_values_r = convert_to_r_dataframe(v_values)
    result = run_r_analysis(merged_data_r, v_values_r)

    return convert_to_pandas_dataframe(result)


def update_google_sheet(filepath):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file('/home/ubuntu/apps/real_estate_property_tax_app/tax-app-420312-51aaf545a365.json', scopes=SCOPES)
        gc = gspread.authorize(creds)
        sheet_url = 'https://docs.google.com/spreadsheets/d/1jiXbgYlPdI5FJQVMK4H66hJ8g3SMB9nNpfj_wVNgSJg/edit#gid=0'
        sheet = gc.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)
        df = pd.read_csv(filepath)
        # Convert DataFrame to a list of lists (each inner list represents a row)
        data = df.values.tolist()
        worksheet.append_rows(data)
        print("Google Sheet updated successfully.")
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")


def save_to_csv(data, filename, total_revenue):
    directory = '/home/ubuntu/apps/real_estate_property_tax_app/backup_for_sheet2'
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Create DataFrame from filtered data
    df = pd.DataFrame(data)

    # Add 'revenue_value' column to the DataFrame with the total_revenue value
    df['revenue_value'] = total_revenue[0]

    # Rearrange column order to place 'revenue_value' before 'end_time' and 'deviceName'
    columns = list(df.columns)
    columns.insert(columns.index('end_time'), columns.pop(columns.index('revenue_value')))
    df = df[columns]

    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Save DataFrame to CSV with filename as enumerator_name_datetime.csv
    filepath = os.path.join(directory, f'{filename}_{current_datetime}.csv')
    df.to_csv(filepath, index=False)
    update_google_sheet(filepath)


def save_dashboard_1_data_on_sheets(data):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(
            '/home/ubuntu/apps/real_estate_property_tax_app/tax-app-420312-51aaf545a365.json', scopes=SCOPES)
        gc = gspread.authorize(creds)
        sheet_url = 'https://docs.google.com/spreadsheets/d/1jiXbgYlPdI5FJQVMK4H66hJ8g3SMB9nNpfj_wVNgSJg/edit#gid=0'
        sheet = gc.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(1)

        # Convert data dictionary to a list
        row = [
            data.get('start_date_time', ''),
            data.get('end_date_time', ''),
            data.get('Prop_id', ''),
            data.get('Enumerator_name', ''),
            data.get('House1', ''),
            data.get('House2', ''),
            data.get('House3', ''),
            data.get('deviceName', '')
        ]
        # Append the row to the worksheet
        worksheet.append_row(row)
        print("Google Sheet updated successfully.")
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")


def save_dashboard_2_survey_data_on_sheets(data):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(
            '/home/ubuntu/apps/real_estate_property_tax_app/tax-app-420312-51aaf545a365.json', scopes=SCOPES)
        gc = gspread.authorize(creds)
        sheet_url = 'https://docs.google.com/spreadsheets/d/1jiXbgYlPdI5FJQVMK4H66hJ8g3SMB9nNpfj_wVNgSJg/edit#gid=0'
        sheet = gc.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(2)

        # Convert data dictionary to a list
        row = [
            data.get('start_date_time'),
            data.get('Enumerator_name'),
            data.get('prop_id'),
            data.get('type'),
            data.get('spending'),
            data.get('budget_support'),
            data.get('international_debt'),
            data.get('property_tax'),
            data.get('high_residential'),
            data.get('medium_residential'),
            data.get('high_commercial'),
            data.get('medium_commercial'),
            data.get('end_survey_time'),
            data.get('deviceName')
        ]

        # Append the row to the worksheet
        worksheet.append_row(row)
        print("Google Sheet updated successfully.")
    except Exception as e:
        print(f"Error updating Google Sheet: {e}")



# def save_to_csv_for_sheet3(data, filtered_data, enumerator_name):
#     directory = '/home/ubuntu/apps/real_estate_property_tax_app/backup_for_sheet3'
#     if not os.path.exists(directory):
#         os.makedirs(directory)
#     # Create DataFrame from filtered data
#     df = pd.DataFrame(data, columns=headers_for_sheet3)
#     filepath = os.path.join(directory, f'{filename}_{current_datetime}.csv')
#     df.to_csv(filepath, index=False)



# # Install the R package eg: 'dplyr'
# import rpy2.robjects.packages as rpackages

# utils = rpackages.importr('utils')
# utils.install_packages('dplyr')