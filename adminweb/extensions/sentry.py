from raven.contrib.flask import Sentry

def register_extension(app):
    print 'Registering sentry'
    app.sentry = Sentry(app)
