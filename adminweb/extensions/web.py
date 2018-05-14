import datetime
import socket
from os.path import abspath
import json
import pkg_resources

from flask import g, render_template
from flask_login import LoginManager, current_user
from flask_cors import CORS
from flask_gravatar import Gravatar

from werkzeug.exceptions import HTTPException

from adminweb.utils import InvalidUsage
from adminweb.db.models import User
import logging

from adminweb.utils import filters

log = logging.getLogger(__name__)


def register_extension(app):
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(e):
        return render_template('usererror.html',
                               message=e.message,
                               status_code=e.status_code
                               ), e.status_code

    CORS(app)

    app.instance_path = abspath(pkg_resources.resource_filename('adminweb', ''))
    app.static_folder = abspath(pkg_resources.resource_filename('adminweb', 'static'))
    app.template_folder = abspath(pkg_resources.resource_filename('adminweb', 'templates'))
    log.info("Init app.instance_path: %s", app.instance_path)
    log.info("Init app.static_folder: %s", app.static_folder)
    log.info("Init app.template_folder: %s", app.template_folder)

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
