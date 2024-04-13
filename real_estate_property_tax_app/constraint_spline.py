from rpy2.robjects import pandas2ri
import rpy2.robjects as robjects
from r_code.r_code import r_code
import pandas as pd
import json, os
from datetime import datetime
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

def perform_analysis_with_r_integration(data):
    # current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # json_filename = os.path.join(directory, f"{current_datetime}.json")
    # with open(json_filename, 'w') as json_file:
    #     json.dump(data, json_file, indent=2)
    merged_data = pd.DataFrame(data)
    v_values = pd.read_csv("v_values_v3.csv")
    pandas2ri.deactivate()
    pandas2ri.activate()

    merged_data_r = convert_to_r_dataframe(merged_data)
    v_values_r = convert_to_r_dataframe(v_values)
    result = run_r_analysis(merged_data_r, v_values_r)

    return convert_to_pandas_dataframe(result)


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

# # Install the R package eg: 'dplyr'
# import rpy2.robjects.packages as rpackages

# utils = rpackages.importr('utils')
# utils.install_packages('dplyr')