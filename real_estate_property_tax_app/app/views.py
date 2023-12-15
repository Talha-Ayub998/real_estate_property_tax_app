from flask import request, jsonify
from constraint_spline import perform_analysis_with_r_integration
from app import app
import pandas as pd
import rpy2.robjects as robjects
robjects.r('library(dplyr)')
robjects.r('library(restriktor)')
robjects.r('library(tidyr)')

@app.route('/')
def hello_world():
    return jsonify({'success': True,}) 

@app.route('/analysis', methods=['POST'])
def perform_analysis():
    try:
        # Retrieve data from the request
        # data = request.json.get("data")

        # Perform analysis with R integration
        plot_data, total_revenue, revenues_long = perform_analysis_with_r_integration(None)
        plot_data = plot_data.to_dict(orient='split')
        total_revenue = total_revenue.to_dict(orient='split')
        revenues_long = revenues_long.to_dict(orient='split')
        return jsonify({
            'success': True,
            'data': [
                {"plot_data": plot_data,
                 "total_revenue": total_revenue,
                 "revenues_long": revenues_long}]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
