from constraint_spline import perform_analysis_with_r_integration
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

        # Perform analysis with R integration
        total_revenue = perform_analysis_with_r_integration(data)
        total_revenue = total_revenue.to_dict(orient='records')
        return jsonify({
            'success': True,
            'data': [
                {"total_revenue": total_revenue}]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
