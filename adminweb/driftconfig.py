from flask import Blueprint, request, jsonify, \
                  flash, g, redirect, url_for, \
                  render_template, make_response, current_app
from driftconfig.util import get_default_drift_config_and_source
from flask_login import login_required
import logging
import operator
log = logging.getLogger(__name__)
bp = Blueprint('driftconfig', __name__, url_prefix='/driftconfig', template_folder="driftconfig")


def drift_init_extension(app, api, **kwargs):
    app.register_blueprint(bp)


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


@bp.route('/tenants')
@login_required
def tenants():
    return render_template('driftconfig/tenants.html',
                           tenants=ts.tables.get('tenant-names')._rows.values(),
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
    deployables = []
    for deployable_name in product_row['deployables']:
        tbl = ts.get_table('deployables')
        row = tbl.find({"deployable_name": deployable_name})[0]
        deployables.append(row)
    tbl = ts.get_table('tenant-names')
    tenant_names = tbl.find({"product_name": product_name})

    tbl = ts.get_table('api-keys')
    api_keys = tbl.find({"product_name": product_name})

    tbl = ts.get_table('api-key-rules')
    api_key_rules = tbl.find({"product_name": product_name})
    api_key_rules.sort(key=operator.itemgetter('assignment_order'))
    return render_template('driftconfig/product.html',
                           product=product_row,
                           deployables=deployables,
                           tenant_names=tenant_names,
                           api_keys=api_keys,
                           api_key_rules=api_key_rules,
                           ts=ts)


@bp.route('/tenants/<tenant_name>')
@login_required
def tenant(tenant_name):
    tbl = ts.get_table('tenant-names')
    tenant_name_row = tbl.find({"tenant_name": tenant_name})[0]
    tbl = ts.get_table('tenants')
    tenant_deployables = tbl.find({"tenant_name": tenant_name})
    return render_template('driftconfig/tenant.html',
                           tenant_name=tenant_name_row,
                           tenant_deployables=tenant_deployables,
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
