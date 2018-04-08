from flask import Blueprint, request, jsonify, \
                  flash, g, redirect, url_for, \
                  render_template, make_response, current_app

from flask_login import login_required
import logging

from drift.utils import request_wants_json
from drift.utils import get_tier_name
from driftconfig.util import get_default_drift_config
from drift.core.extensions.tenancy import tenant_from_hostname
from drift.core.resources.postgres import format_connection_string
from drift.orm import get_sqlalchemy_session
from adminweb.utils.metrics import get_metrics_session

from adminweb.utils import sqlalchemy_tenant_session
from adminweb.utils.metrics import metrics_agent

log = logging.getLogger(__name__)
bp = Blueprint('metrics', __name__, url_prefix='/metrics', template_folder="metrics")


@bp.route('/')
@login_required
def index():
    with metrics_agent() as metrics:
        counter_id = int(request.args.get('counter_id') or 0)
        num_days = int(request.args.get('num_days') or 0)

        series = None
        if counter_id:
            counter = metrics.counters[counter_id]
            period = counter.period
            if not num_days:
                num_days = 2
                if 'day' in period:
                    num_days = 60
            series = metrics.get_counter_data(counter_id, num_days)

        counters = [v for k, v in metrics.counters.items() if isinstance(k, int)]
        return render_template('metrics/index.html',
                               counters=counters,
                               series=[series])
