
from flask import jsonify, make_response

def return_exception(msg):
    res_obj = {
        "status": False,
        "msg": msg
    }
    return make_response(jsonify(res_obj), 400)
