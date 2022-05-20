from flask import Blueprint, jsonify, request, make_response
from firebase_admin import firestore
from firebase_admin.firestore import SERVER_TIMESTAMP
from models.post import Post

posts = Blueprint("posts", __name__)  # initialize blueprint
db = firestore.client()


@posts.route("/api/posts", methods=["POST"])
def create_post():
    try:
        posts_ref = db.collection(u'posts')
        post_doc = posts_ref.document()
        post_id = post_doc.id

        data = request.get_json()
        post = Post(post_id, data["title"], data["body"],
                    data["user"], SERVER_TIMESTAMP,  SERVER_TIMESTAMP)
        post_doc.set(vars(post))
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


@posts.route("/api/posts", methods=["GET"])
def get_posts():
    pass


@posts.route("/api/posts/<id>", methods=["GET"])
def get_specific_post(id):
    try:
        doc_ref = db.collection(u'posts').document(id)
        post_doc = doc_ref.get()

        if post_doc.exists:
            res_obj = {
                "success": True,
                "data": post_doc.to_dict()
            }
            return make_response(jsonify(res_obj), 200)
        else:
            res_obj = {
                "success": False,
                "msg": "Post not found."
            }
        return make_response(jsonify(res_obj), 404)

    except Exception as e:
        res_obj = {
            "success": False,
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)


@posts.route("/api/posts/<id>", methods=["DELETE"])
def delete_specific_post(id):
    doc_ref = db.collection(u'posts').document(id)
    post_doc = doc_ref.get()
    if post_doc.exists:
        doc_ref.delete()
        res_obj = {
            "success": True,
        }
        return make_response(jsonify(res_obj), 200)
    else:
        res_obj = {
            "success": False,
            "msg": "Post not found."
        }
    return make_response(jsonify(res_obj), 404)
