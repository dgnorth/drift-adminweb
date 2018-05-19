
from flask import Blueprint, request, jsonify, \
                  flash, g, redirect, url_for, \
                  render_template, make_response, \
                  current_app

from flask_login import login_required
import logging

from drift.utils import request_wants_json
from drift.core.extensions.tenancy import tenant_from_hostname
from drift.utils import get_tier_name
from adminweb.utils import sqlalchemy_tenant_session, role_required, log_action
from adminweb.utils.country import get_cached_country
from driftbase.db.models import Client, User, UserRole, User, UserEvent
from driftbase.players import log_event

log = logging.getLogger(__name__)
bp = Blueprint('users', __name__, url_prefix='/users', template_folder="users")

MAX_MISSIONS = 3

@bp.route('/')
@login_required
def index():
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    with sqlalchemy_tenant_session(tenant_from_hostname, get_tier_name(), 'drift-base') as session:
        query = session.query(User)
        if request.args.get('user_id'):
            query = query.filter(User.user_id==int(request.args.get('user_id')))
        elif request.args.get('user_name'):
            query = query.filter(User.user_name.ilike('%{}%'.format(request.args.get('user_name'))))
        order_by = request.args.get('order_by') or 'logon_date'
        query = query.order_by(getattr(User, order_by).desc())
        row_count = query.count()
        query = query.limit(page_size)
        query = query.offset(offset)
        users = query
        num_pages = int(row_count/page_size)+1

        if row_count == 1:
            return redirect(url_for('users.user', user_id=users[0].user_id))
        else:
            return render_template('users/index.html', users=users,
                        num_pages=num_pages,
                        curr_page=curr_page,
                        order_by=order_by)


@bp.route('/users/<int:user_id>')
@login_required
def user(user_id):
    with sqlalchemy_tenant_session(tenant_from_hostname, get_tier_name(), 'drift-base') as session:
        user = session.query(User).get(user_id)

    return render_template('users/user.html',
                           user=user)


@bp.route('/users/<int:user_id>/editname', methods=['GET', 'POST'])
@login_required
@role_required('cs')
def edit_user_name(user_id):
    with sqlalchemy_tenant_session(tenant_from_hostname, get_tier_name(), 'drift-base') as session:
        user = session.query(User).get(user_id)
        if request.method == 'POST':
            old_user_name = user.user_name
            user.user_name = request.form['val']
            log_event(user_id, 
                      'event.admin.change_user_name',
                      details={'admin': g.user.username, 'old': old_user_name, 'new': user.user_name},
                      db_session=session)
            log_action('user.change_user_name', ref=('user', user_id))
            flash("User name has been changed from %s to %s" % (old_user_name, user.user_name))

            return redirect(url_for('users.user', user_id=user_id))

        else:
            return render_template('users/editfield.html', user=user, which='user name', val=user.user_name)


@bp.route('/users/<int:user_id>/clients')
@login_required
def clients(user_id):
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    with sqlalchemy_tenant_session(tenant_from_hostname, get_tier_name(), 'drift-base') as session:
        user = session.query(User).get(user_id)
        query = session.query(Client).filter(Client.user_id==user_id)
        query = query.order_by(Client.client_id.desc())
        row_count = query.count()
        query = query.limit(page_size)
        query = query.offset(offset)
        rows = query.all()
        num_pages = int(row_count/page_size)+1
        for client in rows:
            client.country = get_cached_country(client.ip_address)

        return render_template('users/user_clients.html', user=user, clients=query, num_pages=num_pages, curr_page=curr_page)
