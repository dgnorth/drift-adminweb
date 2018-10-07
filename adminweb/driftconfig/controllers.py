from flask import Blueprint, request, jsonify, \
                  flash, g, redirect, url_for, \
                  render_template, make_response, current_app
from driftconfig.util import get_default_drift_config_and_source
from flask_login import login_required
import logging
log = logging.getLogger(__name__)
bp = Blueprint('driftconfig', __name__, url_prefix='/driftconfig', template_folder="driftconfig")

ts, source = get_default_drift_config_and_source()


@bp.route('/')
@login_required
def index():
    return render_template('driftconfig/index.html')


@bp.route('/organizations')
@login_required
def organizations():
    return render_template('driftconfig/organizations.html',
                           organizations=ts.tables.get('organizations')._rows.values(),
                           ts=ts)


@bp.route('/organizations/<organization_name>')
@login_required
def organization(organization_name):
    tbl = ts.get_table('organizations')
    organization_row = tbl.find({"organization_name": organization_name})[0]
    products = ts.get_table('products').find({"organization_name": organization_name})

    return render_template('driftconfig/organization.html',
                           organization=organization_row,
                           products=products,
                           ts=ts)


@bp.route('/products')
@login_required
def products():
    return render_template('driftconfig/products.html',
                           products=ts.tables.get('products')._rows.values(),
                           ts=ts)


@bp.route('/organizations/<organization_name>/products/<product_name>')
@login_required
def product(organization_name, product_name):
    tbl = ts.get_table('products')
    product_row = tbl.find({"product_name": product_name, "organization_name": organization_name})[0]

    return render_template('driftconfig/product.html',
                           product=product_row,
                           ts=ts)


@bp.route('/tablestore')
@login_required
def tablestore():
    meta_by_table = {}
    for tbl in ts.meta['tables']:
        meta_by_table[tbl['table_name']] = tbl
    return render_template('driftconfig/tablestore.html',
                           tables=sorted(ts.tables.keys()),
                           ts=ts,
                           source=source,
                           meta=ts.meta,
                           meta_by_table=meta_by_table)
