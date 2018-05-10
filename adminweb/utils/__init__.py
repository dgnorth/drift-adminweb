from contextlib import contextmanager

from flask import g, current_app
from flask_restful import abort
from functools import wraps

from driftconfig.util import get_drift_config
from driftconfig.relib import create_backend, get_store_from_url
from drift.core.resources.postgres import format_connection_string, get_sqlalchemy_session
from drift.core.extensions.tenancy import tenant_from_hostname
from drift.utils import get_tier_name

from adminweb.db.models import LogAction


BASE_SERVICE = "drift-base"

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super(InvalidUsage, self).__init__()
        self.message = message
        if status_code:
            self.status_code = status_code


def log_action(name, severity='info', details=None, ref=None, db=None):
    if db is None:
        db = g.db

    if ref:
        reference_type = ref[0]
        reference_id = int(ref[1])
    log_row = LogAction(user_id=g.user.user_id,
                        name=name,
                        severity=severity,
                        details=details,
                        reference_type=reference_type,
                        reference_id=reference_id,
                        )
    db.add(log_row)
    db.commit()
    return log_row.id


def get_sqlalchemy_tenant_session(
    tenant_name=None, tier_name=None, deployable_name=None
    ):
    tenant_name = tenant_name or tenant_from_hostname
    tier_name = tier_name or get_tier_name()
    deployable_name = deployable_name or current_app.config['name']

    config = get_drift_config(
        tenant_name=tenant_name, tier_name=tier_name, deployable_name=deployable_name)
    conn_string = format_connection_string(config.tenant['postgres'])
    session = get_sqlalchemy_session(conn_string)
    return session


@contextmanager
def sqlalchemy_tenant_session(tenant_name=None, tier_name=None, deployable_name=None):
    session = get_sqlalchemy_tenant_session(
        tenant_name=tenant_name, tier_name=tier_name, deployable_name=deployable_name)

    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()


def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if role not in [r.role for r in g.user.roles]:
                abort(401, message="You need role '%s' to access this function" % role)
            return fn(*args, **kwargs)

        return decorated
    return wrapper
