from flask import Flask
from flask_cors import CORS
from loaders.blueprints import register_blueprints
from loaders.firebase_admin_init import initialize_firebase_admin

app = Flask(__name__)
CORS(app, resources={r'*': {'origins': '*'}})
# CORS(app, resources={r'*': {'origins': ['https://webisfree.com', 'http://localhost:3000']}})
initialize_firebase_admin()
register_blueprints(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
