def register_blueprints(app):
    """ Helper function to register blueprints into Flask App """
    from api.general import general
    from api.auth import auth
    from api.settings import settings
    from api.posts import posts

    print("Registering Flask Blueprints.")
    app.register_blueprint(general)
    app.register_blueprint(auth)
    app.register_blueprint(settings)
    app.register_blueprint(posts)

    return app