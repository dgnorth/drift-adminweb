from flask import g
from flask_restful import abort
from functools import wraps
from adminweb.db.models import LogAction
from contextlib import contextmanager
from drift.orm import get_sqlalchemy_session
from driftconfig.util import get_domains, get_default_drift_config
from driftconfig.relib import create_backend, get_store_from_url
from drift.core.resources.postgres import format_connection_string

import re

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



@contextmanager
def sqlalchemy_tenant_session(tenant, tier, deployable):
    ts = get_default_drift_config()
    tenant_deployable_config = ts.get_table('tenants').get({'tier_name': tier.upper(), 'tenant_name': tenant, 'deployable_name': deployable})
    conn_string = format_connection_string(tenant_deployable_config["postgres"])
    session = get_sqlalchemy_session(conn_string)
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
