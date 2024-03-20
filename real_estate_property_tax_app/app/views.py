from constraint_spline import perform_analysis_with_r_integration
from rpy2.rinterface_lib.embedded import RRuntimeError
from flask import request, jsonify
from app import app

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
