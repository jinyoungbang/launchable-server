from flask import Blueprint, jsonify, request, make_response
from firebase_admin import firestore
from firebase_admin.firestore import SERVER_TIMESTAMP
from models.post import Post, Comment
from uuid import uuid4
import datetime
import logging

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
                    data["user"], data["user_id"], SERVER_TIMESTAMP,  SERVER_TIMESTAMP)
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


@posts.route("/api/posts/trending", methods=["GET"])
def get_trending_posts():
    try:
        logging.info("Fetching post scores.")
        docs = db.collection(u'posts_score').order_by(
            u"score", direction=firestore.Query.DESCENDING)
        docs = docs.stream()

        id_score_dict = {}
        scores_with_id = [doc.to_dict() for doc in docs]
        for score_doc in scores_with_id:
            id_score_dict[score_doc["id"]] = score_doc["score"]
        
        logging.info("Fetching posts and sorting by scores.")
        docs = db.collection(u'posts')
        docs = docs.stream()
        docs = [doc.to_dict() for doc in docs]
        for doc in docs:
            if doc["id"] not in id_score_dict:
                doc["score"] = 0
            else:
                doc["score"] = id_score_dict[doc["id"]]
        
        trending_posts = sorted(docs, key=lambda x : x["score"], reverse=True)
        for post in trending_posts:
            post.pop("score", None)

        res_obj = {
            "success": True,
            "data": trending_posts
        }
        return make_response(jsonify(res_obj), 200)

    except Exception as e:
        res_obj = {
            "success": False,
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)


@posts.route("/api/posts/recent", methods=["GET"])
def get_recent_posts():
    try:
        docs = db.collection(u'posts').order_by(
            u"created_at", direction=firestore.Query.DESCENDING)
        docs = docs.stream()
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


@posts.route("/api/posts/<id>", methods=["PATCH"])
def edit_specific_post(id):
    try:
        doc_ref = db.collection(u'posts').document(id)
        doc = doc_ref.get().to_dict()
        data = request.get_json()

        if doc["user_id"] != data["user_id"]:
            res_obj = {
                "msg": "Unauthorized."
            }
            return make_response(jsonify(res_obj), 401)

        doc_ref.update({
            "title": data["title"],
            "body": data["body"],
            "updated_at": SERVER_TIMESTAMP
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

    # Checking if post has been scored
    doc_ref = db.collection(u'posts_score').document(id)
    post_score_doc = doc_ref.get()

    score = post_doc_data["comments_count"] + likes_count * 5

    # If post hasn't been scored, score with current stats
    if not post_score_doc.exists:
        score_doc = {
            u"id": id,
            u"score": score,
            u"last_updated": SERVER_TIMESTAMP
        }
        db.collection(u'posts_score').document(id).set(score_doc)
    # Else, update score with new value
    else:
        doc_ref.update({
            u"score": score,
            u"last_updated": SERVER_TIMESTAMP
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

    # Checking if post has been scored
    doc_ref = db.collection(u'posts_score').document(id)
    post_score_doc = doc_ref.get()

    score = post_doc_data["comments_count"] + likes_count * 5

    # If post hasn't been scored, score with current stats
    if not post_score_doc.exists:
        score_doc = {
            u"id": id,
            u"score": score,
            u"last_updated": SERVER_TIMESTAMP
        }
        db.collection(u'posts_score').document(id).set(score_doc)
    # Else, update score with new value
    else:
        doc_ref.update({
            u"score": score,
            u"last_updated": SERVER_TIMESTAMP
        })

    res_obj = {
        "success": True,
        "postId": id,
        "likesCount": likes_count
    }
    return make_response(jsonify(res_obj), 201)


@posts.route("/api/posts/<id>/comments", methods=["POST"])
def create_comment(id):
    try:
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

        comment = Comment(
            str(uuid4()), data["body"], data["userId"], data["username"], 1, datetime.datetime.now(),  datetime.datetime.now())

        doc_ref.update({
            u"comments": firestore.ArrayUnion([vars(comment)]),
            u"comments_count": post_doc_data["comments_count"] + 1
        })

        # Checking if post has been scored
        doc_ref = db.collection(u'posts_score').document(id)
        post_score_doc = doc_ref.get()

        score = (post_doc_data["comments_count"] + 1) + (post_doc_data["likes_count"] * 5)

        # If post hasn't been scored, score with current stats
        if not post_score_doc.exists:
            score_doc = {
                u"id": id,
                u"score": score,
                u"last_updated": SERVER_TIMESTAMP
            }
            db.collection(u'posts_score').document(id).set(score_doc)
        # Else, update score with new value
        else:
            doc_ref.update({
                u"score": score,
                u"last_updated": SERVER_TIMESTAMP
            })

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


@posts.route("/api/posts/<post_id>/comments/<comment_id>", methods=["PATCH"])
def update_comment(post_id, comment_id):
    try:
        doc_ref = db.collection(u'posts').document(post_id)
        post_doc = doc_ref.get()
        if not post_doc.exists:
            res_obj = {
                "success": False,
                "msg": "Post not found."
            }
            return make_response(jsonify(res_obj), 404)

        data = request.get_json()

        post_doc_data = post_doc.to_dict()
        comments = post_doc_data["comments"]
        for i in range(len(comments)):
            if comments[i]["id"] == comment_id:
                comments[i]["body"] = data["body"]
                comments[i]["updated_at"] = datetime.datetime.now()
                break

        doc_ref.update({
            u"comments": comments,
        })

        res_obj = {
            "success": True
        }
        return make_response(jsonify(res_obj), 200)

    except Exception as e:
        res_obj = {
            "success": False,
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)


@posts.route("/api/posts/<post_id>/comments/<comment_id>", methods=["DELETE"])
def delete_comment(post_id, comment_id):
    try:
        doc_ref = db.collection(u'posts').document(post_id)
        post_doc = doc_ref.get()
        if not post_doc.exists:
            res_obj = {
                "success": False,
                "msg": "Post not found."
            }
            return make_response(jsonify(res_obj), 404)

        post_doc_data = post_doc.to_dict()
        comments = [comment for comment in post_doc_data["comments"]
                    if not (comment['id'] == comment_id)]

        doc_ref.update({
            u"comments": comments,
            u"comments_count": len(comments)
        })

        # Checking if post has been scored
        doc_ref = db.collection(u'posts_score').document(post_id)
        post_score_doc = doc_ref.get()
        score = len(comments) + (post_doc_data["likes_count"] * 5)

        # If post hasn't been scored, score with current stats
        if not post_score_doc.exists:
            score_doc = {
                u"id": id,
                u"score": score,
                u"last_updated": SERVER_TIMESTAMP
            }
            db.collection(u'posts_score').document(id).set(score_doc)
        # Else, update score with new value
        else:
            doc_ref.update({
                u"score": score,
                u"last_updated": SERVER_TIMESTAMP
            })

        res_obj = {
            "success": True
        }
        return make_response(jsonify(res_obj), 200)

    except Exception as e:
        res_obj = {
            "success": False,
            "msg": e
        }
        return make_response(jsonify(res_obj), 400)
