from constraint_spline import perform_analysis_with_r_integration, save_to_csv
from rpy2.rinterface_lib.embedded import RRuntimeError
from flask import request, jsonify
from app import app

# Define the headers you want to keep
desired_headers = ['start_time', 'prop_id', 'enumerator_name', 'number_of_property',
                   'prop_val', 'preferred_tax_liability', 'atr', 'tax_liability_current',
                   'atr_current', 'end_time', 'deviceName']

@app.route('/')
def hello_world():
    return jsonify({'success': True,}) 

@app.route('/analysis', methods=['POST'])
def perform_analysis():
    try:
        # Retrieve data from the request
        data = request.json
        try:
        # Perform analysis with R integration
            total_revenue = perform_analysis_with_r_integration(data)
            filtered_data = [{key: entry[key] for key in desired_headers if key in entry} for entry in data]
            # Get the value of 'enumerator_name' from the first entry
            enumerator_name = filtered_data[0].get('enumerator_name', 'unknown')
            # Save desired data to CSV with enumerator_name as the filename
            save_to_csv(filtered_data, enumerator_name, total_revenue)
        except RRuntimeError:
            return jsonify({
                'success': False,
                'message': f"Invalid-data",
                'total_revenue': 0
            }), 400

        return jsonify({
            'success': True,
            "total_revenue": total_revenue
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
