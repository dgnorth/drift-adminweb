# filters.py

from jinja2.utils import Markup
import flask
import json
import copy
import datetime, time
from decimal import Decimal
from dateutil import parser
import types

blueprint = flask.Blueprint('filters', __name__)

def sanitize(d):
    if isinstance(d, dict):
        for k, v in d.iteritems():
            if 'private' in k or 'password' in k or k == 'key' or k == 'client_secret' or k == 'access_token':
                d[k] = "***"
            elif isinstance(v, dict):
                sanitize(v)
            elif isinstance(v, list):
                for vv in v:
                    sanitize(vv)
            else:
                print "{0} : {1}".format(k, v)
    return d

@blueprint.app_template_filter()
def fmt_dict(value):
    value = copy.deepcopy(value)
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except:
            return value
    if not value:
        return ""
    ret = "<table style=\"width:100%%\">"
    value = sanitize(value)
    for k, v in value.iteritems():
        if isinstance(v, dict) or isinstance(v, list):
            v = "<pre>%s</pre>" % json.dumps(v, indent=4)
        ret += "<tr><th class=key>%s</th><td>%s</td></tr>" % (k, v)
    ret += "</table>"
    return Markup(ret)

@blueprint.app_template_filter()
def fmt_dict_inline(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except:
            return value
    if not value:
        return ""

    if isinstance(value, list):
        entries = []
        for entry in value:
            entries.append("{" + _fmt_dict(entry) + "}")
        return "[" + ", ".join(entries) + "]"

    return _fmt_dict(value)

def _fmt_dict(value):
    lst = []
    for k, v in value.iteritems():
        if isinstance(v, dict) or isinstance(v, list):
            v = "<pre>%s</pre>" % json.dumps(v, indent=4)
        lst.append('<span class="inldctkey">%s:</span> <span class="inldctval">%s</span>' % (k, v))
    ret = ", ".join(lst)
    return Markup(ret)

@blueprint.app_template_filter()
def dt(value, format='%Y-%m-%d %H:%M'):
    if isinstance(value, types.StringTypes):
        value = parser.parse(value)
    if not value:
        return "-"
    return value.strftime(format)

@blueprint.app_template_filter()
def dtt(value, format='%Y-%m-%d %H:%M:%S'):
    if not value:
        return "-"
    return value.strftime(format)

@blueprint.app_template_filter()
def desc(value):
    return value.replace("\n", "<br>")

@blueprint.app_template_filter()
def fmt_logevent(value):
    name = value.name
    severity = value.severity
    mapping = {
        "product.edit": ("Edit Product", "products.info", "product_name"),
        "product.create": ("Create Product", "products.info", "product_name"),
        "product.delete": "Delete Product",
        "product.changepicture": ("Change Product Image", "products.info", "product_name"),
        "organization.member.remove": ("Remove Member", "profile.profile", "user_id"),
        "organization.member.left": ("Member Left", "profile.profile", "user_id"),
        "organization.member.add": ("Add Member", "profile.profile", "user_id"),
        "organization.member.edit": ("Edit Member", "profile.profile", "user_id"),
        "organization.changepicture": "Change Image",
    }
    format_info = mapping.get(name, None)
    title = ""
    endpoint = ""
    endpoint_id_name = ""
    if not format_info:
        # apply some heuristics if nothing is found
        title = name.replace(".", " ").title()
    elif isinstance(format_info, tuple):
        title = format_info[0]
        endpoint = format_info[1]
        endpoint_id_name = format_info[2]
    else:
        title = format_info

    link = ""
    if endpoint and value.reference_id:
        kwargs = {endpoint_id_name: value.reference_id}
        url = flask.url_for(endpoint, **kwargs)
        link_name = "link" if not value.reference_text else value.reference_text
        link = ' <a href="{}" title="{}">{}</a>'.format(url, url, link_name)

    ret = ""
    if severity == "warning":
        icon = '<span class="label label-warning"><i class="fa fa-question-circle" title="important"></i></span>'
    elif severity == "alert":
        icon = '<span class="label label-important"><i class="fa fa-exclamation-circle" title="important"></i></span>'
    else:
        icon = '<span class="label"><i class="fa fa-info-circle" title="info"></i></span>'
    ret = '{} {}{}'.format(icon, title, link)
    return Markup(ret)

@blueprint.app_template_filter()
def date_to_millis(d):
    """Converts a datetime object to the number of milliseconds since the unix epoch."""
    return int(time.mktime(d.timetuple())) * 1000

@blueprint.app_template_filter()
def fmt_count(c):
    if c - int(c) != 0:
        c = "%.2f" % c
    c = Decimal(c)
    c = c.quantize(Decimal(c)) if c == c.to_integral() else c.normalize()
    return '{0:,}'.format(c)

@blueprint.app_template_filter()
def fmt_datetime(dt):

    try:
        if not isinstance(dt, datetime.datetime):
            dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f')
        return dt.strftime('%Y/%m/%d %H:%M:%S')
    except Exception as e:
        print "Exception in fmt_datetime for '%s': %s" % (dt, e)
        return dt


@blueprint.app_template_filter()
def fmt_heartbeat(dt):

    try:
        if not isinstance(dt, datetime.datetime):
            dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f')
        cls = "heartbeat_ok"
        icon = "fa-check"
        if dt < datetime.datetime.utcnow()-datetime.timedelta(minutes=5):
            cls = "heartbeat_bad"
            icon = "fa-warning"
        ret = '<div class="%s">%s <i class="fa %s"></i></div>' % (cls, dt.strftime('%Y/%m/%d %H:%M:%S'), icon)
        return ret
    except Exception as e:
        print "Exception in fmt_datetime for '%s': %s" % (dt, e)
        return dt

@blueprint.app_template_filter()
def fmt_duration(diff):
    try:
        secs = diff.total_seconds()
    except:
        return "-"
    minutes, seconds = divmod(secs, 60)
    if minutes > 60:
        hours, minutes = divmod(minutes, 60)
        return "%.0fh %.0fm %.0fs" % (hours, minutes, seconds)
    elif secs > 60:
        return "%.0fm %.0fs" % (minutes, seconds)
    else:
        return "%.0fs" % secs


@blueprint.app_template_filter()
def role(s):
    m = {
        'cs': 'badge-info',
        'dev': 'badge-success',
        'tester': 'badge-info',
        'admin': 'badge-success',
        'roleadmin': 'badge-danger',
        'useradmin': 'badge-warning'
    }
    cls = m.get(s, 'badge-secondary')
    ret = '<span class="badge %s">%s</span>' % (cls, s)
    return Markup(ret)


@blueprint.app_template_filter()
def status(s):
    cls = 'badge-secondary'
    if s == 'active':
        cls = 'badge-success'
    elif s == 'disabled':
        cls = 'badge-warning'
    ret = '<span class="badge %s">%s</span>' % (cls, s)
    return Markup(ret)


@blueprint.app_template_filter()
def client_ip(client, include_country=True):
    try:
        ret = '<a href="{url}">{ip}</a><div class="float-left"><img data-toggle="tooltip" title="{name}" src="{flag}" class="countryflag"></div>'.format(ip=client.ip_address,
                                               name=client.country['country_name'],
                                               flag=client.country['flag'],
                                               url=flask.url_for('clients.index', ip_address=client.ip_address))
        if include_country:
            ret += ' ({name})'.format(name=client.country['country_name'])
    except:
        ret = client.ip_address

    return Markup(ret)


@blueprint.app_template_filter()
def player_url(txt, player_id=None):
    if not player_id:
        player_id = txt
    ret = '<a href="%s">%s</a>' % (flask.url_for('players.player', player_id=player_id), txt)
    return Markup(ret)
