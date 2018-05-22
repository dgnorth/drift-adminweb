import collections
import logging

from flask import Blueprint, request, jsonify, \
                  flash, g, redirect, url_for, \
                  render_template, make_response, \
                  current_app

from flask_login import login_required

from drift.utils import request_wants_json
from drift.core.extensions.tenancy import tenant_from_hostname
from drift.utils import get_tier_name
from adminweb.utils import sqlalchemy_tenant_session, role_required, log_action
from adminweb.db.models import PlayerInfo
from adminweb.db.models import User as AdminUser
from adminweb.utils.country import get_cached_country
from driftbase.db.models import Client, User, UserRole, CorePlayer, PlayerEvent
from driftbase.players import log_event

log = logging.getLogger(__name__)
bp = Blueprint('players', __name__, url_prefix='/players', template_folder="players")

MAX_MISSIONS = 3

@bp.route('/')
@login_required
def index():
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        query = session.query(CorePlayer)
        if request.args.get('player_id'):
            query = query.filter(CorePlayer.player_id==int(request.args.get('player_id')))
        elif request.args.get('player_name'):
            query = query.filter(CorePlayer.player_name.ilike('%{}%'.format(request.args.get('player_name'))))
        order_by = request.args.get('order_by') or 'logon_date'
        query = query.order_by(getattr(CorePlayer, order_by).desc())
        row_count = query.count()
        query = query.limit(page_size)
        query = query.offset(offset)
        players = query
        num_pages = int(row_count/page_size)+1

        if row_count == 1:
            return redirect(url_for('players.player', player_id=players[0].player_id))
        else:
            return render_template('players/index.html', players=players,
                        num_pages=num_pages,
                        curr_page=curr_page,
                        order_by=order_by)


@bp.route('/players/<int:player_id>')
@login_required
def player(player_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        player = session.query(CorePlayer).get(player_id)
        user = session.query(User).get(player.user_id)
        roles = user.roles

    info = g.db.query(PlayerInfo, AdminUser)\
               .filter(PlayerInfo.player_id==player_id, AdminUser.user_id==PlayerInfo.admin_user_id)\
               .first()
    return render_template('players/player.html',
                           player=player,
                           user=user,
                           roles=roles,
                           info=info)


@bp.route('/players/<int:player_id>/editnote', methods=['POST', 'GET'])
@login_required
def edit_player_note(player_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        player = session.query(CorePlayer).get(player_id)
    info = g.db.query(PlayerInfo)\
               .filter(PlayerInfo.player_id==player_id)\
               .first()

    if request.method == 'POST':
        if request.form.get('delete'):
            if info:
                g.db.delete(info)
            log_action('player.note_deleted', ref=('player', player_id))
            flash("Player note deleted")
        else:
            if info:
                log_action('player.note_changed', ref=('player', player_id))
                flash("Player note changed")
            else:
                log_action('player.note_added', ref=('player', player_id))
                info = PlayerInfo(player_id=player_id)
                g.db.add(info)
                flash("Player note added")
            info.notes = request.form['notes']
            info.admin_user_id = g.user.user_id
        g.db.commit()
        return redirect(url_for('players.player', player_id=player_id))
    else:
        return render_template('players/editnote.html',
                               player=player,
                               info=info)


@bp.route('/players/<int:player_id>/events')
@login_required
def player_events(player_id):
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        player = session.query(CorePlayer).get(player_id)
        query = session.query(PlayerEvent) \
                       .filter(PlayerEvent.player_id==player_id)
        if request.args.get('event_type_name'):
            query = query.filter(PlayerEvent.event_type_name.ilike('%{}%'.format(request.args.get('event_type_name'))))

        query = query.order_by(PlayerEvent.event_id.desc())
        row_count = query.count()
        query = query.limit(page_size)
        query = query.offset(offset)
        num_pages = int(row_count/page_size)+1

        return render_template('players/player_events.html', player=player, events=query,
                        num_pages=num_pages,
                        curr_page=curr_page)


@bp.route('/players/<int:player_id>/editname', methods=['GET', 'POST'])
@login_required
@role_required('cs')
def edit_player_name(player_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        player = session.query(CorePlayer).get(player_id)
        if request.method == 'POST':
            old_player_name = player.player_name
            player.player_name = request.form['val']
            log_event(player_id,
                      'event.admin.change_player_name',
                      details={'admin': g.user.username, 'old': old_player_name, 'new': player.player_name},
                      db_session=session)
            log_action('player.change_player_name', ref=('player', player_id))
            flash("Player name has been changed from %s to %s" % (old_player_name, player.player_name))

            return redirect(url_for('players.player', player_id=player_id))

        else:
            return render_template('players/editfield.html', player=player, which='player name', val=player.player_name)


@bp.route('/players/<int:player_id>/clients')
@login_required
def clients(player_id):
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size

    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        player = session.query(CorePlayer).get(player_id)
        query = session.query(Client).filter(Client.player_id==player_id)
        query = query.order_by(Client.client_id.desc())
        row_count = query.count()
        query = query.limit(page_size)
        query = query.offset(offset)
        rows = query.all()
        num_pages = int(row_count/page_size)+1
        for client in rows:
            client.country = get_cached_country(client.ip_address)

        return render_template('players/player_clients.html', player=player, clients=query, num_pages=num_pages, curr_page=curr_page)


@bp.route('/players/<int:player_id>/editroles', methods=['GET', 'POST'])
@role_required('cs')
def edit_roles(player_id):
    all_roles = [r[0] for r in current_app.config.get('player_roles')]
    with sqlalchemy_tenant_session(deployable_name='drift-base') as drift_session:
        player = drift_session.query(CorePlayer).get(player_id)
        user_id = player.user_id
        user = drift_session.query(User).get(player.user_id)

        user_roles = set([r.role for r in user.roles])
        new_roles = set()
        if request.method == 'POST':
            for role in all_roles:
                if request.form.get(role):
                    new_roles.add(role)

            roles_to_remove = user_roles - new_roles
            roles_to_add = new_roles - user_roles
            for role in roles_to_remove:
                for r in user.roles:
                    if r.role == role:
                        drift_session.delete(r)
            for role in roles_to_add:
                r = UserRole(user_id=user_id, role=role)
                drift_session.add(r)
                drift_session.commit()
            flash('User roles has been changed')
            if roles_to_add or roles_to_remove:
                details = {}
                if roles_to_add:
                    details["added_roles"] = ", ".join(roles_to_add)
                if roles_to_remove:
                    details["removed_roles"] = ", ".join(roles_to_remove)
                log_action('player.editroles', ref=('player', player_id))
                log_event(player_id,
                          'event.admin.changeroles',
                          details=details,
                          db_session=drift_session)
            return redirect(url_for('players.player', player_id=player_id))
    return render_template('players/editroles.html',
                           player=player,
                           user=user,
                           player_roles=current_app.config.get('player_roles'),
                           roles=user_roles)
