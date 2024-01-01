from app import app
from flask_cors import CORS

# Enable CORS for all routes
CORS(app)

if __name__ == '__main__':
    # Run the app using Gunicorn
    app.run(host='0.0.0.0', port=5000)
