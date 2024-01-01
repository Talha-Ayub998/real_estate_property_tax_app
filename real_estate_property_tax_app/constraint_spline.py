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
    directory = './Array_for_R_code'
    if not os.path.exists(directory):
        os.makedirs(directory)
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_filename = os.path.join(directory, f"{current_datetime}.json")
    with open(json_filename, 'w') as json_file:
        json.dump(data, json_file, indent=2)
    merged_data = pd.DataFrame(data)
    v_values = pd.read_csv("v_values.csv")
    pandas2ri.deactivate()
    pandas2ri.activate()

    merged_data_r = convert_to_r_dataframe(merged_data)
    v_values_r = convert_to_r_dataframe(v_values)
    result = run_r_analysis(merged_data_r, v_values_r)

    return convert_to_pandas_dataframe(result)


# # Install the R package eg: 'dplyr'
# import rpy2.robjects.packages as rpackages

# utils = rpackages.importr('utils')
# utils.install_packages('dplyr')