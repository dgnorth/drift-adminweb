import controllers

def register_blueprints(app):
    app.register_blueprint(controllers.bp)
