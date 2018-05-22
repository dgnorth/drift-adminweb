from flask import Blueprint, request, jsonify, \
                  flash, g, redirect, url_for, \
                  render_template, make_response, current_app
from driftconfig.util import get_default_drift_config_and_source
from flask_login import login_required
import logging
log = logging.getLogger(__name__)
bp = Blueprint('driftconfig', __name__, url_prefix='/driftconfig', template_folder="driftconfig")


@bp.route('/')
@login_required
def index():
    ts, source = get_default_drift_config_and_source()
    meta_by_table = {}
    for tbl in ts.meta['tables']:
        meta_by_table[tbl['table_name']] = tbl
    return render_template('driftconfig/index.html',
                           tables=sorted(ts.tables.keys()),
                           ts=ts, 
                           source=source,
                           meta=ts.meta,
                           meta_by_table=meta_by_table)
