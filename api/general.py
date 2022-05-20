from flask import Blueprint

general = Blueprint("general", __name__)  # initialize blueprint


# function that is called when you visit /
@general.route("/")
def index():
    return "Hit"


@general.route("/api/ping")
def ping():
    return "Success."

@general.route("/api/test")
def deploy_check():
    return "deployment script worked."

