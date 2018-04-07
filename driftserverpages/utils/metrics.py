from contextlib import contextmanager

from flask import current_app

from driftconfig.util import get_default_drift_config
from drift.utils import get_tier_name
from drift.core.extensions.tenancy import tenant_from_hostname
from drift.core.resources.postgres import format_connection_string
from drift.orm import get_sqlalchemy_session


def get_metrics_session():
    tenant = tenant_from_hostname
    metrics_server = current_app.config['METRICS_SERVER']
    if not metrics_server.get('server'):
        ts = get_default_drift_config()
        tenant_deployable_config = ts.get_table('tenants').get({'tier_name': get_tier_name().upper(), 'tenant_name': tenant, 'deployable_name': 'drift-base'})
        metrics_server['server'] = tenant_deployable_config["postgres"]["server"]
    conn_string = format_connection_string(metrics_server)
    sess = get_sqlalchemy_session(conn_string)
    return sess


@contextmanager
def metrics_agent():
    agent = MetricsAgent()
    try:
        yield agent
        agent.session.commit()
    except BaseException:
        agent.session.rollback()
        raise
    finally:
        agent.session.close()


def collect_counters(session):
    sql = "SELECT counter_id, name, period, description FROM counters"
    rows = session.execute(sql)
    ret = {}
    for r in rows:
        ret[(r.name, r.period)] = r
        ret[r.counter_id] = r

    return ret


class MetricsAgent(object):
    def __init__(self):
        self.session = get_metrics_session()
        self.counters = collect_counters(self.session)

    def get_counter_data(self, key, num_days, title=None):
        ret = {'title': title, 'rows': []}
        if key not in self.counters:
            return ret

        counter = self.counters[key]
        counter_id = counter.counter_id
        title = title or counter.description or counter.name
        ret['title'] = title
        sql = """SELECT date_time, value FROM counters_view
                  WHERE counter_id = {counter_id} AND date_time::date >= current_date - interval '{num_days} days'
                  ORDER BY date_time ASC""".format(counter_id=counter_id, num_days=num_days)
        print sql
        rows = self.session.execute(sql)

        for r in rows:
            p = ((r.date_time.year, r.date_time.month-1, r.date_time.day, r.date_time.hour, r.date_time.minute), int(r.value))
            ret['rows'].append(p)

        # skip the most recent row since it is still filling up
        if ret['rows']:
            del ret['rows'][-1]

        return ret

    def get_counter_glance(self, key):
        rows = self.get_counter_data(key, 2)['rows']
        value = -1
        diff = None
        if len(rows) == 2:
            prev_value = rows[0][-1]
            value = rows[1][-1]
            diff = int(1000*((value / float(prev_value))-1.0))/10.0
        return value, diff
