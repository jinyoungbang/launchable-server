from flask import Flask
from flask_cors import CORS
from loaders.blueprints import register_blueprints
from loaders.firebase_admin_init import initialize_firebase_admin
import os
from dotenv import load_dotenv

load_dotenv()

env = os.environ.get('FLASK_ENV'),
app = Flask(__name__)

if env == "production":
    CORS(app, resources={r'*': {'origins': [
        "http://launchable.kr/",
        "https://launchable.kr/",
        "http://launchable.kr/*",
        "https://launchable.kr/*"
        "http://www.launchable.kr",
        "https://www.launchable.kr/",
        "https://launchable-plhl6vj4k-jinyoung-bang.vercel.app/"
    ]}})
elif env == "development":
    CORS(app, resources={r'*': {'origins': '*'}})
else:
    CORS(app, resources={r'*': {'origins': '*'}})

initialize_firebase_admin()
register_blueprints(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
