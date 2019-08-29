from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from adminweb.utils import sqlalchemy_tenant_session
from driftbase.models.db import Machine, MachineEvent, Server


bp = Blueprint('machines', __name__, url_prefix='/machines', template_folder='machines')


def drift_init_extension(app, api, **kwargs):
    app.register_blueprint(bp)


@bp.route('/')
@login_required
def index():
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        query = session.query(Machine)
        if request.args.get('machine_id'):
            query = query.filter(Machine.machine_id==int(request.args.get('machine_id')))
        elif request.args.get('instance_id'):
            query = query.filter(Machine.instance_id.ilike('%{}%'.format(request.args.get('instance_id'))))
        order_by = request.args.get('order_by') or 'machine_id'
        query = query.order_by(getattr(Machine, order_by).desc())
        query = query.limit(100)
        row_count = query.count()
        machines = query
        if row_count == 1:
            return redirect(url_for('machines.machine', machine_id=machines[0].machine_id))
        else:
            return render_template('machines/index.html', machines=machines)


@bp.route('/machines/<int:machine_id>')
@login_required
def machine(machine_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        machine = session.query(Machine).get(machine_id)
    return render_template('machines/machine.html', page='INFO', machine=machine)


@bp.route('/machines/<int:machine_id>/events')
@login_required
def machine_events(machine_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        machine = session.query(Machine).get(machine_id)
        events = session.query(MachineEvent).filter(MachineEvent.machine_id==machine_id).order_by(MachineEvent.event_id.desc()).limit(100)
        return render_template('machines/machine_events.html', page='Events', machine=machine, events=events)


@bp.route('/machines/<int:machine_id>/servers')
@login_required
def machine_servers(machine_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        machine = session.query(Machine).get(machine_id)
        servers = session.query(Server).filter(Server.machine_id==machine_id).order_by(Server.server_id.desc()).limit(100)
        return render_template('machines/machine_servers.html', page='Servers', machine=machine, servers=servers)
