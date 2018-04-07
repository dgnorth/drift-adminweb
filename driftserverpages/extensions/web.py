import datetime, socket
from os.path import join, abspath
import sys
import json
import pkg_resources

from flask import g, render_template, current_app
from flask_login import LoginManager, current_user
from flask_cors import CORS
from flask_gravatar import Gravatar

from driftserverpages.utils import InvalidUsage
from driftserverpages.db.models import User
import logging
import traceback

from driftserverpages.utils import filters

log = logging.getLogger(__name__)

def register_extension(app):
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(e):
        return render_template('usererror.html',
                               message=e.message,
                               status_code=e.status_code
                               ), e.status_code

    @app.errorhandler(Exception)
    def handle_exception(e):
        if current_app.config.get("show_exceptions"):
            log.exception("Unhandled exception!")
            ex_type, ex, tb = sys.exc_info()
            tb = "\n".join(traceback.format_tb(tb))
            return render_template('runtimeerror.html',
                                   message=repr(e),
                                   traceback=tb,
                                   status_code=500
                                   ), 500
        else:
            raise
    cors = CORS(app)

    app.instance_path = pkg_resources.resource_filename('driftserverpages', '')
    app.static_folder = pkg_resources.resource_filename('driftserverpages', 'static')
    app.template_folder = pkg_resources.resource_filename('driftserverpages', 'templates')

    print "app.static_folder ", app.static_folder 
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    @login_manager.user_loader
    def load_user(id):
        return g.db.query(User).get(int(id))

    @app.before_request
    def before_request():
        g.user = current_user

    app.register_blueprint(filters.blueprint)

    # with open("VERSION") as f:
    #     version = f.read().strip()
    #     app.jinja_env.globals['VERSION'] = version
    version = '0.2.0'
    app.jinja_env.globals['VERSION'] = version

    dt = "unknown"
    try:
        with open("deployment_info.json", "rb") as f:
            js = json.load(f)
            dt = datetime.datetime.strptime(js["datetime"], '%Y-%m-%dT%H:%M:%S.%f')
            dt = dt.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        pass
    app.jinja_env.globals['BUILD_DATE'] = dt
    app.jinja_env.globals['HOST_NAME'] = socket.gethostname()
    app.jinja_env.globals['HOST_ADDRESS'] = socket.gethostbyname(socket.gethostname())

    gravatar = Gravatar(app,
                        size=32,
                        rating='g',
                        default='retro',
                        force_default=False,
                        force_lower=False,
                        use_ssl=True,
                        base_url=None)
