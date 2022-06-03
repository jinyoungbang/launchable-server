from firebase_admin import auth

def delete_user_from_auth_module(id):
    auth.delete_user(id)