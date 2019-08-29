from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from adminweb.utils import sqlalchemy_tenant_session
from driftbase.models.db import Server, Match


bp = Blueprint('servers', __name__, url_prefix='/servers', template_folder='servers')


def drift_init_extension(app, api, **kwargs):
    app.register_blueprint(bp)


@bp.route('/')
@login_required
def index():
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        query = session.query(Server)
        if request.args.get('server_id'):
            query = query.filter(Server.server_id==int(request.args.get('server_id')))
        elif request.args.get('public_ip'):
            query = query.filter(Server.public_ip.ilike('%{}%'.format(request.args.get('public_ip'))))
        order_by = request.args.get('order_by') or 'server_id'
        query = query.order_by(getattr(Server, order_by).desc())
        query = query.limit(100)
        row_count = query.count()
        servers = query
        if row_count == 1:
            return redirect(url_for('servers.server', server_id=servers[0].server_id))
        else:
            return render_template('servers/index.html', servers=servers)


@bp.route('/servers/<int:server_id>')
@login_required
def server(server_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        server = session.query(Server).get(server_id)
    return render_template('servers/server.html', page='INFO', server=server)


@bp.route('/servers/<int:server_id>/matches')
@login_required
def server_matches(server_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        server = session.query(Server).get(server_id)
        matches = session.query(Match).filter(Match.server_id==server_id).order_by(Match.match_id.desc()).limit(100)
        return render_template('servers/server_matches.html', page='Matches', server=server, matches=matches)
