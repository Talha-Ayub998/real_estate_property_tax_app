from rpy2.robjects import pandas2ri
import rpy2.robjects as robjects
from r_code.r_code import r_code
import pandas as pd
robjects.r('library(dplyr)')
robjects.r('library(restriktor)')
robjects.r('library(tidyr)')
pandas2ri.activate()


def read_csv(file_path):
    return pd.read_csv(file_path)

def convert_to_r_dataframe(data_frame):
    return pandas2ri.py2rpy(data_frame)

def run_r_analysis(merged_data, v_values):
    robjects.r(r_code)
    r_function = robjects.globalenv['perform_analysis']
    result = r_function(merged_data, v_values)
    return result

def convert_to_pandas_dataframe(result):
    total_revenue = result
    return pd.DataFrame(total_revenue)

def perform_analysis_with_r_integration(data):
    merged_data = read_csv("test_data2.csv")
    v_values = read_csv("v_values.csv")
    pandas2ri.deactivate()
    pandas2ri.activate()

    merged_data_r = convert_to_r_dataframe(merged_data)
    v_values_r = convert_to_r_dataframe(v_values)
    result = run_r_analysis(merged_data_r, v_values_r)

    return convert_to_pandas_dataframe(result)