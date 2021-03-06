from flask import Blueprint, request, jsonify, \
                  flash, g, redirect, url_for, \
                  render_template, make_response

from flask_login import login_required
import logging

from drift.utils import request_wants_json
from drift.core.extensions.tenancy import tenant_from_hostname
from drift.utils import get_tier_name

from adminweb.utils import sqlalchemy_tenant_session

log = logging.getLogger(__name__)
bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder="admin")


def drift_init_extension(app, api, **kwargs):
    app.register_blueprint(bp)


@bp.route('/')
@login_required
def index():
    return render_template('admin/index.html')
