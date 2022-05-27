from flask import Blueprint, jsonify, request, make_response
from firebase_admin import firestore
from firebase_admin.firestore import SERVER_TIMESTAMP
from models.post import Post, Like

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
    try:
        docs = db.collection(u'posts').stream()

        docs_to_send = [doc.to_dict() for doc in docs]

        res_obj = {
            "success": True,
            "data": docs_to_send
        }
        return make_response(jsonify(res_obj), 200)

    except Exception as e:
        res_obj = {
            "success": False,
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)


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


@posts.route("/api/posts/like/<id>", methods=["POST"])
def like_post(id):

    # Find post and check if post exists
    doc_ref = db.collection(u'posts').document(id)
    post_doc = doc_ref.get()
    if not post_doc.exists:
        res_obj = {
            "success": False,
            "msg": "Post not found."
        }
        return make_response(jsonify(res_obj), 404)

    post_doc_data = post_doc.to_dict()
    data = request.get_json()
    user_id = data["userId"]

    if not user_id or user_id == "":
        res_obj = {
            "success": False,
            "msg": "Error, please try again."
        }
        return make_response(jsonify(res_obj), 404)

    if user_id in post_doc_data["likes"]:
        res_obj = {
            "success": False,
            "msg": "Post already liked."
        }
        return make_response(jsonify(res_obj), 404)

    likes_count = len(post_doc_data["likes"]) + 1
    doc_ref.update({
        u"likes": post_doc_data["likes"] + [user_id],
        u"likes_count": likes_count
    })

    res_obj = {
        "success": True,
        "postId": id,
        "likesCount": likes_count
    }
    return make_response(jsonify(res_obj), 201)


@posts.route("/api/posts/unlike/<id>", methods=["POST"])
def unlike_post(id):
    doc_ref = db.collection(u'posts').document(id)
    post_doc = doc_ref.get()
    if not post_doc.exists:
        res_obj = {
            "success": False,
            "msg": "Post not found."
        }
        return make_response(jsonify(res_obj), 404)

    post_doc_data = post_doc.to_dict()
    data = request.get_json()
    user_id = data["userId"]

    if not user_id or user_id == "":
        res_obj = {
            "success": False,
            "msg": "Error, please try again."
        }
        return make_response(jsonify(res_obj), 404)

    if user_id not in post_doc_data["likes"]:
        res_obj = {
            "success": False,
            "msg": "Post not liked, cannot unlike."
        }
        return make_response(jsonify(res_obj), 404)

    if len(post_doc_data["likes"]) == 0:
        res_obj = {
            "success": False,
            "msg": "No likes for given post,cannot unlike."
        }
        return make_response(jsonify(res_obj), 404)

    likes_count = len(post_doc_data["likes"]) - 1
    likes_list = post_doc_data["likes"][:]
    likes_list.remove(user_id)

    doc_ref.update({
        u"likes": likes_list,
        u"likes_count": likes_count
    })

    res_obj = {
        "success": True,
        "postId": id,
        "likesCount": likes_count
    }
    return make_response(jsonify(res_obj), 201)
