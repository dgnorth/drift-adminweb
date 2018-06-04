from flask import Blueprint, request, flash, g, redirect, url_for, render_template
from flask_login import login_required

from drift.utils import request_wants_json
from drift.core.extensions.tenancy import tenant_from_hostname
from drift.utils import get_tier_name
from adminweb.utils import sqlalchemy_tenant_session, role_required, log_action
from adminweb.utils.country import get_cached_country
from driftbase.db.models import Client, User, UserRole, UserEvent, UserIdentity, CorePlayer
from driftbase.players import log_event


bp = Blueprint('users', __name__, url_prefix='/users', template_folder="users")


@bp.route('/')
@login_required
def index():
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
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

        return render_template('users/index.html', users=users,
                               num_pages=num_pages,
                               curr_page=curr_page,
                               order_by=order_by)


@bp.route('/users/<int:user_id>')
@login_required
def user(user_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        user = session.query(User).get(user_id)
        player = session.query(CorePlayer).get(user.default_player_id)
        identities = session.query(UserIdentity).filter(UserIdentity.user_id==user_id).all()
        return render_template('users/user.html', page='INFO',
                               user=user, player=player, identities=identities)


@bp.route('/users/<int:user_id>/editname', methods=['GET', 'POST'])
@login_required
@role_required('cs')
def edit_user_name(user_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
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
def user_clients(user_id):
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
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

        return render_template('users/user_clients.html', page='Clients', user=user, clients=query, num_pages=num_pages, curr_page=curr_page)


@bp.route('/users/<int:user_id>/players')
@login_required
def user_players(user_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        user = session.query(User).get(user_id)
        players = session.query(CorePlayer).filter(CorePlayer.user_id==user_id).order_by(CorePlayer.player_name).limit(9999)
        return render_template('users/user_players.html', page='Players', user=user, players=players)


@bp.route('/users/<int:user_id>/identities')
@login_required
def user_identities(user_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        user = session.query(User).get(user_id)
        identities = session.query(UserIdentity).filter(UserIdentity.user_id==user_id).order_by(UserIdentity.name).limit(9999)
        return render_template('users/user_identities.html', page='Identities', user=user, identities=identities)
