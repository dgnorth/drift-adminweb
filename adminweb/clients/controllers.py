import collections

from flask import Blueprint, request, jsonify, \
                  flash, g, redirect, url_for, \
                  render_template, make_response, \
                  current_app

from flask_login import login_required
import logging

from drift.core.extensions.tenancy import tenant_from_hostname
from drift.utils import get_tier_name
from adminweb.utils import sqlalchemy_tenant_session, role_required, log_action
from adminweb.utils.country import get_cached_country
from adminweb.db.models import PlayerInfo
from adminweb.db.models import User as AdminUser
from driftbase.db.models import Client, User, UserRole, CorePlayer

log = logging.getLogger(__name__)
bp = Blueprint('clients', __name__, url_prefix='/clients', template_folder="clients")

@bp.route('/')
@login_required
def index():
    page_size = 25
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        query = session.query(Client).filter()
        if request.args.get('player_id'):
            query = query.filter(Client.player_id==int(request.args.get('player_id')))
        if request.args.get('user_id'):
            query = query.filter(Client.user_id==int(request.args.get('user_id')))
        if request.args.get('ip_address'):
            query = query.filter(Client.ip_address==request.args.get('ip_address'))
        order_by = request.args.get('order_by') or 'client_id'
        query = query.order_by(getattr(Client, order_by).desc())
        row_count = query.count()
        query = query.limit(page_size)
        query = query.offset(offset)
        num_pages = int(row_count/page_size)+1
        rows = query.all()
        for client in rows:
            client.country = get_cached_country(client.ip_address)

        return render_template('clients/index.html', clients=rows,
                        num_pages=num_pages,
                        curr_page=curr_page,
                        order_by=order_by)


@bp.route('/clients/<int:client_id>')
@login_required
def client(client_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        client = session.query(Client).get(client_id)
        client.country = get_cached_country(client.ip_address) or {}
        player = session.query(CorePlayer).get(client.player_id)

        return render_template('clients/client.html', client=client, player=player)
