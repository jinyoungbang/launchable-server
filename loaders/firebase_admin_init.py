import firebase_admin
from firebase_admin import credentials

def initialize_firebase_admin():
    cred = credentials.Certificate("./config/firebase_admin_key.json")
    firebase_admin.initialize_app(cred)