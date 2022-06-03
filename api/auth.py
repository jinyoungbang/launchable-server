from flask import Blueprint, jsonify, request, make_response
from firebase_admin import firestore
from firebase_admin.firestore import SERVER_TIMESTAMP
from models.user import User
from service.common import return_exception
import json

from service.auth import delete_user_from_auth_module

auth = Blueprint("auth", __name__)  # initialize blueprint
db = firestore.client()


@auth.route("/api/auth", methods=["POST"])
# Checks if a user's UID exists in Firestore
def check_uid():
    try:
        data = request.get_json()
        users_ref = db.collection(u'users')
        doc = users_ref.document(data["id"]).get()
        if doc.exists:
            res_obj = {
                "userExists": True,
                "userData": doc.to_dict()
            }
            return make_response(jsonify(res_obj), 200)
        else:
            res_obj = {
                "userExists": False
            }
            return make_response(jsonify(res_obj), 200)

    except Exception as e:
        res_obj = {
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)


@auth.route("/api/auth/check-username", methods=["POST"])
# Checks if a user's UID exists in Firestore
def check_username():
    try:
        data = request.get_json()
        users_ref = db.collection(u'users')
        doc = users_ref.where(u"username", u"==", data["username"]).get()
        print(doc)
        if len(doc) != 0:
            res_obj = {
                "usernameExists": True,
            }
            return make_response(jsonify(res_obj), 200)
        else:
            res_obj = {
                "usernameExists": False
            }
            return make_response(jsonify(res_obj), 200)

    except Exception as e:
        res_obj = {
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)


@auth.route("/api/auth/create", methods=["POST"])
def create_user():
    try:
        users_ref = db.collection(u'users')
        data = request.get_json()
        user = User(data["id"], data["username"], data["email"],
                    SERVER_TIMESTAMP,  SERVER_TIMESTAMP, True)

        users_ref.document(data["id"]).set(vars(user))
        res_obj = {
            "success": True
        }
        return make_response(jsonify(res_obj), 201)

    except Exception as e:
        res_obj = {
            "success": False,
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)


@auth.route("/api/auth/<id>", methods=["GET"])
def check_user_exists(id):
    try:
        users_ref = db.collection(u'users')
        doc = users_ref.document(id).get()
        if doc.exists:
            res_obj = {
                "userExists": True,
            }
            return make_response(jsonify(res_obj), 200)
        else:
            res_obj = {
                "userExists": False
            }
            return make_response(jsonify(res_obj), 200)

    except Exception as e:
        res_obj = {
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)


@auth.route("/api/auth/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        doc_ref = db.collection(u'users').document(id)
        post_doc = doc_ref.get()

        if post_doc.exists:
            print("users doc found")
            doc_ref.delete()
            delete_user_from_auth_module(id)
            print("deleted with auth")

        else:
            res_obj = {
                "success": False,
                "msg": "User not found."
            }

            return make_response(jsonify(res_obj), 404)

        collection_ref = db.collection(u"posts")
        docs = collection_ref.where(u"user_id", "==", id).get()
        batch = db.batch()

        print("creating batch")
        num = 0

        for doc in docs:
            if num % 500 == 499:
                batch.commit()
                batch = db.batch()
                num = 0
            batch.delete(doc.reference)
            num += 1
            print("deleting " + str(num))

        batch.commit()

        res_obj = {
            "success": True,
        }
        return make_response(jsonify(res_obj), 200)

    except Exception as e:
        res_obj = {
            "success": False,
        }
        return make_response(jsonify(res_obj), 404)
