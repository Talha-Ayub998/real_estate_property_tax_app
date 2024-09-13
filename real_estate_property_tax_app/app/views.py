from constraint_spline import perform_analysis_with_r_integration, save_to_csv, save_dashboard_1_data_on_sheets
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
            data = [{**item, "atr": 0.00000001 if item["atr"] == 0.000001 else (0 if item["atr"] == 0.00000001 else item["atr"])} for item in data]
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


@app.route('/save_dashboard_1.1', methods=['POST'])
def save_dashboard_1():
    try:
        # Retrieve data from the request
        data = request.json
        save_dashboard_1_data_on_sheets(data)
        return jsonify({
            'success': True,
        }), 200
    except (ConnectionError, Timeout) as e:
        return jsonify({'success': False, 'message': "Server is down or request timed out"}), 503
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500




# from constraint_spline import perform_analysis_with_r_integration, save_to_csv, save_to_csv_for_sheet3


# headers_for_sheet3 = ["start_date_time", "Enumerator_name", "prop_id", "type", "spending",
#                     "budget_support", "international_debt", "property_tax", "high_residential",
#                     "medium_residential", "high_commercial", "medium_commercial", "end_survey_time",
#                     "deviceName",]


# @app.route('/save_survey', methods=['POST'])
# def perform_analysis():
#     try:
#         # Retrieve data from the request
#         data = request.json
#         try:
#             filtered_data = [{key: entry[key] for key in headers_for_sheet3 if key in entry} for entry in data]
#             # Get the value of 'enumerator_name' from the first entry
#             enumerator_name = filtered_data[0].get('Enumerator_name', 'unknown')
#             save_to_csv_for_sheet3(data, filtered_data, enumerator_name)
#         except RRuntimeError:
#             return jsonify({
#                 'success': False,
#             }), 400

#         return jsonify({
#             'success': True
#         }), 200
#     except (ConnectionError, Timeout) as e:
#         return jsonify({'success': False, 'message': "Server is down or request timed out"}), 503
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}), 500

