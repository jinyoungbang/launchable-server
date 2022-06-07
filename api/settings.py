import profile
from flask import Blueprint, jsonify, request, make_response
from firebase_admin import firestore, storage, exceptions
from firebase_admin.firestore import SERVER_TIMESTAMP

settings = Blueprint("settings", __name__)  # initialize blueprint
db = firestore.client()
# bucket = storage.bucket()


@settings.route("/api/settings", methods=["PATCH"])
# Function to edit username on Settings page
def edit_user_profile():
    try:
        data = request.get_json()
        users_ref = db.collection(u'users')

        user_id = data["id"]
        profile_data = data["userData"]["profile"]

        # # Ensures that inner object values do not get wiped
        profile_data["updated_at"] = SERVER_TIMESTAMP
        profile_data["id"] = user_id

        if "display_name" not in profile_data:
            profile_data["display_name"] = ""

        if "about" not in profile_data:
            profile_data["about"] = ""

        users_ref.document(user_id).update({
            "profile.about": profile_data["about"],
            "profile.display_name": profile_data["display_name"],
            "profile.profile_links": profile_data["profile_links"]
        })
        res_obj = {
            "msg": "Success",
        }
        return make_response(jsonify(res_obj), 200)

    except:
        res_obj = {
            "msg": "Error. Please check Firebase console."
        }
        return make_response(jsonify(res_obj), 400)


@settings.route("/api/settings/avatar", methods=["PATCH"])
def edit_avatar_url():
    try:
        data = request.get_json()
        users_ref = db.collection(u'users')
        user_id = data["id"]

        users_ref.document(user_id).update({
            "profile.avatar_url": data["avatar_url"]
        })
        res_obj = {
            "msg": "Success",
        }
        return make_response(jsonify(res_obj), 200)

    except:
        res_obj = {
            "msg": "Error. Please check Firebase console."
        }
        return make_response(jsonify(res_obj), 400)
