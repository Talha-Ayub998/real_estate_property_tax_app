from constraint_spline import perform_analysis_with_r_integration, save_to_csv
from requests.exceptions import ConnectionError, Timeout
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
            # Just to change the atr values for now
            data = [{**item, "atr": 0.000001 if item["atr"] == 0 else (0 if item["atr"] == 0.00000001 else item["atr"])} for item in data]
            # Perform analysis with R integration
            filtered_data = [{key: entry[key] for key in desired_headers if key in entry} for entry in data]
            enumerator_name = filtered_data[0].get('enumerator_name', 'unknown')
            total_revenue = perform_analysis_with_r_integration(data, enumerator_name)
            # Get the value of 'enumerator_name' from the first entry
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
    except (ConnectionError, Timeout) as e:
        return jsonify({'success': False, 'message': "Server is down or request timed out"}), 503
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
