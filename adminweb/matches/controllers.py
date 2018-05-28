from flask import Blueprint, request, redirect, url_for, render_template
from flask_login import login_required

from adminweb.utils import sqlalchemy_tenant_session
from driftbase.db.models import Match, MatchPlayer, MatchTeam, CorePlayer, MatchEvent, MatchQueuePlayer


bp = Blueprint('matches', __name__, url_prefix='/matches', template_folder="matches")


@bp.route('/')
@login_required
def index():
    page_size = 50
    curr_page = int(request.args.get("page") or 1)
    offset = (curr_page-1) * page_size
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        query = session.query(Match)
        if request.args.get('match_id'):
            query = query.filter(Match.match_id==int(request.args.get('match_id')))
        elif request.args.get('public_ip'):
            query = query.filter(Match.public_ip.ilike('%{}%'.format(request.args.get('public_ip'))))
        order_by = request.args.get('order_by') or 'match_id'
        query = query.order_by(getattr(Match, order_by).desc())
        query = query.limit(100)
        row_count = query.count()
        query = query.limit(page_size)
        query = query.offset(offset)
        num_pages = int(row_count/page_size)+1
        matches = query
        if row_count == 1:
            return redirect(url_for('matches.match', match_id=matches[0].match_id))
        else:
            return render_template('matches/index.html', matches=matches,
                                   num_pages=num_pages,
                                   curr_page=curr_page)


@bp.route('/matches/<int:match_id>')
@login_required
def match(match_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        match = session.query(Match).get(match_id)
    return render_template('matches/match.html', match=match, page_name='Home')


@bp.route('/matches/<int:match_id>/players')
@login_required
def match_players(match_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        match = session.query(Match).get(match_id)
        players = session.query(MatchPlayer, CorePlayer).filter(MatchPlayer.match_id==match_id, CorePlayer.player_id==MatchPlayer.player_id).order_by(MatchPlayer.team_id).limit(9999)
        return render_template('matches/match_players.html',
                               match=match, players=players, page_name='Players')


@bp.route('/matches/<int:match_id>/teams')
@login_required
def match_teams(match_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        match = session.query(Match).get(match_id)
        teams = session.query(MatchTeam).filter(MatchTeam.match_id==match_id).order_by(MatchTeam.team_id.desc()).limit(9999)
        return render_template('matches/match_teams.html',
                               match=match, teams=teams, page_name='Teams')


@bp.route('/matches/<int:match_id>/events')
@login_required
def match_events(match_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        match = session.query(Match).get(match_id)
        events = session.query(MatchEvent).filter(MatchEvent.match_id==match_id).order_by(MatchEvent.event_id.desc()).limit(100)
        return render_template('matches/match_events.html',
                               match=match, events=events, page_name='Events')


@bp.route('/matches/<int:match_id>/queueplayers')
@login_required
def match_queueplayers(match_id):
    with sqlalchemy_tenant_session(deployable_name='drift-base') as session:
        match = session.query(Match).get(match_id)
        players = session.query(MatchQueuePlayer).filter(MatchQueuePlayer.match_id==match_id).order_by(MatchQueuePlayer.id.desc()).limit(100)
        return render_template('matches/match_queueplayers.html',
                               match=match, players=players, page_name='Queue')
