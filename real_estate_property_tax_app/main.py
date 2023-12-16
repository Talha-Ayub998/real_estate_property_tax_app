from app import app
from flask_cors import CORS

if __name__ == '__main__':
    CORS(app, resources={r"/": {"origins": ""}}, supports_credentials=True,
        methods=["GET", "HEAD", "POST", "PATCH", "PUT", "DELETE"])
    app.run(debug=True)
